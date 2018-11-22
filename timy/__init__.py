import time
import sys
import logging

from .settings import (
    timy_config,
    TrackingMode
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def output(ident, text):
    if not timy_config.tracking:
        return

    message = '{} {}'.format(ident, text)

    if timy_config.tracking_mode == TrackingMode.PRINTING:
        print(message, file=sys.stderr)
    elif timy_config.tracking_mode == TrackingMode.LOGGING:
        logger.info(message)


class Timer(object):

    def __init__(self, ident=timy_config.DEFAULT_IDENT,
                 include_sleeptime=True):
        self.ident = ident
        self.start = 0
        if include_sleeptime:
            self.time_func = time.perf_counter
        else:
            self.time_func = time.process_time

    def __enter__(self):
        self.start = self.time_func()
        return self

    def __exit__(self, type, value, traceback):
        output(self.ident, '{:f}'.format(self.elapsed))

    @property
    def elapsed(self):
        return self.time_func() - self.start

    def track(self, name='track'):
        output(self.ident, '({}) {:f}'.format(name, self.elapsed))


def timer(ident=timy_config.DEFAULT_IDENT, loops=1, include_sleeptime=True):
    if include_sleeptime:
        time_func = time.perf_counter
    else:
        time_func = time.process_time

    def _timer(function, *args, **kwargs):
        if not timy_config.tracking:
            return function

        def wrapper(*args, **kwargs):
            times = []
            for _ in range(loops):
                start = time_func()
                result = function(*args, **kwargs)
                end = time_func()
                times.append(end - start)

            total_secs = sum(times)

            print(file=sys.stderr)
            output(ident, 'executed ({}) for {} times in {:.2f} secs ({:.2f} hours)'.format(
                function.__name__, loops, total_secs, total_secs / 3600.0))
            # output(ident, 'best time ({}) was {:f} secs'.format(function.__name__, min(times)))
            return result

        return wrapper
    return _timer
