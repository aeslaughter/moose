import os
import traceback
import multiprocessing
import time
from multiprocessing.pool import ThreadPool
import threading # for thread locking and thread timers

from Worker import Worker

class Scheduler(object):
    """
    A simple threading scheduler.

    Call Scheduler.schedule(workers), where 'workers' are an iterable set of Worker objects.

    When you have scheduled everything you wish to run, call Scheduler.waitFinish()
    which will return, once until all scheduled jobs have completed.

    Inputs:
        num_threads[int]: The number of threads to run with, if not provide the number of
                          available CPUs are used.
        average_load[int]:

    """

    def __init__(self, num_threads=multiprocessing.cpu_count(), average_load=64):
        # Hard limit machine usage
        self.average_load = average_load

        # Initialize run_pool based on available slots
        self.run_pool = ThreadPool(processes=num_threads)

        # Slot lock when processing resource allocations and modifying slots_in_use
        self.slot_lock = threading.Lock()

        # Current slots in use
        self.slots_in_use = 0

        # Number of available slots
        self.available_slots = num_threads

        # Sets of threading objects created by jobs entering and exiting the queue. When scheduler.waitFinish()
        # is called, and the thread pool is empty, the pool closes, and the call to waitFinish() returns.
        self.__thread_pool_lock = threading.Lock()
        self.__runner_pool_jobs = set([])

        # Max time a job is allowed to run in a thread pool
        # Set to something reasonable, or False to allow infinite
        self.__max_time = False

        # Allow threads the ability to set a global error state
        self.__error_state = False

    def schedule(self, worker):
        """
        Do stuff with incoming objects and submit them to the
        thread pool to perform work.
        """
        # If we are not to schedule any more jobs for some reason, return now
        if self.__error_state:
            return

        if isinstance(worker, Worker):
            worker.lock = self.__thread_pool_lock

        #for worker in workers:
        #    worker.lock = self.__thread_pool_lock
        self._queueJobs((worker, 'hold'))

    def waitFinish(self):
        """
        Inform the Scheduler there are no further jobs to schedule.
        Return once all jobs have completed.
        """
        try:
            # wait until there is an error, or if all the queus are empty
            #with self.__thread_pool_lock:
            #    waiting_on_runner_pool = sum(1 for x in self.__runner_pool_jobs if not x.ready())

            waiting_on_runner_pool = True
            while waiting_on_runner_pool:

                if self.__error_state:
                    break

                with self.__thread_pool_lock:
                    waiting_on_runner_pool = sum(1 for x in self.__runner_pool_jobs if not x.ready())

                time.sleep(0.1)

            if not self.__error_state:
                self.run_pool.close()
                self.run_pool.join()

        except KeyboardInterrupt:
            # Do ctrl-c stuff
            pass

    def _queueJobs(self, job):
        """
        submit work to a thread pool
        """
        (a_job, state) = job
        with self.__thread_pool_lock:
            if state == 'hold':
                job = (a_job, 'queued')
                self.__runner_pool_jobs.add(self.run_pool.apply_async(self._runJob, (job,)))

    def _getLoad(self):
        """ Method to return current load average """
        loadAverage = 0.0
        try:
            loadAverage = os.getloadavg()[0]
        except AttributeError:
            pass      # getloadavg() not available in this implementation of os
        return loadAverage

    def _satisfyLoad(self):
        """ Method for controlling load average """
        while self.slots_in_use > 1 and self._getLoad() >= self.average_load:
            time.sleep(1.0)

    def _reserveSlots(self):
        """
        Method which allocates resources to perform the job. Returns bool if job
        should be allowed to run based on available resources.
        """
        self._satisfyLoad()
        with self.slot_lock:
            can_run = False
            if self.slots_in_use + 1 <= self.available_slots:
                can_run = True

            if can_run:
                self.slots_in_use += 1
        return can_run

    def _handleTimeoutJob(self, job):
        """ Handle jobs that have timed out """
        # Do stuff if the job has surpassed a max time
        pass

    def _runJob(self, job):
        """ Method the run_pool calls when an available thread becomes ready """
        if self.__error_state:
            return

        (a_job, state) = job
        try:
            # see if we have enough slots to start this job
            if self._reserveSlots():
                # Create timeout timer
                if self.__max_time:
                    timeout_timer = threading.Timer(float(), self._handleTimeoutJob, (job,))
                    timeout_timer.start()

                a_job()

                if self.__max_time:
                    timeout_timer.cancel()

                # a_job is now finished
                job = (a_job, 'finished')

                # Recover slots
                with self.slot_lock:
                    self.slots_in_use = max(0, self.slots_in_use - 1)

            # Not enough slots to run the job
            else:
                # set job on hold, so it will re-enter the queue
                # sleep a little bit so as not to saturate the main thread
                job = (a_job, 'hold')
                time.sleep(.1)

            # Job is done (or needs to re-enter the queue)
            self._queueJobs(job)

        except Exception as e:
            print('runWorker Exception: %s' % (traceback.format_exc()))

        except KeyboardInterrupt:
            # Do ctrl-c stuff
            pass
