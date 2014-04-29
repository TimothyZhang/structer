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



# coding=utf-8
import copy

from structer import log

class Event(object):
    def get_keys(self):
        '''Get all event keys to notify
        
        Returns:
            a list of keys, each key is a tuple.
        '''
        raise NotImplemented
    
    def create_sliced_keys(self, full_key):
        '''Create keys by sub slicing full_key.
        
        eg: 
            create_sliced_keys( (1,2,3) ) returns [(1,2,3), (1,2), (1,)]
        
        Args:
            full_key a tuple
        
        Returns:
            a list of tuple, whose elements are subsets of full_key
        '''
        return [tuple(full_key[:i]) for i in xrange(len(full_key),0,-1)]
    
#     @classmethod 
#     def _create_register_key(self, cls, list_):        
#         list_ = list(list_)[:]        
#         list_.insert(0, cls.EVT_PREFIX)
#         list_ = filter(lambda x:x != None, list_)
#         return tuple(list_)
        
class EventManager(object):
    def __init__(self):
        self._listeners = {}

    def register(self, event_key, call_back):
        self._listeners.setdefault(event_key, set()).add(call_back)        
        
    def process(self, evt):
        keys = evt.get_keys()
        
        for key in keys:
            call_backs = self._listeners.get(key)
            
            # todo other complicated situations
            if call_backs:
                call_backs = copy.copy(call_backs)                        
                for call_back in call_backs:
                    try:
                        call_back(evt)
                    except Exception, e:
                        log.error(e, 'error in callback: %s', key)

    def unregister(self, event_key, call_back):
        call_backs = self._listeners.get(event_key)
        if call_backs:
            call_backs.discard(call_back)           



