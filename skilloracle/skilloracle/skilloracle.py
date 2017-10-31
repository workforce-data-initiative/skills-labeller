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

    def sendrecv(self, host, port, content):
        ret = None

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.sendall(content.encode())
        s.shutdown(socket.SHUT_WR)
        recv_buffer = []
        while True:
            data = s.recv(4096)
            if not data:
                break
            recv_buffer.append(data)
        s.close()

        if 0 != len(recv_buffer):
            ret = recv_buffer

        return ret

    def check_socket(self, host=None, port=None):
        ret = False
        host = host
        if host == None:
            host = '127.0.0.1' # need some kind of a host to check

        try:
            self.sendrecv(host, port, "1")
        except ConnectionRefused:
            pass
        else:
            ret = True

        return ret

    def kill(self, name='vw'):
        ret = subprocess(shlex("killall vw"))
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
