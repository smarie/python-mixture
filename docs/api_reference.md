# API reference

In general, `help(symbol)` will provide the latest up-to-date documentation.

## 1. Mixin basics

### *`field`*

`field(default=MISSING, default_factory=MISSING, doc=None, name=None)`

Returns a class-level attribute definition. It allows developers to define an attribute without writing an 
`__init__` method. Typically useful for mixin classes.

**Lazyness**

The field will be lazily-defined, so if you create an instance of the class, the field will not have any value 
until it is first read or written.

**Optional/Mandatory**

By default fields are mandatory, which means that you must set them before reading them (otherwise a
`MandatoryFieldInitError` will be raised). You can define an optional field by providing a `default` value. 
This value will not be copied but used "as is" on all instances, following python's classical pattern for default 
values. If you wish to run specific code to instantiate the default value, you may provide a `default_factory`
callable instead. That callable should have no mandatory argument and should return the default value. 

**Typing**

Type hints for fields can be provided using the standard python typing mechanisms (type comments for python < 3.6  and class member type hints for python >= 3.6). Types declared this way will not be checked at runtime, they are just hints for the IDE.
    
Instead, you can specify a `type` to declare that type should be checked. In that case the type will be validated everytime a new value is provided, and a `TypeError` will be raised if invalid. The corresponding type hint is automatically declared by `field` so your IDE will know about it, no need to use additional type hints.

**Documentation**

A docstring can be provided for code readability.

**Example**

```python
>>> from mixture import field
>>> class Foo:
...     foo = field(default='bar', doc="This is an optional field with a default value")
...     foo2 = field(default_factory=list, doc="This is an optional with a default value factory")
...     foo3 = field(doc="This is a mandatory field")
...
>>> o = Foo()
>>> o.foo   # read access with default value
'bar'
>>> o.foo2  # read access with default value factory
[]
>>> o.foo2 = 12  # write access
>>> o.foo2
12
>>> o.foo3  # read access for mandatory attr without init
Traceback (most recent call last):
    ...
mixture.core.MandatoryFieldInitError: Mandatory field 'foo3' was not set before first access on object...
>>> o.foo3 = True
>>> o.foo3  # read access for mandatory attr after init
True
>>> del o.foo3  # all attributes can be deleted, same behaviour than new object
>>> o.foo3
Traceback (most recent call last):
    ...
mixture.core.MandatoryFieldInitError: Mandatory field 'foo3' was not set before first access on object...
```

**Limitations**

Old-style classes are not supported: in python 2, don't forget to inherit from `object`.

**Performance overhead**

`field` has two different ways to create your fields. One named `NativeField` is faster but does not permit type checking, validation, or converters; besides it does not work with classes using `__slots__`. It is used by default everytime where it is possible, except if you use one of the abovementioned features. In that case a `DescriptorField` will transparently be created. You can force a `DescriptorField` to be created by setting `use_descriptor=True`.
    
The `NativeField` class implements the "non-data" descriptor protocol. So the first time the attribute is read, a small  python method call extra cost is paid. *But* afterwards the attribute is replaced with a native attribute inside the object `__dict__`, so subsequent calls use native access without overhead. 
This was inspired by [werkzeug's @cached_property](https://tedboy.github.io/flask/generated/generated/werkzeug.cached_property.html). 

**Inspired by**

This method was inspired by 

 - @lazy_attribute (sagemath)
 - @cached_property (werkzeug) and https://stackoverflow.com/questions/24704147/python-what-is-a-lazy-property
 - https://stackoverflow.com/questions/42023852/how-can-i-get-the-attribute-name-when-working-with-descriptor-protocol-in-python
 - attrs / dataclasses

**Parameters**

 - `type`: an optional type for the field. If one is provided, the field will not be a simple (fast) field any more but will be a descriptor (slower) field.
 - `default`: a default value for the field. Providing a `default` makes the field "optional". `default` value is not copied on new instances, if you wish a new copy to be created you should provide a `default_factory` instead. Only one of `default` or `default_factory` should be provided.
 - `default_factory`: a factory that will be called (without arguments) to get the default value for that field, everytime one is needed. Providing a `default_factory` makes the field "optional". Only one of `default` or `default_factory` should be provided.
 - `doc`: documentation for the field. This is mostly for class readability purposes for now.
 - `name`: in python < 3.6 this is mandatory, and should be the same name than the one used used in the class definition (typically, `class Foo:    <name> = field(name=<name>)`).
 - `use_descriptor`: a boolean (default: `False`) that can be turned to `True` to force a field to be a descriptor field. This is mandatory for classes that do not have `__dict__` (so, classes with `__slots__`)
