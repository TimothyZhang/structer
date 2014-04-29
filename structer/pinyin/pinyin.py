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


import os, types, zipfile, traceback, string, itertools

def is_alpha_or_digit(s):
    '''Returns True if each char of "s" is either ascii letter or digit'''
    for i in s:
        if (i in string.ascii_letters) or (i in string.digits):
            continue
        return False
    return True

class Pinyin(object):
    '''Gets the FLP(first letter of pinyin) of each characters of a string
        
    For speed reason, the result will be cached.
    '''
    
    def __init__(self, cache_size=99999):
        '''
        Args:
            cache_size: how many strings to cache? -1 means infinite
        ''' 
        self._cache_size = cache_size
        
        # str -> [FLPs, ...], First letters of each characters
        self._cache = {}
        self._load_pinyin_data()
    
    def _load_pinyin_data(self):
        # chinese char -> first letterS of its pinyin
        self._char2pinyin = {}
        
        try:
            #print __file__
            path = os.path.join(os.path.split(__file__)[0], 'pinyin.zip')
            file_ = zipfile.ZipFile(path)            
            data = file_.read('py_utf8.txt').split("\n")
            for item in data:
                if item:
                    pinyin, chars = item.split(':')
                    chars = chars.decode('utf-8')
                    for char in chars:      
                        if char in self._char2pinyin:
                            if pinyin[0] not in self._char2pinyin[char]:
                                self._char2pinyin[char] += pinyin[0]
                        else:
                            self._char2pinyin[char] = pinyin[0]
        except Exception, e:
            traceback.print_exc()
    
    def __getitem__(self, text):
        r = self._cache.get(text)
        if r is not None:
            return r
        
        try:
            assert type(text) is types.UnicodeType
                                    
            pylist = []
            for uc in text:
                if uc in self._char2pinyin:
                    pylist.append( self._char2pinyin[uc] )
                elif is_alpha_or_digit(uc):
                    pylist.append( str(uc.lower()) )
                else:
                    # chinese char not found, use a question mark
                    pylist.append( '?' )                    
                
            results = [''.join(i) for i in itertools.product(*pylist)]
            if self._cache_size>=0 and len(self._cache) >= self._cache_size:
                try:           
                    self._cache.popitem()
                except: pass
            self._cache[text] = results
            return results
        except:
            traceback.print_exc()
            return []

_PINYIN = Pinyin()

def get_pinyin(text):
    return _PINYIN[text]
    
if __name__ == '__main__':
    #py = Pinyin()
#    print PINYIN._char2pinyin[u'长']    
#    print PINYIN[u'媃a']
#    #import re
#    #print re.match('.A', 'BA')
#    print PINYIN[u'长A长']
#    print PINYIN[u'原棘NPC']
#    print PINYIN[u'村长']
    print get_pinyin(u'很好很强大ab123')
    print 'hehe'
