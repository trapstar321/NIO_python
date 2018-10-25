import datetime

class Logger:
    def __init__(self, debug):
        self.debug = debug

    def log(self, msg):
        if self.debug:
            print("{0}: {1}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], msg))
        
    