#!/usr/bin/python

"""

    synchronized.py

    201801 Tom Wilkin <YE91256>
    This module add a decorator to enforce synchronisation on a function that will
    ensure no other call can enter the same function until the previous call has
    returned.
    Example adapted from http://theorangeduck.com/page/synchronized-python

"""

import threading

from functools import wraps


def synchronized(func):
    """Decorator for a function that must be synchronised so no two threads
    can enter the same function at the same time.
    :param func: The function to make synchronised."""
    # initialise the lock
    func.__synchronized_lock__ = threading.Lock()
    
    def _decorator(*args, **kws):
        with func.__synchronized_lock__:
            # run the function with the lock to ensure other calls cannot enter
            return func(*args, **kws)
    
    return wraps(func)(_decorator)
