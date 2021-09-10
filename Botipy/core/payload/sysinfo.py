try:
    import platform
except ImportError as err:
    print(err)

class Sysinfo(object):

    def __init__(self):
        self.hostname  = platform.node()
        self.os        = platform.platform()
        self.processor = platform.processor()

    def get_host_info(self):
        return 'Hostname: {hostname}\nOS: {os}\nProcessor: {processor}'.format(hostname=self.hostname,
                                                                               os=self.os,
                                                                               processor=self.processor)
