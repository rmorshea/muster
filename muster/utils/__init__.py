import inspect


def annotate(*args, **kwargs):
    notes = dict(*args, **kwargs)
    def setup(method):
        if not hasattr(method, "__annotations__"):
            setattr(method, "__annotations__", {})
        method.__annotations__.update(notes)
        return method
    return setup


class Sentinel(object):

    def __init__(self, name, module, info=None):
        self.name = "%s.%s" % (module, name)
        self.info = info

    def __repr__(self):
        return self.name

    def __str__(self):
        if self.info is not None:
            return "%s - %s" % (repr(self), self.info)
        else:
            return repr(self)


def typename(x):
    if not inspect.isclass(x):
        x = type(x)
    return x.__name__


class ExitQueue(object):

    def __init__(self):
        self._stack = []

    def __enter__(self):
        return self

    def enter_context(self, other):
        self._stack.append(other)
        return other.__enter__()

    def __exit__(self, type, value, traceback):
        for context in self._stack:
            context.__exit__(type, value, None)
        self._stack = []


class grouping(object):

    def __init__(self, type):
        self.type = type

    def __call__(self, filter):
        self.name = filter.__name__
        self.filter = filter
        return self

    def __get__(self, obj, cls):
        result = []
        for k in dir(cls):
            if k != self.name:
                try:
                    v = getattr(cls, k)
                except:
                    pass
                else:
                    if isinstance(v, self.type):
                        result.append(v)
        if obj is None:
            return list(self.filter(cls, result))
        else:
            values = {}
            for s in self.filter(cls, result):
                name = s.public
                values[name] = getattr(obj, name)
            return values
