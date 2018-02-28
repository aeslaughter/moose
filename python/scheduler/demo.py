#!/usr/bin/env python
from Scheduler import Scheduler
from Worker import Worker
import time

if __name__ == '__main__':

    class MyWorker(Worker):
        COUNT = 0
        def __init__(self):
            MyWorker.COUNT += 1
            self._id = MyWorker.COUNT

        def run(self):
            time.sleep(1)
            with self.lock:
                print 'MyWorker', self._id

    workers = [MyWorker() for i in range(10)]

    s = Scheduler(num_threads=3)
    for worker in workers:
        s.schedule(worker)
    s.waitFinish()
