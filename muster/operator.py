import re
from functools import wraps
from .utils import typename, annotate
from .utils.compat import Descriptor


def directive(form):
    def deco(*args, **kwargs):
        split = form.format(*args, **kwargs).split(":")
        classifier, directive = split[0], ":".join(split[1:])
        return annotate({classifier: directive})
    return deco


class Operator(Descriptor):

    parent = None
    classifier = None

    def __init__(self, parent=None):
        if parent is not None:
            self.inherit(parent)

    def inherit(self, parent):
        self.parent = parent

    def __set_name__(self, owner, name):
        self.owner = owner
        self.public = name
        mangle = (typename(self), name)
        self.private = "_%s_%s" % mangle
        self._subscribe_to_directives(owner)

    def __set_subclass__(self, cls):
        if self.public not in vars(cls):
            new = type(self)(self)
            new.__set_name__(cls, self.public)
            setattr(cls, self.public, new)

    def _subscribe_to_directives(self, owner):
        for name, value in vars(owner).items():
            directive = self.my_directive(owner, value)
            if directive is not None:
                selector, command, options = directive
                if self.am_selected(selector):
                    self.do_directive(directive, owner, name)

    def my_directive(self, owner, value):
        return find_directives(owner, value).get(self.classifier)

    def do_directive(self, directive, owner, name):
        selector, command, options = directive
        try:
            command = getattr(self, command)
        except AttributeError:
            raise TypeError("The %r named %r has no method %r" % 
                (typename(self), self.public, command))
        command(owner, name, *options)

    def am_selected(self, selector):
        if isinstance(selector, Operator):
            return self == selector
        else:
            return self in list(selector)

    def __eq__(self, other):
        if type(other) is type(self):
            try:
                name = self.public
            except AttributeError:
                raise RuntimeError("Cannot compare an uninitialized %r" % typename(self))
            return name == getattr(other, "public", None)
        else:
            return False


def is_directive(owner, x):
    if isinstance(x, str) and ":" in x and len(x.split(":")) > 2:
        selector = x.replace(" ", "").split(":")[0]
        return hasattr(owner, selector)
    return False


def to_directive(owner, x):
    directive = x.replace(" ", "").split(":")
    selector, command = directive[:2]
    selector = getattr(owner, selector)
    if callable(selector):
        selector = selector()
    options = tuple(directive[2:])
    return selector, command, options


def find_directives(owner, x):
    return dict(iter_find_directives(owner, x))


def iter_find_directives(owner, x):
    for k, v in getattr(x, "__annotations__", {}).items():
        if is_directive(owner, v):
            yield k, to_directive(owner, v)
