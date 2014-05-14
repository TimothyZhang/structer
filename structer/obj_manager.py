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



import types, uuid

import const, fs_util
from stype.clazz import *
from pinyin import get_pinyin
from fs_manager import FSEvent

class ObjectManager(object):
    '''Manages objects, seperated by Clazz'''

    def __init__(self, project):        
        self.project = project
        
        # Two level dict: {clazz_name: {uuid: Object} }
        self._obj_map = {}
        
        # {uuid: Object}
        self._recycled_objects = {}
        
        self.project.event_manager.register(FSEvent.get_key_of(FSEvent.CREATE), self._on_fs_create)
        self.project.event_manager.register(FSEvent.get_key_of(FSEvent.MODIFY), self._on_fs_modify)
        self.project.event_manager.register(FSEvent.get_key_of(FSEvent.RECYCLE), self._on_fs_recycle)
        self.project.event_manager.register(FSEvent.get_key_of(FSEvent.RESTORE), self._on_fs_restore)
        
    def load(self):
        success = True
                
        for clazz in self.project.type_manager.get_clazzes():
            self._obj_map[clazz.name] = {}
        
        fsm = self.project.fs_manager
        for node in fsm.iter(False):
            if not fs_util.is_object(node):
                continue         
            
            obj = None
            try:
                obj = self._create_object(node, False)                                                
            except Exception, e:
                log.error(e, 'Failed to create object: %s', node.uuid)
                success = False
            else:    
                self.add_object(obj)
        
        # verify all
        for obj in self.iter_all_objects():
            obj.verify()                
        
        for node in fsm.walk(fsm.recycle, True):
            if not fs_util.is_object(node):
                continue
            
            try:
                obj = self._create_object(node, verify=False)                            
            except Exception, e:            
                log.warn('Failed to create recycled object: %s(%s)', node.uuid, e)
            else:            
                self._recycled_objects[obj.uuid] = obj                
        
        return success
    
    def _on_fs_create(self, evt):
        fs_node = evt.fs_node
        
        if fs_util.is_object( fs_node ): 
            obj = self._create_object( fs_node )
            self.add_object(obj)
    
    def _on_fs_modify(self, evt):
        fs_node = evt.fs_node
        
        if fs_util.is_object(fs_node):
            obj = self.get_object(fs_node.uuid, fs_util.get_object_clazz_name(fs_node))
            if obj:            
                self.project.ref_manager.update_references(obj, obj.get_refs())
            else:
                log.error('fs_node not in object manager: %s' % fs_node)
    
    def _on_fs_recycle(self, evt):
        fs_node = evt.fs_node
        
        if fs_util.is_object( fs_node ):
            object_ = self.get_object( fs_node.uuid )
            self.remove_object( object_ )    
            self._recycled_objects[ object_.uuid ] = object_        
    
    def _on_fs_restore(self, evt):
        fs_node = evt.fs_node
        
        if fs_util.is_object( fs_node ):
            object_ = self.get_object( fs_node.uuid )
            assert not object_
            
            object_ = self._recycled_objects.get( fs_node.uuid )
            object_.verify()
            self._manage_object( object_ )
    
    def _create_object(self, fs_node, verify=True):
        clazz_name = fs_util.get_object_clazz_name(fs_node)
        if not clazz_name:
            raise Exception('clazz name not found in fs_node: %s', fs_node.uuid)
            
        
        clazz = self.project.type_manager.get_clazz_by_name(clazz_name)
        if not clazz:
            raise Exception('%s Classs "%s" not found: %s' % (self.project.name, clazz_name, fs_node.uuid))            
            
        object_ = Object(self.project, clazz, fs_node.uuid, fs_node.data['data'])
        if verify:
            #todo: how to deal with verify result?
            object_.verify()
            
        return object_
        
    def add_object(self, object_):        
        self._obj_map[object_.clazz.name][object_.uuid] = object_        
        self.project.ref_manager.update_references(object_, object_.get_refs())

    def remove_object(self, obj):
        self._obj_map[obj.clazz.name].pop(obj.uuid)
        self.project.ref_manager.update_references(obj, [])
        
    def get_recycled_object(self, uuid):
        return self._recycled_objects.get(uuid)

    def get_object(self, uuid, clazz_or_name = None):      
        '''Gets an object by its Clazz or Clazz name, and its uuid.
            
        Args:
            uuid: str, uuid.
            clazz_or_name: Instance of Clazz, or name of Clazz. Optional            
            
        Returns:
            Instance of Object, might be None.
            
        Throws:
            KeyError: if clazz_or_name not exists.
        '''        
        if clazz_or_name is None:
            for objs in self._obj_map.itervalues():
                obj = objs.get(uuid)
                if obj:
                    return obj
            return
            
        if type(clazz_or_name) is Clazz:
            clazz_name = clazz_or_name.name
        else:
            assert type(clazz_or_name) is unicode, type(clazz_or_name)
            clazz_name = clazz_or_name
          
        #print '>>>', clazz_name, uuid
        return self._obj_map[clazz_name].get(uuid)
    
    def get_objects(self, clazz_or_name, filter_=None):
        '''see iter_objects()'''
        return list(self.iter_objects(clazz_or_name, filter_))
    
    def iter_objects(self, clazz_or_name, filter_=None):
        '''Gets an iterator of objects of a Clazz.
        
        Args:
            clazz_or_name: Instance of Clazz, or name of Clazz.
            filter_: a filter str, or a function.
                if str: see _parse_filter
                if function: obj, fs_node, project are passed as arguments 
        Returns:
            A iterator which returns instances of Object.
            
        Throws:
            KeyError: if clazz_or_name not exsits.
        '''
        if type(clazz_or_name) is Clazz:
            clazz_name = clazz_or_name.name
        else:
            assert type(clazz_or_name) is unicode
            clazz_name = clazz_or_name
            
        objects = self._obj_map[clazz_name].itervalues()
        return self._iter_objects(objects, filter_)
    
    def _iter_objects(self, objects, filter_):
        if not filter_:
            for obj in objects:
                yield obj
            return
            #return objects
        
        if type(filter_) is unicode:
            filter_ = self._parse_filter(filter_)
            for obj in objects:
                if self._filter(obj, filter_):
                    yield obj        
            return
        
        if type(filter_) is types.FunctionType:
            errors = 0
            for obj in objects:
                node = self.project.fs_manager.get_node_by_uuid(obj.uuid)                
                try:
                    if filter_(obj, node, self.project):
                        yield obj
                except Exception, e:
                    errors += 1
                    if errors < 10:
                        log.error(e, 'filter error')                                    
                    continue
            #todo: replace with verify logger
            if errors:
                log.error('%s errors while filtering', errors)
            return
        
        raise Exception('invaild filter: %s(type:%s)' % (filter_, type(filter_))) 
    
    def iter_all_objects(self, filter_=None):
        def iter_all():
            for clazz in self._obj_map.itervalues():
                for obj in clazz.itervalues():
                    yield obj
