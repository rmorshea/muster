from .utils import annotate


def directive(annotation):
    return directive_template("{0}")


def directive_template(template, interpreter=None):
    def decorator(*args, **kwargs):
        if interpreter is None:
            raw = template.format(*args, **kwargs)
        else:
            data = interpreter(*args, **kwargs)
            raw = template.format(**data)
        if not is_directive(raw):
            raise TypeError("%r is not a directive" % raw)
        else:
            split = raw.split(":")
        classifier, directive = split[0], ":".join(split[1:])
        return annotate({classifier: directive})
    return decorator


def is_directive(x):
    return isinstance(x, str) and ":" in x and len(x.split(":")) > 2


def directive_components(x):
    if not is_directive(x):
        raise TypeError("%r is not a directive" % x)
    return split(x)


def directive_in(owner, x):
    if is_directive(x):
        selector = directive_components(x)[0]
        return hasattr(owner, selector)
    else:
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
        if directive_in(owner, v):
            yield k, to_directive(owner, v)


def split(x):
    return x.replace(" ", "").split(":")


def join(x, *y):
    return ":".join(x + y)

