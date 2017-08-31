import re
from functools import wraps
from .utils import typename
from .utils.compat import Descriptor


class Servant(Descriptor):

    parent = None

    def __init__(self, parent=None):
        if parent is not None:
            self.inherit(parent)

    def inherit(self, parent):
        self.parent = parent

    def __set_subclass__(self, cls):
        if self.public not in vars(cls):
            new = type(self)(self)
            new.__set_name__(cls, self.public)
            setattr(cls, self.public, new)

    def __set_name__(self, owner, name):
        self.owner = owner
        self.public = name
        mangle = (typename(self), name)
        self.private = "_%s_%s" % mangle
        self._subscribe_directives(owner)

    def _subscribe_directives(self, owner):
        for k, v in vars(owner).items():
            if callable(v) and self.has_directive(v):
                selector, command, option = self.resolve_directive(v)
                if self.is_my_directive(owner, selector, command):
                    getattr(self, command)(owner, option, k)

    def is_my_directive(self, owner, selector, command):
        selector = getattr(owner, selector)
        if isinstance(selector, Servant):
            return self == selector
        else:
            return self in selector

    @classmethod
    def has_directive(cls, method):
        return cls.annotation() in getattr(method, "__annotations__", {})

    def resolve_directive(self, method):
        annotations = getattr(method, "__annotations__", {})
        directive = annotations.get(self.annotation(), "").split(":")
        selector, command, option = tuple(x or None for x in directive)
        return (selector or self, command, option)

    def __eq__(self, other):
        if type(other) is type(self):
            try:
                name = self.public
            except AttributeError:
                raise RuntimeError("Cannot compare an uninitialized %r" % typename(self))
            return name == getattr(other, "public", None)
        else:
            return False

    @classmethod
    def annotation(cls):
        return "_".join(n.lower() for n in re.findall('[A-Z][^A-Z]*', typename(cls)))


class grouping(object):

    def __init__(self, type):
        self.type = type

    def __call__(self, filter):
        self.name = filter.__name__
        self.filter = filter
        return self

    def __get__(self, obj, cls):
        servants = []
        for k in dir(cls):
            if k != self.name:
                try:
                    v = getattr(cls, k)
                except:
                    pass
                else:
                    if isinstance(v, self.type):
                        servants.append(v)
        if obj is None:
            return list(self.filter(cls, servants))
        else:
            result = {}
            for s in self.filter(cls, servants):
                name = s.public
                result[name] = getattr(obj, name)
            return result
