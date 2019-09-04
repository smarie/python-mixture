#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.
from mixture import apply_mixins

from .utils import ABC


def test_doc_basic(capsys):

    class BarkerMixin(ABC):
        def bark(self):
            print("barking loudly")

    @apply_mixins(BarkerMixin)
    class Duck:
        pass

    # check the class
    assert Duck.__from_mixins__ == ('bark', )
    assert issubclass(Duck, BarkerMixin)

    # lets create a barking duck
    d = Duck()
    d.bark()
    assert isinstance(d, BarkerMixin)

    with capsys.disabled():
        out, err = capsys.readouterr()
        print(out)
        assert out == "barking loudly\n"
