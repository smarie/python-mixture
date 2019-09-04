#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.
import pytest

from mixture import apply_mixins

from .utils import ABC


@pytest.mark.parametrize('use_inheritance', [False, True], ids="use_inheritance={}".format)
def test_doc_basic(capsys, use_inheritance):

    class BarkerMixin(ABC):
        def bark(self):
            print("barking loudly")

    if use_inheritance:
        class Duck(BarkerMixin):
            pass
    else:
        @apply_mixins(BarkerMixin)
        class Duck:
            pass

        # in that case a special field is set
        assert Duck.__from_mixins__ == ('bark',)

    # check the class
    assert issubclass(Duck, BarkerMixin)

    # lets create a barking duck
    d = Duck()
    d.bark()
    assert isinstance(d, BarkerMixin)

    with capsys.disabled():
        out, err = capsys.readouterr()
        print(out)
        assert out == "barking loudly\n"
