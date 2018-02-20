import time
import datetime
import subprocess
import shlex
import json
from wabbit_wappa.active_learner import DaemonVWProcess
from wabbit_wappa import escape_vw_string
import redis
import re


VW_HOST='127.0.0.1'
VW_PORT=7000
VW_CMD="vw"
#todo: break down into PEP compliant long string
VW_ARGS ="--save_resume --port {port} --active --quiet --daemon -b{bits} --skips 2 --ngram 2 --loss_function logistic".format(port=VW_PORT, bits=25)

class SkillOracle(object):
    def __init__(self,
                 host=None,
                 port=None,
                 cmd=" ".join([VW_CMD, VW_ARGS])):
        self.SKILL_CANDIDATES = "candidates" # backing for ordered importances
        self.TIMESTAMP = "timestamp" # string of last timestamp value
        self.REDIS = "redis" # Host name Redis container in service docker network
        self.cmd = cmd
        self.host = host # should we have a default host or force user to provide one?
        self.port = port
        self.oracle = None
        self.escape_dict = {':': r'\;',
                            '|': r'\\',
                            ' ': r' '
                            }# note: space has no change
        self.validation_regex = re.compile(r' |:|\|')

        command = None
        if not self.check_socket(host=self.host, port=self.port):
            command = self.cmd
        # Stand up/Connect to an instance of vowpal wabbit
        self.oracle = DaemonVWProcess(command=self.cmd,
                                      port=self.port,
                                      ip=self.host)

        self.redis_db = redis.StrictRedis(host=self.REDIS)# defaults to redis:6379

    def escape_vw_character(self, special_character_re_match):
      special_character = special_character_re_match.group()
      return self.escape_dict[special_character]

    def escape_vw_string(self, s):
      """
      Taken from wabbit wappa, does not replace spaces
      """
      escaped_s = self.validation_regex.sub(self.escape_vw_character, s)
      return escaped_s

    def sendrecv(self, host, port, content):
        """
        We avoid a standard sockets based check because
        there seems to be some interation between sockets, unittest
        where .close doesn't really close and .connect doesn't through
        see: https://github.com/requests/requests/issues/1882

        I'm probably overlooking something simple but we favor the
        echo, netcat strategy below for now. Note that w/o shell,
        netcat also hangs like the socket approach. This
        approach requires less resource management and debugging.
        """
        ret = None
        echo = subprocess.Popen(('echo', content), stdout=subprocess.PIPE)
        try:
            # '-q 1' causes netcat to quit after EOF or 1 second
            cmd = " ".join(('netcat', '-q 1', host, str(port)))
            nc = subprocess.check_output(cmd,
                                         stdin=echo.stdout,
                                         shell=True,
                                         timeout=10)
        except subprocess.CalledProcessError:
            ret = False # nothing listening on the port
        else:
            ret = True

        return ret

    def check_socket(self, host=None, port=None):
        ret = False
        host = host
        if host == None:
            host = self.host # need some kind of a host to check

        ret = self.sendrecv(host, port, "1")

        return ret

    def kill(self, name='vw'):
        ret = subprocess.call(shlex.split('killall vw'))
        return ret == 0

    def PUT(self, label, name, context):
        """
        Note this function could be made more elegant I suppose,
        although I have tried to keep it DRY
        """
        response = None
        send_to_candidate_store = False

        if label:
            label = self.escape_vw_string(label) # can protect with contraint on API
        else:
            label = "" # no label, expect a prediction, etc, back
            send_to_candidate_store = True

        name = self.escape_vw_string(name) # can protect w contrain on API
        context = self.escape_vw_string(context)

        labelled_example = "{label} |{context_namespace} {context} \
                                    |{name_namespace} {name}".\
                format(label=label,
                       context_namespace="context",
                       context=context,
                       name_namespace="name",
                       name=name)

        self.oracle.sendline(labelled_example)
        response = self.oracle._recvline()

        if response:
            result = response.split()
            importance = 0

            if len(result) == 2:
                importance = result[1].decode()

            response = {'importance': importance,
                        'prediction': result[0].decode()}

        if send_to_candidate_store and response:
            # first add candidate...
            importance = float(response['importance'])

            self.redis_db.zadd(self.SKILL_CANDIDATES,
                               importance,
                               json.dumps({"name":name,
                                           "context":context}))# TODO: replace name with json obj container name, context

            # ... then we get the candidate store size
            # directly from redis to return the user as part
            # of the API contract
            pipe = self.redis_db.pipeline()
            pipe.zcard(self.SKILL_CANDIDATES) # can probably call directly?
            size = pipe.execute()

            response['number of candidates'] = size[0]

        return response

    def GET(self):
        # note: __get_redis() shoudl be cleaned up
        # just return importance, key/skill candidate
        response = self._get_redis()
        return response

    def __setup_redis(self):
        raise NotImplementedError

    def _get_redis(self):
        """
        _get_redis is an important utility function that pops off the candidate
        of highest importance (e.g., in active learning, the example we would most
        like labelled).

        Typically this would be done in Redis with a special z set (ordered set)
        reverse pop function, called ZREVPOP. However this function is not implemented
        in python's redis library, mainly because it can be acheived with
        a couple of other z set functions: zrange and zremrangebyrank

        The code below sets up a pipeline, an ordered set of redis commands that are
        executely atomically as a group. The commands used, referring to the google
        group link for more discussion, are:

        zrange - get the item with the highest score, as inidcated by -1
        zremrangebyrank - remove the item with highest score, as indicated by -1

        Finally, we return the size of the ordered z set, to help with fetching more
        examples when neccessary.

        note: the fact that we're popping the item of highest importance assumes that
        the importances are unique, that is, you can't have importances of 1.0 and 1.0
        across two examples. If this does not hold then what will happen is that all
        items of the same importance will be popped.

        It is possible at the start of the skill oracle, since most everything is unknown,
        that multiple items are popped off. However, as active learning continues
        the chance that any two items share the a same importance should become very unlikely.

        Since the main purpose of the skilloracle is to faciliate large scale skill labelling,
        and not accuracy and other metrics, it seems prudent to tolerate this uncertainity
        instead of creating custom lua scripts or otherwise working with Redis more.

        see: https://github.com/antirez/redis/issues/180 for workarounds if this is an
        issue in the steady state of the skill oracle

        note2: given the first note, a simpler (but hacky) fix may be to randomly perturb the
        lower bits (least significant) of the returned importance, e.g. importance + np.random.uniform(1e-4, 1e-6)
        to force probablistic uniqueness w/o messing up the active learning too much (I assume)
        """
        # see: https://groups.google.com/forum/#!topic/redis-db/ur9U8o-Sko0
        response = None
        pipe = self.redis_db.pipeline()# runs w/in multi/exec, atomic, on Redis

        pipe.zrange(self.SKILL_CANDIDATES,
                    -1,
                    -1,
                    withscores=True)
        pipe.zremrangebyrank(self.SKILL_CANDIDATES,
                             -1,
                             -1)
        pipe.zcard(self.SKILL_CANDIDATES)
        candidate_response, _, size = pipe.execute()
        candidate_response = candidate_response[0] # flatten the redis zrange() response

        return {'response': candidate_response[0].decode(),
                'importance': candidate_response[1],
                'number of candidates': size}

    def fetch_push_more(self, fetcher=None):
        """
        WIP: in the process of removing from this service, use PUT instead
        """
        raise NotImplementedError

        # can subclass to provide your own call/code
        self.__fetch_push_more(fetcher=fetcher)

    def _fetch_push_more(self, fetcher=None):
        """
        WIP: Need to also push the context so that the users can see on
        GET()

        Fetches more data using the provided `fetcher` (typically a candidtate db
        connection), passes through skill oracle for importances, pushes to the
        candidate store
        """

        # note: there is a way to batch up canditates and send in bulk
        # but that would take more effort to implement, may not
        # be needed?
        for candidate in fetcher:
            label = None
            name = candidate['name']
            context = candidate['context']

            response = self.PUT(label, name, context)

            prediction = response['prediction']
            importance = float(response['importance'])

            self.redis_db.zadd(self.SKILL_CANDIDATES,
                               importance,
                               name)

    def _push_once(self, size, threshold, fetcher=None, period=60):
        """
        Note: Typically not used, included as a convienence function
        to implementers.

        Utlity function to push new candidates for GET to return
        where pushing happens once per period seconds (default 1 minute)

        This is done to control the feedback loop between
        multiple GET and _fetch_push_more() when the candidate store
        is low and many _fetch_push_more calls are triggered when
        just one successful call would replenish the candidate store.

        The timestamp is assumed to be in epoch time, e.g. time.gmtime()

        note: there are some system assumptions embedded inthis function:
            * that we can push all the candidate skills in the period time
            * generally, in a given period, that the GET rate is a lot less
            than the fetch rate (if you think of this like a queue, that we
            can always fill it back up in time)
        """

        if size < threshold:# push more candidates
            timestamp = self.redis_db.get(self.TIMESTAMP)
            if not timestamp: # is nil
                timestamp = -1
            else:
                timestamp = float(timestamp) # should be time obj?

            if time.time() - timestamp > period:
                # prevent other calls from entering until period has elapsed
                self.redis_db.set(self.TIMESTAMP, str(time.time()))
                self._fetch_push_more(fetcher=fetcher)

