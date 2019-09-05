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


NA = object()
_unset = object()


class MandatoryFieldInitError(Exception):
    """
    Raised by Field when a mandatory field is read without being set first.
    """
    __slots__ = 'field_name', 'obj'

    def __init__(self, field_name, obj):
        self.field_name = field_name
        self.obj= obj

    def __str__(self):
        return "Mandatory field '%s' was not set before first access on " \
               "object '%s'." % (self.field_name, self.obj)


class Factory(object):
    """
    Defines a default values' factory for a `Field`, based on a user-provided initialization function.

    >>> class Foo:
    ...     foo = Field(default=Factory(lambda: ["hello"]))
    ...
    >>> o = Foo()
    >>> o.foo
    ['hello']

    """
    __slots__ = ('create',)

    def __init__(self, f):
        """
        Constructs a factory with initialization function `f`.
        `f` should have no mandatory argument and should return the default value to use.

        :param f:
        """
        self.create = f


def factory(f):
    """ decorator to easily create `Factory` objects from functions.

    >>> @factory
    ... def my_default():
    ...    return "hello"
    ...
    >>> class Foo:
    ...     foo = Field(default=my_default)
    ...
    >>> o = Foo()
    >>> o.foo
    'hello'

    :param f:
    :return:
    """
    return Factory(f)


PY36 = sys.version_info >= (3, 6)


class Field(object):
    """
    A class-level attribute definition.

    An easy way to create a field in a class without writing any `__init__` method.
    Typically useful for mixin classes.

    The class has to have a __dict__ in order for this property to work, so classes with `__slots__` are not supported.
    ---
    Note on performance:
    This class implements the descriptor protocol but is actually used on the *first* field
    access only. Indeed, the first time it is accessed on read or write on a specific instance,
    the `Field` descriptor is replaced with the actual value so that subsequent calls are native
    python access calls.

    Inspired by
     - @lazy_attribute (sagemath)
     - @cached_property (werkzeug) and https://stackoverflow.com/questions/24704147/python-what-is-a-lazy-property
     - https://stackoverflow.com/questions/42023852/how-can-i-get-the-attribute-name-when-working-with-descriptor-protocol-in-python
     - attrs / dataclasses / autoclass
    """
    __slots__ = ('default', 'name', 'doc')

    def __init__(self, default=NA, doc=None, name=None):
        """
        Defines a `Field` in a class. The field will be lazily-defined, so if you create an instance of the class, the
        field will not have any value until it is first read or set.

        By default fields are mandatory, which means that you must set them before reading them (otherwise a
        `MandatoryFieldInitError` will be raised).

        You can define an optional field by providing a `default` value. This value will not be copied but used "as is"
        on all instances, following python's classical pattern for default values. If you wish to run specific code to
        instantiate the default value, you may provide a `Factory`

        In python < 3.6 the `name` attribute is mandatory and should be the same name than the one used used in the
        class field definition (i.e. you should define the field as '<name> = Field(name=<name>)').

        :param default:
        :param doc: documentation for the field. This is mostly for class readability purposes for now.
        :param name: in python < 3.6 this is mandatory, and should be the same name than the one used used in the class
            definition (typically, '<name> = Field(name=<name>').
        """
        self.default = default
        if not PY36 and name is None:
            raise ValueError("`name` is mandatory in python < 3.6")
        self.name = name
        self.doc = dedent(doc) if doc is not None else None

    def __set_name__(self, owner, name):
        # called at class creation time
        if self.name is not None and self.name != name:
            raise ValueError("Field name '%s' in class '%s' does not correspond to explicitly declared name '%s' in "
                             "Field constructor" % (name, owner.__class__, self.name))
        self.name = name

    def __get__(self, obj, objtype):
        if obj is None:
            # class-level call ?
            return self

        if self.default is NA:
            # mandatory
            raise MandatoryFieldInitError(self.name, obj)

        # Check if the field is already set in the object __dict__
        value = obj.__dict__.get(self.name, _unset)

        if value is _unset:
            # nominal case: we set the attribute in the object __dict__ on first read
            # so that next reads will be pure native field access
            if isinstance(self.default, Factory):
                value = self.default.create()
            else:
                value = self.default
            obj.__dict__[self.name] = value
        # else:
            # this was probably a manual call of __get__ (or a concurrent call of the first access)
        return value

    def __set__(self, obj, value):
        if obj is not None:
            # set the attribute in the object __dict__ on first read
            # so that next reads will be pure native field access
            obj.__dict__[self.name] = value
        else:
            # class-level call ? what TODO ?
            pass

    def __delete__(self, obj):
        try:
            del obj.__dict__[self.name]
        except KeyError:
            # silently ignore: the field has not been set on that object yet,
            # and we wont delete the class `Field` anyway...
            pass
