#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.

#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
import pytest

from mixture import apply_mixins, Field

from ..utils import ABC


@pytest.mark.parametrize('do_apply', [False, True], ids="do_apply={}".format)
def test_doc_basic(capsys, do_apply):

    class BarkerMixin:
        def bark(self):
            print("barking loudly")

    if not do_apply:
        class TweeterMixin:
            afraid = Field(default=False,
                           doc="""Status of the tweeter. When this is `True`, 
                           tweets will be lighter""")

            def tweet(self):
                how = "lightly" if self.afraid else "loudly"
                print("tweeting %s" % how)

        class MagicDuck(BarkerMixin, TweeterMixin):
            pass

    else:
        class TweeterMixin(ABC):
            afraid = Field(default=False)

            def tweet(self):
                how = "lightly" if self.afraid else "loudly"
                print("tweeting %s" % how)

        @apply_mixins(TweeterMixin)
        class MagicDuck(BarkerMixin):
            pass

        # a special field is set for monkeypatched members
        assert set(MagicDuck.__from_mixins__) == {'tweet', 'afraid'}

    # check the class
    assert issubclass(MagicDuck, BarkerMixin)
    assert issubclass(MagicDuck, TweeterMixin)

    # lets create a barking MagicDuck
    d = MagicDuck()
    d.bark()
    d.tweet()
    d.afraid = True
    d.tweet()
    assert isinstance(d, BarkerMixin)

    with capsys.disabled():
        out, err = capsys.readouterr()
        print(out)
        assert out == "barking loudly\ntweeting loudly\ntweeting lightly\n"
