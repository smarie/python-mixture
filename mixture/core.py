#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.
import sys
from textwrap import dedent
from warnings import warn

try:  # python 3.5+
    from typing import Optional, Set, List, Callable, Dict
except ImportError:
    pass


FROM_MIXINS_TAG = '__from_mixins__'
"""Attribute set to classes to remember which members where copied from mixins"""


class MixinContainsInitWarning(UserWarning):
    pass


# class MixinNotRegisterableWarning(UserWarning):
#     pass


def apply_mixins(*mixin_classes):
    """
    Decorator to apply a list of mix-in classes in order, to the decorated class.
    The left-most class will be applied last, so as to get the same intuitive behaviour than explicit inheritance in
    the same order.

    Classes are

    :param mixin_classes:
    :param cls: the decorated class
    :return:
    """
    def _effectively_decorate(orig_cls):

        # First gather everything that has to be done
        to_copy = dict()
        for mixin_class in reversed(mixin_classes):
            # display a warning if the mixin class contains an __init__
            if '__init__' in mixin_class.__dict__:
                warn("Mixin class '%' contains an explicit `__init__` method. This is highly NOT recommended.",
                     MixinContainsInitWarning)

            # list all methods that should be copied
            res = list_all_members_to_copy(mixin_class, orig_cls)
            to_copy.update(res)

        # Now perform copy or create a new type
        if issubclass(orig_cls, object):
            # --- new-style class, no need to create a new type

            # copy all members
            for m_name, member in to_copy.items():
                setattr(orig_cls, m_name, member)

            # fill the __from_mixins__ field with the list of names copied
            setattr(orig_cls, FROM_MIXINS_TAG, tuple(to_copy.keys()))

            out_cls = orig_cls

        else:
            # --- old-style class, need to create a new class

            # with the same class type, class name and class parents
            orig_cls_type = type(orig_cls)
            orig_cls_name = orig_cls.__name__
            orig_cls_bases = orig_cls.__bases__

            # but with members that also include the new ones
            # --original
            orig_vars = copy_cls_vars(orig_cls)
            # --new ones
            for m_name, member in to_copy.items():
                orig_vars[m_name] = member
            # --FROM_MIXINS_TAG
            orig_vars[FROM_MIXINS_TAG] = tuple(to_copy.keys())

            out_cls = orig_cls_type(orig_cls_name, orig_cls_bases, orig_vars)

        # register the output class as a subclass of all mixins that support it (python ABC mechanism)
        for mixin_class in reversed(mixin_classes):
            try:
                mixin_class.register(out_cls)
            except AttributeError:
                # warn(
                #     "Mixin class '%s' does not seem to be an ABC so it can not be registered as the virtual parent of "
                #     "class '%s'. As a result issubclass and isinstance will result `False`. You probably wish your "
                #     "mixin class to inherit from `ABC` or use meta `ABCMeta` to fix this", MixinNotRegisterableWarning)
                # ignore silently
                pass

        return out_cls

    return _effectively_decorate


def list_all_members_to_copy(source_cls, dest_cls):
    # type: (...) -> Dict[str, Callable]
    """
    Returns a set containing all members from source class `source_cls` that should be copied to destination class
    `dest_cls`. These are all members, except for:

     - those that are part of the `__from_mixins__` list
     - private members whose names start with '_'
     - members already existing in `dest_cls` itself (not its hierarchy)

    :param source_cls:
    :param dest_cls:
    :param force_copy: the names that should be copied in all cases
    :return:
    """
    members_to_copy = dict()
    force_copy = getattr(dest_cls, FROM_MIXINS_TAG, ())

    for m_name, member in source_cls.__dict__.items():
        # exclude private members
        # exclude explicitly overridden members
        # note: do not use hasattr as we only want to see explicitly overridden
        should_copy = (m_name in force_copy) \
                      or ((not m_name.startswith('_')) and (m_name not in dest_cls.__dict__))

        if should_copy:
            members_to_copy[m_name] = member

    return members_to_copy


# def copy_all_members(source_cls, dest_cls, return_copied_names=False, force_copy=()):
#     # type: (...) -> Optional[Set]
#     """
#     Copies all members from source class `source_cls` to destination class `dest_cls`, except for:
#
#      - private members whose names start with '_'
#      - members already existing in `dest_cls` itself (not its hierarchy)
#
#     :param source_cls:
#     :param dest_cls:
#     :param return_copied_names: if True a set of names copied will be returned
#     :param force_copy: the names that should be copied in all cases
#     :return:
#     """
#     if return_copied_names:
#         copied_names = set()
#
#     for m_name, member in source_cls.__dict__.items():
#         # exclude private members
#         # exclude explicitly overridden members
#         # note: do not use hasattr as we only want to see explicitly overridden
#         should_copy = (m_name in force_copy) \
#                       or (not m_name.startswith('_')) \
#                       or (m_name not in dest_cls.__dict__)
#
#         if should_copy:
#             setattr(dest_cls, m_name, member)
#             if return_copied_names:
#                 copied_names.add(m_name)
#
#     if return_copied_names:
#         return copied_names


def copy_cls_vars(cls):
    """
    "Strongly inspired" :) by https://github.com/yupeng0921/pymixin/blob/master/mixin.py
    :param cls:
    :return:
    """
    cls_vars = cls.__dict__.copy()
    slots = cls_vars.get('__slots__')
    if slots is not None:
        if isinstance(slots, str):
            slots = [slots]
        for slots_var in slots:
            cls_vars.pop(slots_var)
    cls_vars.pop('__dict__', None)
    cls_vars.pop('__weakref__', None)
    return cls_vars


