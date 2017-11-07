import time
import subprocess
import shlex
from wabbit_wappa.active_learner import DaemonVWProcess
from wabbit_wappa import escape_vw_string
import redis


VW_HOST='127.0.0.1'
VW_PORT=7000
VW_CMD="vw"
#todo: break down into PEP compliant long string
VW_ARGS ="--save_resume --port {port} --active --predictions /dev/null --daemon --audit -b{bits} --skips 2 --ngram 2 --loss_function logistic".format(port=VW_PORT, bits=25)

class SkillOracle(object):
    def __init__(self,
                 host=None,
                 port=None,
                 cmd=" ".join([VW_CMD, VW_ARGS])):
        self.SKILL_CANDIDATES = "candidates" # backing for ordered importances
        self.cmd = cmd
        self.host = host
        self.port = port
        self.oracle = None

        command = None
        if not self.check_socket(host=self.host, port=self.port):
            command = self.cmd
        # Stand up/Connect to an instance of vowpal wabbit
        self.oracle = DaemonVWProcess(command=self.cmd,
                                      port=self.port,
                                      ip=self.host)

        self.redis_db = redis.StrictRedis()# defaults to 127.0.0.1:6379 db=0

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
            nc = subprocess.check_output(('netcat', host, str(port)),
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
            host = '127.0.0.1' # need some kind of a host to check

        self.sendrecv(host, port, "1")
        time.sleep(0.5) # wait for a replay
        ret = True

        return ret

    def kill(self, name='vw'):
        ret = subprocess.call(shlex.split('killall vw'))
        return ret == 0

    def PUT(self, label, name, context):
        response = None

        # todo: I think this function expects a string array
        name = escape_vw_string(name)
        context = escape_vw_string(context)

        if label:
            label = escape_vw_string(label)
            labelled_example = "{label} |{context_namespace} {context} \
                                        |{name_namespace} {name}".\
                    format(label=label,
                           context_namespace="context",
                           context=context,
                           name_namespace="name",
                           name=name)
        else:
            labelled_example = "|{context_namespace} {context} \
                                |{name_namespace} {name}".\
                    format(context_namespace="context",
                           context=context,
                           name_namespace="name",
                           name=name)

            self.oracle.sendline(labelled_example)
            response = self.oracle._recvline()

        return response

    def GET(self):
        response = self.__get_redis()
        return response

    def __setup_redis(self):
        raise NotImplementedError

    def __get_redis(self):
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
        response = pipe.execute()

        return response

    def fetch_push_more(self, fetcher=None):
        # can subclass to provide your own call/code
        self.__fetch_push_more(fetcher=fetcher)

    def __fetch_push_more(self, fetcher=None):
        """
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

            self.redis_db.zadd(self.SKILL_CANDIDATES,
                               response.importance,
                               name)
