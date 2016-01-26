# -*- coding=utf-8 -*-

# Copyright 2014 Timothy Zhang(zt@live.cn).
#
# This file is part of Structer.
#
# Structer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Structer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Structer.  If not, see <http://www.gnu.org/licenses/>.


import os
import zipfile
import string
import itertools


def is_alpha_or_digit(s):
    """
    :param s: str
    :return: bool
        True if *ALL* characters in 's' are alphas or digits, otherwise False
    """
    for i in s:
        if (i in string.ascii_letters) or (i in string.digits):
            continue
        return False
    return True


class Pinyin(object):
    """
    Gets the FLP(first letter of pinyin) of each characters of a string.
    For speed reason, the result will be cached.

    ie: the FLP of "中国" is "zg", the first letters of "Zhong" and "Guo"
    """

    def __init__(self, cache_size=99999):
        """
        :param cache_size: int
            how many strings to cache? a value <= 0 means infinite
        """
        self._cache_size = cache_size

        # {str: [FLPs, ...]}
        self._cache = {}
        self._load_pinyin_data()

    def _load_pinyin_data(self):
        """
        Loads pinyin data for each chinese characters
        """

        # {chinese char: [FLP, ...]}
        # chinese characters might have multi pronunciations, so the value of each char is a list
        self._char_to_flps = {}

        path = os.path.join(os.path.split(__file__)[0], 'pinyin.zip')
        file_ = zipfile.ZipFile(path)
        data = file_.read('py_utf8.txt').split("\n")

        for item in data:
            if item:
                pinyin, chars = item.split(':')
                chars = chars.decode('utf-8')
                for char in chars:
                    if char in self._char_to_flps:
                        if pinyin[0] not in self._char_to_flps[char]:
                            self._char_to_flps[char] += pinyin[0]
                    else:
                        self._char_to_flps[char] = pinyin[0]

    def __getitem__(self, text):
        if not isinstance(text, unicode):
            assert isinstance(text, str), 'text should be str or unicode.'
            text = text.decode("utf-8")

        r = self._cache.get(text)
        if r is not None:
            return r

        pylist = []
        for uc in text:
            if uc in self._char_to_flps:
                pylist.append(self._char_to_flps[uc])
            elif is_alpha_or_digit(uc):
                pylist.append(str(uc.lower()))
            else:
                # chinese char not found, use a question mark
                pylist.append('?')

        results = [''.join(i) for i in itertools.product(*pylist)]
        if len(self._cache) >= self._cache_size > 0:
            self._cache.popitem()

        self._cache[text] = results
        return results


_PINYIN = Pinyin()


def get_pinyin(text):
    return _PINYIN[text]


if __name__ == '__main__':
    # py = Pinyin()
    #    print PINYIN._char_to_flps[u'长']
    #    print PINYIN[u'媃a']
    #    #import re
    #    #print re.match('.A', 'BA')
    #    print PINYIN[u'长A长']
    #    print PINYIN[u'原棘NPC']
    #    print PINYIN[u'村长']
    print get_pinyin(u'很好很强大ab123')
