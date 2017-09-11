import six
import sys


if sys.version_info < (3, 6, 0):
    class MetaBase(type):
        def __init__(cls, name, bases, classdict):
            super(MetaBase, cls).__init__(name, bases, classdict)
            for k, v in classdict.items():
                if hasattr(v, "__set_name__"):
                    v.__set_name__(cls, k)
            for k in dir(cls):
                try:
                    v = getattr(cls, k)
                except AttributeError:
                    pass
                else:
                    if hasattr(v, "__set_subclass__"):
                        v.__set_subclass__(cls)
else:
    class MetaBase(type):
        def __init__(cls, name, bases, classdict):
            super().__init__(name, bases, classdict)
            for k in dir(cls):
                try:
                    v = getattr(cls, k)
                except AttributeError:
                    pass
                else:
                    if hasattr(v, "__set_subclass__"):
                        v.__set_subclass__(cls)


class Base(six.with_metaclass(MetaBase, object)):
    pass
