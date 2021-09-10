try:
    import random, socket, string, sys, threading
except ImportError as err:
    print(err)

class Client(threading.Thread):

    def __init__(self, ip, port, socket):
        threading.Thread.__init__(self)
        self.ip      = ip
        self.port    = port
        self.socket  = socket
        self.uid     = self.random_uid()
        self.running = threading.Event()
	
    def run(self):
        self.running.set()
        while self.running.is_set():
            try:
                raw_cmd = self.socket.recv(4096)
                if len(raw_cmd):
                    output = '{msg}'.format(msg=raw_cmd.decode())
                    print(output)
            except socket.error:
                self.running.clear()
                self.socket.close()
        sys.exit()

    def random_uid(self):
        return ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(24)])
