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

### Basic mix-in mechanisms

A mix-in class is typically 

 - a class without constructor, 
 - that implements some functionality as a set of functions, based on the existence of certain fields.
 - that may include include class attributes (for example to add fields using the "descriptor protocol")


```python
from abc import ABC

class BarkerMixin(ABC):
    def bark(self):
        print("barking loudly")
```

In native python you can already use mixin classes by inheriting from them:

```python
class Duck(BarkerMixin):
    pass
```

In addition, this library provides a way to apply mixin classes *without inheritance*:

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
