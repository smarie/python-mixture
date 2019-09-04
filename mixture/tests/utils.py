#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2019. All right reserved.

try:
    from abc import ABC
except ImportError:
    from six import with_metaclass
    from abc import ABCMeta
    ABC = with_metaclass(ABCMeta, object)
