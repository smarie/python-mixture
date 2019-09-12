#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.

from collections import Iterable

import pytest
from valid8.base import Failure

from mixture import field, MandatoryFieldInitError, UnsupportedOnNativeFieldError


@pytest.mark.parametrize('read_first', [False, True], ids="read_first={}".format)
@pytest.mark.parametrize('type_', ['default_factory', 'default', 'mandatory'], ids="type_={}".format)
def test_field(read_first, type_):
    """Checks that field works as expected"""

    if type_ == 'default_factory':
        class Tweety:
            afraid = field(default_factory=lambda: False, name='afraid')
    elif type_ == 'default':
        class Tweety:
            afraid = field(default=False, name='afraid')
    elif type_ == 'mandatory':
        class Tweety:
            afraid = field(name='afraid')
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


def test_type():
    """ Tests that when `type` is provided, it works as expected """

    class Foo(object):
        f = field(name='f', type=str)

    o = Foo()
    o.f = 'hello'
    with pytest.raises(TypeError) as exc_info:
        o.f = 1

    assert str(exc_info.value) == "Invalid value type provided for 'Foo.f'. " \
                                  "Value should be of type 'str'. " \
                                  "Instead, received a 'int': 1"


def test_validator():
    """ tests that `validator` functionality works correctly with several flavours of definition."""

    from valid8 import non_empty
    from valid8.entry_points import ValidationError

    # class EmptyError(ValidationError):
    #     help_msg = "h should be non empty"

    class EmptyFailure(Failure, ValueError):
        """ Custom Failure raised by non_empty """
        help_msg = 'len(x) > 0 does not hold for x={wrong_value}'

    class Foo2(object):
        f = field(name='f', type=str, validator=non_empty)

        g = field(name='g', type=str, validator=[non_empty])

        h = field(name='h', type=str, validator=[(non_empty, EmptyFailure),
                                                 non_empty,
                                                 (lambda obj, val: obj.f in val, "h should contain f"),
                                                 (lambda val: 'a' in val, "h should contain 'a'"),
                                                 (non_empty, "h should be non empty", EmptyFailure)])

        j = field(name='j', type=str, validator={non_empty: ("h should be non empty", EmptyFailure),
                                                 lambda obj, val: obj.f in val: "h should contain f",
                                                 "h should contain 'a'": lambda val: 'a' in val
                                                 })

    o = Foo2()
    o.f = 'hey'

    with pytest.raises(ValidationError):
        o.f = ''

    # o.h should be a non-empty string containing 'a' and containing o.f
    with pytest.raises(ValidationError) as exc_info:
        o.h = ''
    assert isinstance(exc_info.value.validation_outcome, EmptyFailure)

    with pytest.raises(ValidationError) as exc_info:
        o.h = 'hey'  # does not contain 'a'
    assert exc_info.value.validation_outcome is False

    with pytest.raises(ValidationError) as exc_info:
        o.h = 'a'  # does not contain 'hey'
    assert exc_info.value.validation_outcome is False

    o.h = 'hey ya'

    # same for j but with a different syntax
    with pytest.raises(ValidationError):
        o.j = ''

    with pytest.raises(ValidationError):
        o.j = 'hey'  # does not contain 'a'

    with pytest.raises(ValidationError):
        o.j = 'a'  # does not contain 'hello'

    o.j = 'hey ya'


def test_validator_not_compliant_with_native_field():
    """tests that `use_descriptor=False` can not be set when a validator is provided"""
    with pytest.raises(UnsupportedOnNativeFieldError):
        class Foo(object):
            f = field(name='f', validator=lambda x: True, use_descriptor=False)