MISSING = object()
_unset = object()


class MandatoryFieldInitError(Exception):
    """
    Raised by `field` when a mandatory field is read without being set first.
    """
    __slots__ = 'field_name', 'obj'

    def __init__(self, field_name, obj):
        self.field_name = field_name
        self.obj= obj

    def __str__(self):
        return "Mandatory field '%s' was not set before first access on " \
               "object '%s'." % (self.field_name, self.obj)


PY36 = sys.version_info >= (3, 6)


def field(default=MISSING, default_factory=MISSING, doc=None, name=None):
    """
    Returns a class-level attribute definition. It allows developers to define an attribute without writing an
    `__init__` method. Typically useful for mixin classes.

    Lazyness
    --------
    The field will be lazily-defined, so if you create an instance of the class, the field will not have any value
    until it is first read or written.

    Optional/Mandatory
    ------------------
    By default fields are mandatory, which means that you must set them before reading them (otherwise a
    `MandatoryFieldInitError` will be raised). You can define an optional field by providing a `default` value.
    This value will not be copied but used "as is" on all instances, following python's classical pattern for default
    values. If you wish to run specific code to instantiate the default value, you may provide a `default_factory`
    callable instead. That callable should have no mandatory argument and should return the default value.

    Documentation
    -------------
    A docstring can be provided for code readability.

    Example
    -------

    >>> import sys, pytest
    >>> if sys.version_info < (3, 6):
    ...     pytest.skip('this doctest does not work on python <3.6 beacause `name` is mandatory')
    ...
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

    Limitations
    -----------
    The class has to have a `__dict__` in order for this property to work, so classes with `__slots__` are not supported.

    Performance overhead
    --------------------
    The `Field` class implements the "non-data" descriptor protocol. So the first time the attribute is read, a small
    python method call extra cost is paid. *But* afterwards the attribute is replaced with a native attribute
    inside the object `__dict__`, so subsequent calls use native access without overhead.
    This was inspired by
    [werkzeug's @cached_property](https://tedboy.github.io/flask/generated/generated/werkzeug.cached_property.html).

    Inspired by
    -----------
    This method was inspired by

     - @lazy_attribute (sagemath)
     - @cached_property (werkzeug) and https://stackoverflow.com/questions/24704147/python-what-is-a-lazy-property
     - https://stackoverflow.com/questions/42023852/how-can-i-get-the-attribute-name-when-working-with-descriptor-protocol-in-python
     - attrs / dataclasses
            In python < 3.6 the `name` attribute is mandatory and should be the same name than the one used used in the
        class field definition (i.e. you should define the field as '<name> = field(name=<name>)').

    :param default: a default value for the field. Providing a `default` makes the field "optional". `default` value
        is not copied on new instances, if you wish a new copy to be created you should provide a `default_factory`
        instead. Only one of `default` or `default_factory` should be provided.
    :param default_factory: a factory that will be called (without arguments) to get the default value for that
        field, everytime one is needed. Providing a `default_factory` makes the field "optional". Only one of `default`
        or `default_factory` should be provided.
    :param doc: documentation for the field. This is mostly for class readability purposes for now.
    :param name: in python < 3.6 this is mandatory, and should be the same name than the one used used in the class
        definition (typically, `class Foo:    <name> = field(name=<name>)`).
    :return:
    """
    return Field(default=default, default_factory=default_factory, doc=doc, name=name)


class Field(object):
    __slots__ = ('default', 'is_factory', 'name', 'doc')

    def __init__(self, default=MISSING, default_factory=MISSING, doc=None, name=None):
        """See help(field) for details"""
        if default_factory is not MISSING:
            if default is not MISSING:
                raise ValueError("Only one of `default` and `default_factory` should be provided")
            else:
                self.default = default_factory
                self.is_factory = True
        else:
            self.default = default
            self.is_factory = False

        if not PY36 and name is None:
            raise ValueError("`name` is mandatory in python < 3.6")
        self.name = name
        self.doc = dedent(doc) if doc is not None else None

    def __set_name__(self, owner, name):
        # called at class creation time
        if self.name is not None and self.name != name:
            raise ValueError("field name '%s' in class '%s' does not correspond to explicitly declared name '%s' in "
                             "field constructor" % (name, owner.__class__, self.name))
        self.name = name

    def __get__(self, obj, objtype):
        if obj is None:
            # class-level call ?
            return self

        if self.default is MISSING:
            # mandatory
            raise MandatoryFieldInitError(self.name, obj)

        # Check if the field is already set in the object __dict__
        value = obj.__dict__.get(self.name, _unset)

        if value is _unset:
            # nominal case: we set the attribute in the object __dict__ on first read
            # so that next reads will be pure native field access
            if self.is_factory:
                value = self.default()
            else:
                value = self.default
            obj.__dict__[self.name] = value
        # else:
            # this was probably a manual call of __get__ (or a concurrent call of the first access)
        return value

    # not needed apparently
    # def __delete__(self, obj):
    #     try:
    #         del obj.__dict__[self.name]
    #     except KeyError:
    #         # silently ignore: the field has not been set on that object yet,
    #         # and we wont delete the class `field` anyway...
    #         pass
