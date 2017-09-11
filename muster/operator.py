import re
import inspect
from .utils import annotations, instruction as inst


def directive(pattern, name=None):
    # Must be the last decorator. If not,
    # then provide the function's name.
    local = inspect.currentframe().f_back.f_locals
    dirs = local.setdefault("directives", {})
    def decorator(method):
        dirs[name or method.__name__] = pattern
        return method
    return decorator


class Operator(object):
    
    # never matches
    selector = "^(?!.*)$"
    
    def __init__(self, parent=None):
        self.instructions = {}
        if parent is not None:
            self.inherit(parent)

    def inherit(self, parent):
        inherits = parent.instructions
        self.instructions.update(inherits)

    def __set_name__(self, owner, name):
        self.owner = owner
        self.public = name
        self.private = "_%s_%s" % (type(self).__name__, name)
        self.instructions.update(self.my_instructions(owner))
        for n, i in self.instructions.items():
            self.try_directive(owner, n, i)
    
    def __set_subclass__(self, cls):
        if self.public not in vars(cls):
            new = type(self)(self)
            new.__set_name__(cls, self.public)
            setattr(cls, self.public, new)

    def my_instructions(self, cls):
        for name, note in annotations(cls).items():
            if isinstance(note, inst):
                note = str(note)
            if isinstance(note, str):
                instruction = self.note_to_instruction(note)
                match = re.match(self.selector, instruction)
                if match is not None:
                    groups = match.groups()
                    instruction = self.selection(cls, *groups)
                    if instruction is not None:
                        yield name, instruction
    
    def note_to_instruction(self, note):
        return note

    def selection(self, cls, *args):
        raise NotImplementedError()

    def try_directive(self, cls, name, instruction):
        for directive, args in self.match_directives(instruction):
            getattr(self, directive)(cls, name, *args)

    def match_directives(self, instruction):
        for k, v in self.inherited_directives():
            m = re.match(v, instruction)
            if m is not None:
                yield k, m.groups()

    @classmethod
    def inherited_directives(cls):
        seen = set()
        for c in reversed(cls.mro()):
            if issubclass(c, Operator):
                d = getattr(c, "directives", {})
                for k, v in d.items():
                    if k not in seen:
                        seen.add(k)
                        yield k, v
    def __eq__(self, other):
        return (type(other) is type(self) and
            (other is self or
            other.public == self.public))
