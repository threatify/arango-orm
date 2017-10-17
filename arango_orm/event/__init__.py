from collections import defaultdict

import six

"""
_registrars = {
    'post_save': {Person: [], Car: []},
    'post_delete': {Collection: []}
}
"""
_registrars = defaultdict(lambda: defaultdict(list))


def dispatch(target, event, *args, **kwargs):
    by_event = _registrars[event]
    for t in by_event.keys():
        if isinstance(target, t):
            for fn in by_event[t]:
                fn(target, event, *args, **kwargs)


def listen(target, event, fn, *args, **kwargs):
    events = [event] if isinstance(event, six.text_type) else event

    for event in events:
        _registrars[event][target].append(fn)


def listens_for(target, event, *args, **kwargs):
    def decorator(fn):
        listen(target, event, fn, *args, **kwargs)
        return fn
    return decorator
