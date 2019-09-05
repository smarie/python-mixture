#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.

import sys

import pytest

from mixture import apply_mixins, field, MixinContainsInitWarning, MandatoryFieldInitError

from ..utils import ABC


@pytest.mark.parametrize("old_style_class", [False, True], ids="oldstyle={}".format)
def test_apply_mixins(old_style_class):
    """ nominal test with two mixin classes, checks that the overriding order is correct"""

    class DummyMixinA:
        def foo(self, a):
            return a + 1

    class DummyMixinB(ABC):
        def foo(self, a):
            return a + 2

    if not old_style_class:
        @apply_mixins(DummyMixinA, DummyMixinB)
        class MyClass(object):
            pass
    else:
        # create an old-style class
        if sys.version_info < (3, 0):
            @apply_mixins(DummyMixinA, DummyMixinB)
            class MyClass:
                pass
        else:
            # python 3: harder, impossible ?
            pytest.skip("it is not possible to create an old style class with python 3+")

    # Check that copy worked correctly
    assert MyClass.__from_mixins__ == ('foo',)
    if sys.version_info > (3, 0):
        assert MyClass.foo is DummyMixinA.foo
    else:
        assert MyClass.foo.im_func is DummyMixinA.foo.im_func

    # create an object from the class
    o = MyClass()
    assert o.foo(1) == 2  # and not 3

    # check that DummyMixinB has been registered as a virtual parent class
    assert issubclass(MyClass, DummyMixinB)
    assert not issubclass(MyClass, DummyMixinA)


def test_apply_mixins_warning_none():
    """Checks that no warning is issued if the mixin class is correct"""

    if sys.version_info >= (3, 0):
        class DummyMixinAbcWithoutInit(ABC):
            pass

        with pytest.warns(None) as record:
            @apply_mixins(DummyMixinAbcWithoutInit)
            class MyClass:
                pass
        assert len(record) == 0

    class DummyMixinAbcWithoutInit(ABC):
        pass

    with pytest.warns(None) as record:
        @apply_mixins(DummyMixinAbcWithoutInit)
        class MyClass:
            pass
    assert len(record) == 0


def test_apply_mixins_warning_init():
    """checks that warning is issued in case an init method is present on the mixin class"""
    class DummyMixinWithInit(object):
        def __init__(self):
            pass

    with pytest.warns(MixinContainsInitWarning, match="contains an explicit `__init__` method"):
        @apply_mixins(DummyMixinWithInit)
        class MyClass(object):
            pass


# def test_apply_mixins_warning_abc():
#     """Checks that a warning is issued when the mixin class is not an ABC"""
#     class DummyMixinNotAbc(type):
#         pass
#
#     with pytest.warns(MixinNotRegisterableWarning, match="does not seem to be an ABC"):
#         @apply_mixins(DummyMixinNotAbc)
#         class MyClass(object):
#             pass


@pytest.mark.parametrize('read_first', [False, True], ids="read_first={}".format)
@pytest.mark.parametrize('type_', ['default_factory', 'default', 'mandatory'], ids="type_={}".format)
def test_field(read_first, type_):
    """Checks that field works as expected"""

    if type_ == 'default_factory':
        class Tweety:
            afraid = field(default_factory=lambda: False)
    elif type_ == 'default':
        class Tweety:
            afraid = field(default=False)
    elif type_ == 'mandatory':
        class Tweety:
            afraid = field()
    else:
        raise ValueError()

    # instantiate
    t = Tweety()

    if not read_first:
        # set
        t.afraid = False

    # read
    if read_first and type_ == 'mandatory':
        with pytest.raises(MandatoryFieldInitError):
            assert not t.afraid
    else:
        assert not t.afraid

    # set
    t.afraid = True
    assert t.afraid
