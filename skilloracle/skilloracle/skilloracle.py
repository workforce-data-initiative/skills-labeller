import socket
from contextlib import closing
import psutil

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0

VW_HOST='127.0.0.1'
VW_PORT=7000
#todo: break down into PEP compliant long string
VW_CMD ="--save_resume --port {port} --active --predictions /dev/null --daemon --audit -b{bits} --skips 2 --ngram 2 --loss_function logistic".format(port=VW_PORT, bits=25)

class SkillOracle(object):
    def __init__(self,
                 host=VW_HOST,
                 port=VW_PORT,
                 cmd=VW_CMD):
        self.cmd = cmd
        self.host = host
        self.port = port
        self.oracle = None

        command = None
        if not check_socket(host=host, port=port):
            command = self.cmd
        # Stand up/Connect to an instance of vowpal wabbit
        self.oracle = wabbit_wappa.DaemonVWProcess(command=self.cmd,
                                                   port=self.port,
                                                   ip=self.host)

    def kill_oracle(self, name='vw'):
        ret = False
        for proc in psutil.process_iter():
            if proc.name() == name:
                proc.kill()
                # continue, could be more...
                ret = True

        return ret
