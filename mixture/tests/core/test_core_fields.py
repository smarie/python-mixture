#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.

from collections import Iterable

import pytest

from mixture import field, MandatoryFieldInitError


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