#         all_clazzes = (t.itervalues() for t in self._obj_map.itervalues())
#         itertools.chain(*all_clazzes)        
        return self._iter_objects(iter_all(), filter_)
        
    def _parse_filter(self, filter_):
        '''Parses filter string
        
        A filter string is consist of a keyword and an expression, sperated by a ' ',  the expression can be omitted.
        keyword is a string without space. Can be empty.
        expression should be a valid python expression, which can passed be eval() directly. all attricutes of objects
        can be referenced by the expression as globals()        
        
        eg:
            123                                # search by keyword "123"
            123; level>10 and power<100        # serache by keyword "123", restricted with expected level and power
            ; level<5                          # all objects whose level<5
        
        Args:
            filter_: filter string.
        
        Returns:
            A tuple, (keyword, expression)
        '''
        tmp = map(unicode.strip, filter_.split(u' ', 1))
        tmp[0] = tmp[0].lower()
        if len(tmp)==1:
            return tmp[0], None
        
        return tuple(tmp)
    
    def _filter(self, obj, filter_):
        '''Check whether the object satisfies the filter
        
        Args:
            obj: the object to be check
            filter_: A tuple: (keyword, expression)

        Returns:
            True if the objects satisfies the filter, otherwise False
        '''        
        keyword, expr = filter_
        
        if keyword:
            if not self._filter_keyword(obj, keyword):
                return False
        
        if expr:
            try:
                # print 'filter expr', expr, obj.raw_data
                r = eval(expr, {}, obj.raw_data)
                return bool(r)
            except:
                return False
        
        return True

    def _filter_keyword(self, obj, keyword):
        '''Check whether the given objects's name or id matches keyword
        
        If object name is a dict, each value will be checked. 
        
        Args:
            obj: instance of Object
            keyword: unicode
            
        Returns
            True if obj matches keyword
        '''
        # name
        if obj.struct.has_attr('name'):
            name = obj.get_attr_value('name')
            if type(name) is dict:
                for lang, n in name.iteritems():
                    if self._test_keyword(n.lower(), keyword, lang):
                        return True                    
            else:
                if self._test_keyword(name.lower(), keyword, None):
                    return True
                        
        # id
        if obj.id:
            if keyword in unicode(obj.id):
                return True
        
        # keyword search failed            
        return False
    
    def _test_keyword(self, str_, keyword, lang):
        '''Check whether str_ matches keyword
        
        We say it match if:
            str_ contains keyword, or
            first letter of pinyin str_ contains keyword, if lang is "cn" or None(language not specified) 
        
        Args:
            str_: unicode string to be tested
            keyword: unicode
            lang: language code. Can be None.
        
        Returns
            True if str_ matches keyword
        '''
        if keyword in str_:
            return True
        
        if lang == 'cn' or lang is None:
            for pinyin in get_pinyin(str_):
                if keyword in pinyin:
                    return True
        
        return False
    
    
