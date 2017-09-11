from functools import wraps
from collections import defaultdict
from .operator import Operator, directive


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


Undefined = Sentinel("Undefined", "muster")


def action(method):
    @wraps(method)
    def wrapper(self, obj, **kwargs):
        action = method.__name__
        for cb in self.callbacks["before-%s" % action]:
            getattr(obj, cb)(self, kwargs)
        kwargs["returns"] = method(self, obj, **kwargs)
        for cb in self.callbacks["after-%s" % action]:
            getattr(obj, cb)(kwargs)
        return kwargs["returns"]
    return wrapper


class Member(Operator):

    selector = "^(.*) (.*)$"
    
    def __init__(self, parent=None):
        self.callbacks = defaultdict(list)
        super(Member, self).__init__(parent)
    
    def inherit(self, parent):
        self.__set_name__(parent.owner, parent.public)
        super(Member, self).inherit(parent)
    
    def note_to_instruction(self, note):
        return " ".join(l.lstrip() for l in note.split("\n"))

    def selection(self, cls, instruction, selector):
        selector = getattr(cls, selector)
        if callable(selector):
            selector = selector()
        try:
            selector = list(selector)
        except TypeError:
            selector = [selector]
        if self in selector:
            return instruction
    
    @directive("^then (.*)$")
    def then(self, cls, before, after):
        if not self.callbacks:
            raise ValueError("%r has no callbacks yet" % self)
        for callbacks in self.callbacks.values():
            try:
                i = callbacks.index(after)
            except:
                raise ValueError("No callback %r exists" % after)
            else:
                callbacks.insert(i, before)
        
    @directive("^before (.*)$")
    def before(self, cls, name, action):
        self.callbacks["before-%s" % action].append(name)

    @directive("^after (.*)$")
    def after(self, cls, name, action):
        self.callbacks["after-%s" % action].append(name)

    @action
    def setting(self, obj, value):
        setattr(obj, self.private, value)

    @action
    def deleting(self, obj):
        try:
            delattr(self, self.private)
        except AttributeError:
            raise AttributeError(self.public)

    @action
    def default(self, obj, value=Undefined):
        if value is not Undefined:
            setattr(self, self.private, value)
        return value

    def getting(self, obj):
        try:
            return getattr(obj, self.private)
        except AttributeError:
            value = self.default(obj)
            if value is Undefined:
                raise AttributeError(self.public)
            return value

    def __set__(self, obj, val):
        self.setting(obj, value=val)

    def __get__(self, obj, cls):
        if obj is not None:
            return self.getting(obj)
        else:
            return self

    def __delete__(self, obj):
        self.deleting(obj)
