import logging
import multiprocessing

import mooseutils

import MooseDocs

class MooseDocsFormatter(logging.Formatter):
    """
    A formatter that is aware of the class hierarchy of the MooseDocs library.
    Call the init_logging function to initialize the use of this custom formatter.
    """
    COLOR = dict(DEBUG='CYAN',
                 INFO='RESET',
                 WARNING='YELLOW',
                 ERROR='RED',
                 CRITICAL='MAGENTA')

    COUNTS = dict(CRITICAL=multiprocessing.Value('I', 0, lock=True),
                  ERROR=multiprocessing.Value('I', 0, lock=True),
                  WARNING=multiprocessing.Value('I', 0, lock=True),
                  INFO=multiprocessing.Value('I', 0, lock=True),
                  DEBUG=multiprocessing.Value('I', 0, lock=True))

    def format(self, record):
        msg = logging.Formatter.format(self, record)
        msg = mooseutils.colorText(u'{}: {}'.format(record.name, msg), self.COLOR[record.levelname])

        with self.COUNTS[record.levelname].get_lock():
            self.COUNTS[record.levelname].value += 1

        return msg

class MultiprocessingHandler(logging.StreamHandler):
    """A simple handler that locks when writing with multiprocessing."""

    def flush(self):
        if self._lock:
            with self._lock:
                super(MultiprocessingHandler, self).flush()
        else:
            super(MultiprocessingHandler, self).flush()

    def createLock(self):
        self.lock = None
        self._lock = multiprocessing.Lock()

    def aquire(self):
        pass

    def release(self):
        pass


def init_logging(level=logging.INFO):
    """
    Call this function to initialize the MooseDocs logging formatter.
    """

    # Custom format that colors and counts errors/warnings
    formatter = MooseDocsFormatter()
    handler = MultiprocessingHandler()
    handler.setFormatter(formatter)

    # Setup the custom formatter
    log = logging.getLogger('MooseDocs')
    log.addHandler(handler)
    #log.addHandler(logging.NullHandler())

    log.setLevel(level)
    MooseDocs.LOG_LEVEL = level
    return log

#    return formatter
