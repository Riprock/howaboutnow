"""Are all those things the way I want them yet? How about now?"""

from threading import Thread, Timer
from Queue import Queue


class AndNow(object):
    """Handles all the asynchronous fetching and result checking."""

    POISON_PILL = object()

    def __init__(self, fetcher=None, checker=bool, arg_sets=None,
                 max_concurrent=None, repeat_delay=0):
        """
        Prepare for a round of checking and rechecking.

        :keyword fetcher: Function to call to fetch results.
        :keyword checker:
            Function to call to decide if a result passes, or doesn't
            and needs rechecking. The default is :py:func:`bool`.
        :keyword arg_sets:
            Arguments for the fetcher function. A list of tuples. The
            tuples are a list of args and a dictionary of kwargs.
        :keyword max_concurrent:
            The maximum amount of concurrent calls to the fetcher
            function. The default is the length of ``arg_sets``.
        :keyword repeat_delay:
            The minimum time in seconds to wait between calling the
            fetcher function with the same arg_set. The default is not
            to wait.
        """
        self.fetcher = fetcher
        self.checker = checker
        self.arg_sets = arg_sets
        self.max_concurrent = max_concurrent
        self.repeat_delay = repeat_delay
        self.fetch_queue = Queue()
        if self.arg_sets:
            self.passed_count = 0
            for arg_set in arg_sets:
                self.fetch_queue.put(arg_set)
        self.results_queue = Queue()
        self.started = False
        self.checker_threads = []

    def start(self):
        """Kick off the cycle of asynchronous rechecking."""
        if self.started:
            # No exceptions, no nothin', just pass. We're started.
            return
        for i in range(self.max_concurrent or len(self.arg_sets)):
            t = Thread(target=self.keep_checking)
            self.checker_threads.append(t)
            t.start()
        self.started = True

    def keep_checking(self):
        """
        Consume a queue of *arg_sets* and call the *fetcher* function.
        If the results do not pass the *checker* function then add them
        back to the queue. Stop when all the *arg_sets* have passed.
        This method is the target of the :py:class:`threading.Thread`
        instances started in :py:meth:`start`
        """
        while True:
            arg_set = self.fetch_queue.get()
            # If we're meant to stop, or have stopped
            if arg_set is self.POISON_PILL:
                # Let other threads know
                self.fetch_queue.put(self.POISON_PILL)
                break
            result = self.fetcher(*arg_set[0], **arg_set[1])
            passed = self.checker(result)
            if passed:
                self.passed_count += 1
            else:
                if self.repeat_delay:
                    Timer(self.repeat_delay, self.fetch_queue.put,
                          args=[arg_set]).start()
                else:
                    self.fetch_queue.put(arg_set)
            self.results_queue.put((arg_set, result, passed))
            if self.passed_count == len(self.arg_sets):
                # Let next thread know to end too
                self.fetch_queue.put(self.POISON_PILL)
                break

    def join(self):
        """Block until all *arg_sets* have passed."""
        for t in self.checker_threads:
            t.join()
