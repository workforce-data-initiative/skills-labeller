import subprocess
import time
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
            nc = subprocess.check_output(('nc', host, str(port)),
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

        try:
            self.sendrecv(host, port, "1")
            time.sleep(0.5) # wait for a replay
        except ConnectionRefusedError:
            pass
        except ConnectionResetError:
            pass # either exception indicates no vw exists
        else:
            ret = True

        return ret

    def kill(self, name='vw'):
        ret = subprocess.call(shlex.split('killall vw'))
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

        self.oracle.sendline(labelled_example)
