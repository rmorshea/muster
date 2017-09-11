import re
import inspect
from .compat import Model


def annotate(**notes):
    local = inspect.currentframe().f_back.f_locals
    annotations = local.setdefault("__annotations__", {})
    for k, v in notes:
        annotations[k] = v


def annotations(x):
    return getattr(x, "__annotations__", {})


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


class grouping(object):

    def __init__(self, filter):
        self.name = filter.__name__
        self.filter = filter

    def __get__(self, obj, cls):
        result = []
        names = dir(cls)
        names.remove(self.name)
        for k in names:
            if k != self.name:
                try:
                    v = getattr(cls, k)
                except:
                    pass
                else:
                    if self.filter(cls, v):
                        result.append(v)
        if obj is None:
            return result
        else:
            values = {}
            for s in result:
                name = s.public
                values[name] = getattr(obj, name)
            return values


class instruction(object):

    _delim = " "

    def __init__(self, data):
        if not isinstance(data, str):
            raise TypeError("Expected a string, not %r" % data)
        self._data = data

    def __getattr__(self, data):
        if data.startswith("_"):
            return super(instruction, sef).__getattr__(data)
        forms = re.findall("(%[^%])", self._data)
        if len(forms):
            forms[0] = data
            data = self._data % tuple(forms)
        else:
            data = self._data + self._delim + data
        return instruction(data)
    
    def __repr__(self):
        return self._data
