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

import fs_util
from structer.sql import parse_sql
from stype.clazz import *
from fs_manager import FSEvent


class ObjectManager(object):
    """Manages objects, separated by Clazz"""

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
        
    def load(self, vlog):
        for clazz in self.project.type_manager.get_clazzes():
            self._obj_map[clazz.name] = {}
        
        fsm = self.project.fs_manager
        for node in fsm.iter(False):
            if not fs_util.is_object(node):
                continue         
            
            try:
                obj = self._create_object(node, False)                                                
            except Exception, e:
                log.error(e, 'Failed to create object: %s', node.uuid)
                vlog.error('Failed to create object: %s(%s)', node.uuid, e)
            else:    
                # self.add_object(obj)
                self._obj_map[obj.clazz.name][obj.uuid] = obj
        
        # verify all
        for obj in self.iter_all_objects():
            # noinspection PyBroadException
            try:
                obj.verify()
            except Exception, e:
                import traceback
                traceback.print_exc()
                vlog.error('Failed to verify object: %s(%s)', obj.uuid, e)

        # update references
        for obj in self.iter_all_objects():
            self.project.ref_manager.update_references(obj, obj.get_refs())
        
        for node in fsm.walk(fsm.recycle, True):
            if not fs_util.is_object(node):
                continue
            
            try:
                obj = self._create_object(node, verify=False)                            
            except Exception, e:            
                log.warn('Failed to create recycled object: %s(%s)', node.uuid, e)
            else:            
                self._recycled_objects[obj.uuid] = obj                

    def _on_fs_create(self, evt):
        fs_node = evt.fs_node
        
        if fs_util.is_object(fs_node):
            obj = self._create_object(fs_node, verify=True)
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
        
        if fs_util.is_object(fs_node):
            object_ = self.get_object(fs_node.uuid)
            self.remove_object(object_)
            self._recycled_objects[object_.uuid] = object_
    
    def _on_fs_restore(self, evt):
        fs_node = evt.fs_node
        
        if fs_util.is_object(fs_node):
            object_ = self.get_object(fs_node.uuid)
            assert not object_

            object_ = self._recycled_objects.get(fs_node.uuid)
            object_.verify()
            # self._manage_object( object_ )
            self.add_object(object_)
    
    def _create_object(self, fs_node, verify=True):
        clazz_name = fs_util.get_object_clazz_name(fs_node)
        if not clazz_name:
            raise Exception('clazz name not found in fs_node: %s', fs_node.uuid)

        clazz = self.project.type_manager.get_clazz_by_name(clazz_name)
        if not clazz:
            raise Exception('%s Class "%s" not found: %s' % (self.project.name, clazz_name, fs_node.uuid))
            
        object_ = Object(self.project, clazz, fs_node.uuid, fs_node.data['data'])
        if verify:
            # todo: how to deal with verify result?
            object_.verify()
            
        return object_
        
    def add_object(self, object_):        
        self._obj_map[object_.clazz.name][object_.uuid] = object_        
        self.project.ref_manager.update_references(object_, object_.get_refs())

    def remove_object(self, obj):
        self._obj_map[obj.clazz.name].pop(obj.uuid)

        referents = copy.copy(self.project.ref_manager.get_referents(obj.uuid))
        self.project.ref_manager.update_references(obj, [])

        # all referents got an "invalid refenrence"
        for uuid_ in referents:
            referent = self.get_object(uuid_)
            referent.verify()
        
    def get_recycled_object(self, uuid):
        return self._recycled_objects.get(uuid)

    def get_object(self, uuid, clazz_or_name=None):
        """Gets an object by its Clazz or Clazz name, and its uuid.
            
        Args:
            uuid: str, uuid.
            clazz_or_name: Instance of Clazz, or name of Clazz. Optional            
            
        Returns:
            Instance of Object, might be None.
            
        Throws:
            KeyError: if clazz_or_name not exists.

        :rtype: Object
        """        
        if clazz_or_name is None:
            for objects in self._obj_map.itervalues():
                obj = objects.get(uuid)
                if obj:
                    return obj
            return
            
        if type(clazz_or_name) is Clazz:
            clazz_name = clazz_or_name.name
        else:
            assert type(clazz_or_name) is unicode, type(clazz_or_name)
            clazz_name = clazz_or_name
          
        # print '>>>', clazz_name, uuid
        return self._obj_map[clazz_name].get(uuid)
    
    def get_objects(self, clazz_or_name, filter_=None):
        """see iter_objects()"""
        return list(self.iter_objects(clazz_or_name, filter_))
    
    def iter_objects(self, clazz_or_name, filter_=None):
        """Gets an iterator of objects of a Clazz.
        
        Args:
            clazz_or_name: Instance of Clazz, or name of Clazz.
            filter_: a filter str, or a function.
                if str: see _parse_filter
                if function: obj, fs_node, project are passed as arguments 
        Returns:
            A iterator which returns instances of Object.
            
        Throws:
            KeyError: if clazz_or_name not exists.
        """
        if type(clazz_or_name) is Clazz:
            clazz_name = clazz_or_name.name
        else:
            assert type(clazz_or_name) is unicode
            clazz_name = clazz_or_name
            
        objects = self._obj_map[clazz_name].itervalues()
        return self._iter_objects(objects, filter_)
    
    def _iter_objects(self, objects, sql=None):
        if not sql:
            for obj in objects:
                yield obj
            return

        func = parse_sql(self.project, sql)

        errors = 0
        for obj in objects:
            try:
                if func(obj):
                    yield obj
            except Exception, e:
                errors += 1
                if errors < 10:
                    log.error(e, 'filter error')
                continue
        # todo: replace with verify logger
        if errors:
            log.error('%s errors while filtering', errors)
        return

    def iter_all_objects(self, sql=None):
        def iter_all():
            for clazz in self._obj_map.itervalues():
                for obj in clazz.itervalues():
                    yield obj

        return self._iter_objects(iter_all(), sql)
    
    def iter_objects_of_classes(self, clazz_names, sql=None):
        def iter_all():
            for clazz in self._obj_map.itervalues():
                if clazz.name in clazz_names:
                    for obj in clazz.itervalues():
                        yield obj
        
        return self._iter_objects(iter_all(), sql)

    def filter_objects(self, objects, sql=None):
        return self._iter_objects(objects, sql)