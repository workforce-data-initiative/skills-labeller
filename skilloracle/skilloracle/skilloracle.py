import socket
from contextlib import closing
import psutil
from wabbit_wappa.active_learner import DaemonVWProcess


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
        host = host
        if host == None:
            host = '127.0.0.1' # need some kind of a host to check
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            return sock.connect_ex((host, port)) == 0

    def kill(self, name='vw'):
        ret = False
        for proc in psutil.process_iter():
            if proc.name() == name:
                proc.kill()
                # continue, could be more...
                ret = True

        return ret

    def PUT(self, label, name, context):
        # Given a labelled example, construct a vowpal_wabbit
        # suitable input string for .teach'ing
        # ideally I would use the Namespace, and other, functions but
        # I believe it's faster to do it directly

        labelled_example = "{label} |{context_namespace} {context} |{name_namespace} {name}".\
                format(label=label,
                       context_namespace="context",
                       context=context,
                       name_namespace="name",
                       name=name)

        self.oracle.teach(labelled_example)


