How about Now?
==============

Handle the concurrent and rechecking parts of seeing whether things are the way
you want yet.

```python
from random import randint
from howaboutnow import AndNow


def is_it_good_yet():
    # Pretend it isn't random.
    if randint(1, 10) == 5:
        # It's good, so we stop.
        return True
    # It isn't good, so we try again.
    return False

# 100 sets of no arguments
arg_sets = [([], dict())] * 100

an = AndNow(fetcher=is_it_good_yet, arg_sets=arg_sets, repeat_delay=0.2,
            max_concurrent=5)
an.start()
an.join()
print 'This is the moment I was waiting for.'
```
