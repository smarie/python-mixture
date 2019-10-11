#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.

from warnings import warn

try:  # python 3.5+
    from typing import Optional, Set, List, Callable, Dict, Type, Any, TypeVar, Union, Iterable, Tuple, Mapping
    from valid8 import ValidationFuncs, ValidationError
    use_type_hints = True
except ImportError:
    use_type_hints = False


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
            # TODO maybe it would be better that the field is an ordered tuple by mixin order ot appearance.
            #    but that is quite tricky since some names can be overridden by several mixins
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
                #     "Mixin class '%s' does not seem to be an ABC so it can not be registered as the virtual parent of"
                #     " class '%s'. As a result issubclass and isinstance will result `False`. You probably wish your "
                #     "mixin class to inherit from `ABC` or use meta `ABCMeta` to fix this",
                #     MixinNotRegisterableWarning)
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
