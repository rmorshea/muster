import six
import sys


if sys.version_info < (3, 6, 0):
    class Descriptor(object):
        def __set_name__(self, cls, name):
            pass
        def __set_subclass__(self, cls):
            pass
else:
    class Descriptor(object):
        pass


if sys.version_info < (3, 6, 0):
    class MetaModel(type):
        def __init__(cls, name, bases, classdict):
            for k, v in classdict.items():
                if isinstance(v, Descriptor):
                    v.__set_name__(cls, k)
            for k in dir(cls):
                v = getattr(cls, k)
                if isinstance(v, Descriptor):
                    v.__set_subclass__(cls)
else:
    class MetaModel(type):
        def __init__(cls, name, bases, classdict):
            super().__init__(name, bases, classdict)
            for k in dir(cls):
                v = getattr(cls, k)
                if isinstance(v, Descriptor):
                    v.__set_subclass__(cls)


class Model(six.with_metaclass(MetaModel, object)):
    pass
