# mixture

*Mixin classes for great objects !*

[![Python versions](https://img.shields.io/pypi/pyversions/mixture.svg)](https://pypi.python.org/pypi/mixture/) [![Build Status](https://travis-ci.org/smarie/python-mixture.svg?branch=master)](https://travis-ci.org/smarie/python-mixture) [![Tests Status](https://smarie.github.io/python-mixture/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mixture/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mixture/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mixture)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-mixture/) [![PyPI](https://img.shields.io/pypi/v/mixture.svg)](https://pypi.python.org/pypi/mixture/) [![Downloads](https://pepy.tech/badge/mixture)](https://pepy.tech/project/mixture) [![Downloads per week](https://pepy.tech/badge/mixture/week)](https://pepy.tech/project/mixture) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-mixture.svg)](https://github.com/smarie/python-mixture/stargazers)

**TODO**

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

Thanks to the `Field` goodie provided in this library, we can easily create mix-in classes that include fields definitions without defining a constructor:

```python
from mixture import Field

class TweeterMixin:
    afraid = Field(default=False, 
                   doc="Status of the tweeter. When this is `True`, tweets will be lighter")

    def tweet(self):
        how = "lightly" if self.afraid else "loudly"
        print("tweeting %s" % how)
```

See [API documentation](./api_reference.md) for details on `Field` and `Factory`.

!!! success "No performance overhead"
    For those of the readers who have recognized it: `Field` implements the [python descriptor protocol](https://docs.python.org/3.7/howto/descriptor.html). *But* on first get/set the attribute is replaced with a native attribute inside the object `__dict__` so subsequent calls use native access without overhead. This was inspired by [werkzeug's @cached_property](https://tedboy.github.io/flask/generated/generated/werkzeug.cached_property.html).

!!! info "Alternatives for class-level Field definition"
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


In addition, this library provides a way to apply mixin classes *without inheritance*.

```python
from mixture import apply_mixins

@apply_mixins(BarkerMixin)
class Duck:
    pass
```

in that case a special field is set on the class, containing the list of all members that were created as the result of copying from mixins:

```python
>>> Duck.__from_mixins__
('bark',)
```

and if the mixin is an [Abstract Base Class](https://docs.python.org/3/library/abc.html), the decorated class is registered as a virtual subclass:

```python
>>> issubclass(Duck, BarkerMixin)
True
 ```

Lets create a barking duck:

```python
>>> d = Duck()
>>> d.bark()
barking loudly
>>> isinstance(d, BarkerMixin)
True
```

## Main features / benefits

**TODO**

## See Also

 * [`pymixin`](https://github.com/yupeng0921/pymixin)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-mixture](https://github.com/smarie/python-mixture)
