# Muster


A streamlined framework for responsive classes.


# Summary


Muster, is a [descriptor](https://docs.python.org/howto/descriptor.html) callback framework, that is both approachable, and extremely extensible. Other frameworks have been [approachable](https://traitlets.readthedocs.io/en/stable/) and others [extensible](http://www.attrs.org/en/stable/index.html), but few, if any have been both. Muster uses specialized [metaclass](https://jakevdp.github.io/blog/2012/12/01/a-primer-on-python-metaclasses/), but manages to remain agnostic about the user's class model. Despite this, Muster still allows you to define customized callbacks to arbitrary object mutations. The former means that creating classes with Muster is about as simple as it gets, and the latter makes the framework extremely adaptable. To accomplish this, Muster uses three core concepts:

1. **Models** - the place where Members live
2. **Members** - the things directives control
3. **Directives** - manage Member operations


---


## Models


A Model is simply a class which inherits from `muster.Model`

```python
from muster import Model

class A(Model):
    """This is my Model."""
    pass
```

so you're pretty much free to do whatever you want!

*Unless you're concerned with the dark arts of [metaclasses](https://jakevdp.github.io/blog/2012/12/01/a-primer-on-python-metaclasses/).*


## Members


Members are objects which exist on classes. Without directives, Members like `x` act prety much like any other attribute:

```python
from muster import Model, Member

class A(Model):
    x = Member()
```

+ setting values

```python
a.x = 1
```

+ getting values

```python
print(a.x)
```

+ and deleting values

```python
del a.x
```


## Directives


Directives are string annotations which are identified by the `Member` descriptors they refer to, and trigger a response from the `Member`. This is achieved by performing two seperate operations that leverage [regex](https://docs.python.org/library/re.html) patterns - the first determines whether a directive refers to a particular `Member`, while the second figures out whether the `Member` knows of the directive. Once this is done, a corresponding method is called which understands how to carry out the directive. While there is a base class which can support any kind of directive `Member` descriptors know of two basic ones: `"before ..."` and `"after..."` with the following supported actions:

+ "setting" - occurs when the member is set
+ "deleting" - occurs when the member is deleted
+ "default" - occurs when the member is retrieved but has no value.


### `"before <action> <member>"`


A "before" directive allows you to register a callback that will be triggered before a `Member`'s method is called.

For example:

```python
from muster import Model, Member

class A(Model):

    x = Member()
    
    _x_is_int : "before setting x"
    
    def _x_is_int(self, member, data):
        data["value"] = int(data["value"])
```

In this example `setting` corresponds to a supported `<action>` and `x` refers to the `<member>` that should respond to the directive.


### `"after <action> <member>"`


A "after" directive allows you to register a callback that will be triggered after a `Member`'s method is called.

```python
from muster import Model, Member

class A(Model):

    x = Member()
    
    _x_old : "before setting x"
    _x_change : "after setting x"
    
    def _x_old(self, member, data):
        data["old"] = getattr(self, "x", None)

    def _x_change(self, member, data):
        msg = "x : %r => %r"
        info = (data["old"], data["value"])
        print(msg % info)

A().x = 1
# x : None => 1
```

In this example we see a "before" directive used in conjunction with an "after" directive. Similarly to the "before" directive, in "after", `setting` corresponds to a supported `<action>` and `x` refers to the `<member>` that should respond to the directive.
