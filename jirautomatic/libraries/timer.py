import time

class Timer:
    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(elapsed_time, 60)
        print "Elapsed Time: %02dm %02ds" % (minutes, seconds)