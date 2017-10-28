import subprocess
import shlex
import socket
from contextlib import closing
import psutil
from wabbit_wappa.active_learner import DaemonVWProcess
from wabbit_wappa import escape_vw_string


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

    def check_socket(self, host=None, port=None):
        """
        todo: fix this function, i assumed it worked and it doesn't

        echo'ing to vw doesn't seem to consistently work. might be better
        to look at some kind of process list or echo a "1" or something
        """
        host = host
        if host == None:
            host = '127.0.0.1' # need some kind of a host to check
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            return sock.connect_ex((host, port)) == 0

    def kill(self, name='vw'):
        ret = subprocess(shlex("killall vw"))
        #for proc in psutil.process_iter():
        #    if proc.name() == name:
        #        proc.kill()
        #        proc.wait() # let it clean up...
        #        # continue, could be more...
        #        ret = True
        return ret == 0

    def PUT(self, label, name, context):
        label = escape_vw_string(label)
        name = escape_vw_string(name)
        context = escape_vw_string(context)

        labelled_example = "{label} |{context_namespace} {context} \
                                    |{name_namespace} {name}".\
                format(label=label,
                       context_namespace="context",
                       context=context,
                       name_namespace="name",
                       name=name)

        # note this is a raw send, need esacping for real use
        self.oracle.sendline(labelled_example)
