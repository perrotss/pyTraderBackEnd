import datetime
import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
f = open(f"temp/{datetime.datetime.now().strftime('mylogfile_%H_%M_%d_%m_%Y.txt')}", 'w')
backup = sys.stdout
sys.stdout = Tee(sys.stdout, f)
