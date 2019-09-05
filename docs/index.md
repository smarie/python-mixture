# mixture

*Mixin classes for great objects !*

[![Python versions](https://img.shields.io/pypi/pyversions/mixture.svg)](https://pypi.python.org/pypi/mixture/) [![Build Status](https://travis-ci.org/smarie/python-mixture.svg?branch=master)](https://travis-ci.org/smarie/python-mixture) [![Tests Status](https://smarie.github.io/python-mixture/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mixture/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mixture/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mixture)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-mixture/) [![PyPI](https://img.shields.io/pypi/v/mixture.svg)](https://pypi.python.org/pypi/mixture/) [![Downloads](https://pepy.tech/badge/mixture)](https://pepy.tech/project/mixture) [![Downloads per week](https://pepy.tech/badge/mixture/week)](https://pepy.tech/project/mixture) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-mixture.svg)](https://github.com/smarie/python-mixture/stargazers)

Creating [mixin classes](https://en.wikipedia.org/wiki/Mixin) is a quite elegant way to design reusable object-oriented code in python. Doing it right might be tricky as python provides many alternate ways. This library provides

 - a minimal `field` implementation enabling developers to create mixin classes without having to define `__init__` methods (thus avoiding the multiparent initialization hell) 
 - an `@apply_mixins` decorator for those users wishing to avoid inheritance *at all* when mixing classes
 - (TODO) provides a few reusable mix-in class


## Installing

```bash
> pip install mixture
```

## Usage

### 1. Mix-in basics

#### a- Defining

A mix-in class in python is typically a class :

 - **without `__init__` constructor** (to avoid constructor inheritance hell in case of multiple inheritance), 
 - providing a set of **instance/static/class methods** to provide some functionality. This functionality may be based on the existence of certain fields.
 - that may also include **class attributes**. This can be used to explicitly add a field to an object without defining an `__init__` method, as we'll see below)
 - without parent classes, or where the **parent classes are mix-in classes** themselves

For example this is a very basic mix-in class without any requirement on instance attributes:

```python
class BarkerMixin:
    def bark(self):
        print("barking loudly")
```

Thanks to the `field` goodie provided in this library, we can easily create mix-in classes that include fields definitions without defining a constructor:

```python
from mixture import field

class TweeterMixin:
    afraid = field(default=False, 
                   doc="Status of the tweeter. When this is `True`," 
                       "tweets will be less aggressive.")

    def tweet(self):
        how = "lightly" if self.afraid else "loudly"
        print("tweeting %s" % how)
```

See [API documentation](./api_reference.md) for details on `field`.

!!! success "No performance overhead"
    For those of the readers who have recognized it: `field` returns a ["non-data" python descriptor](https://docs.python.org/3.7/howto/descriptor.html). So the first time the attribute is read, a small python method call extra cost is paid. *But* afterwards the attribute is replaced with a native attribute inside the object `__dict__`, so subsequent calls use native access without overhead. This was inspired by [werkzeug's @cached_property](https://tedboy.github.io/flask/generated/generated/werkzeug.cached_property.html).

!!! info "Alternatives for class-level field definition"
    You can obviously use more advanced libraries such as [`attrs`](http://www.attrs.org) or [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) but be aware that by default they create an `__init__` method for you. The intent here is to provide a "minimal viable product" to define class-level fields without creating `__init__` methods.

#### b- Mixing

In python we can already use such mixin classes without additional framework, simply by inheriting from them thanks to python's multiple inheritance capabilities:

```python
class MagicDuck(BarkerMixin, TweeterMixin):
    pass
```

Let's try it by creating a barking and tweeting duck:

```python
>>> d = MagicDuck()
>>> d.bark()
barking loudly
>>> d.tweet()
tweeting loudly
>>> d.afraid = True
>>> d.tweet()
tweeting lightly
```


In addition, this library provides a way to apply mixin classes *without inheritance*. The author does not have any opinion on this alternative, it may be marginally faster as the MRO cost is not paid for accessing members, but this would have to be studied (if you're interested, please discuss it [here](https://github.com/smarie/python-mixture/issues/1)).

```python
from mixture import apply_mixins

@apply_mixins(BarkerMixin, TweeterMixin)
class MagicDuck:
    pass
```

in that case a special field is set on the class for reference, containing the list of all members that were created as the result of copying from mixins:

```python
>>> MagicDuck.__from_mixins__
('tweet', 'afraid', 'bark')
```

and if the mixin is an [Abstract Base Class](https://docs.python.org/3/library/abc.html), the decorated class is registered as a virtual subclass so that `isinstance` and `issubclass` still work as expected.

### 2. Handy Mix-in classes

**TODO**

## Main features / benefits

 * create mix-in classes without `__init__`, thanks to `field` 
 * optionally apply mix-ins without inheritance thanks to `@apply_mixins`

## See Also


This library was inspired by:

 * [`pymixin`](https://github.com/yupeng0921/pymixin)
 * [`werkzeug.cached_property`](https://werkzeug.palletsprojects.com/en/0.15.x/utils/#werkzeug.utils.cached_property)
 * [`attrs`](http://www.attrs.org/)
 * [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
 * [`autoclass`](https://smarie.github.io/python-autoclass/)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-mixture](https://github.com/smarie/python-mixture)
