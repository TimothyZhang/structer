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


import copy
# from structer.stype.clazz import Object
from structer.stype.attr_types import ATList
from structerui import log

from undo import UndoManager


class EditorContext(object):
    """Holds all the informations need by an editor.
    
    Attributes:
        attr_type: instance of AttrType
        attr_data: value to be edited
    """
    def __init__(self, project, attr_type, attr_data, undo_manager, read_only=False):
        self._project = project
        self._attr_type = attr_type
        self._old_data = copy.deepcopy(attr_data)
        self._attr_data = attr_data
        
        self._undo_manager = undo_manager
        self._read_only = read_only

        # if value is None, do not edit
        self.freeze_none = False

    @property
    def undo_manager(self):
        return self._undo_manager
    
    @property
    def read_only(self):
        return self._read_only
    
    @property
    def project(self):
        return self._project

    @property
    def attr_type(self):
        return self._attr_type
    
    @property
    def attr_data(self):
        return self._attr_data
    
    @attr_data.setter
    def attr_data(self, value):
        self._attr_data = value
    
    def is_modified(self):
        return self._attr_type.compare(self._old_data, self._attr_data) != 0
        # return self._undo_manager.is_modified()
    
    def get_title(self):
        return self._attr_type.name
    
    def create_sub_context(self, attr_type, attr_data):
        return EditorContext(self._project, attr_type, attr_data, self.undo_manager, self.read_only)


# todo: rename to RootEditorContext?
class FrameEditorContext(EditorContext):
    def __init__(self, project, objects, readonly=False):
        """
        Args:
            objects: can be one object, or a list of objects
        """
        
        if type(objects) is list:
            self._objects = dict([(obj.uuid, obj) for obj in objects])
            clazz = objects[0].clazz
            attr_type = ATList(clazz.atstruct, unique_attrs=clazz.unique_attrs)
            attr_data = []
            for obj in objects:
                data = copy.deepcopy(obj.raw_data)
                # use this hidden value to locate which object this data belongs to
                data['__uuid__'] = obj.uuid
                attr_data.append(data)
        else:
            self._objects = objects            
            clazz = objects.clazz
            attr_type = clazz.atstruct
            attr_data = copy.deepcopy(objects.raw_data)
        
        self.clazz = clazz
        EditorContext.__init__(self, project, attr_type, attr_data, UndoManager(), readonly)
    
#     @property
#     def objects(self):
#         return self._objects
    def is_batch(self):
        return type(self._objects) is dict
        
    def contains_object(self, obj):
        if self.is_batch():
            return obj.uuid in self._objects
        
        return obj == self._objects 
    
    def check_save(self):
        """Check uuid changes before saving
        
        Returns:
            (new_uuids, delete_uuids). 
            new_uuids is a list of uuids which are going to be created when saved
            delete_uuids is a list of uuids which are going to be deleted when saved
        """
        
        if not self.is_batch():
            return [], []
        
        objects = copy.copy(self._objects)
        new = []
        for data in self.attr_data:
            uuid = data.get('__uuid__')
            if uuid:  # existing obj                
                objects.pop(uuid)                        
            else:  # new obj
                new.append(uuid)
                                            
        delete = objects.keys()
        return new, delete
    
    def is_modified(self):        
        cmp_ = self.clazz.atstruct.compare
        
        if self.is_batch():
            if len(self._objects) != len(self.attr_data):
                return True
            for data in self.attr_data:
                uuid = data.get('__uuid__')
                obj = self._objects.get(uuid)
                if not obj:
                    return True
                if cmp_(data, obj.raw_data) != 0:
                    return True            
            return False
        
        else:
            return cmp_(self.attr_data, self._objects.raw_data) != 0
    
    def save(self):
        """Save all datas

        Returns:
            True/False
        """
        success = True
        if self.is_batch():
            new, delete = self.check_save()
            if new or delete:
                msg = 'Are you sure to:\n'
                if new:
                    msg += "  Create %s %s(s)\n" % (len(new), self.clazz.name)
                if delete:
                    msg += " Delete %s %s(s)\n" % (len(delete), self.clazz.name)
                msg += "?"
                import wx
                if wx.MessageBox(msg, style=wx.YES_NO | wx.ICON_WARNING) == wx.NO:
                    return False                
                                    
            objects = copy.copy(self._objects)
            
            fs_node = self.project.fs_manager.get_node_by_uuid(objects.keys()[0])
            fs_folder = fs_node.parent
            
            for data in self.attr_data:
                uuid = data.get('__uuid__')
                data2 = copy.deepcopy(data)
                
                if uuid:  # existing obj
                    data2.pop('__uuid__')
                    obj = objects.get(uuid)                    
                    if obj:
                        objects.pop(uuid)

                        if self.clazz.atstruct.compare(data2, obj.raw_data) != 0:
                            obj.raw_data = data2
                            try:
                                self.project.save_object(obj)
                            except Exception, e:
                                log.alert(e, 'Failed to save %s', obj)
                                success = False
                    else:
                        log.alert('Internal error. Editing object not found: %s', uuid)
                        success = False
                else:  # new obj
                    try:
                        obj = self.project.create_object(fs_folder, self.clazz, data2)
                        self._objects[obj.uuid] = obj
                        data['__uuid__'] = obj.uuid
                    except Exception, e:
                        log.alert(e, "Failed to create object: %s", data2)
                        success = False                    
            
            # to be deleted
            for obj in objects.itervalues():
                try:
                    self.project.delete_object(obj)
                    self._objects.pop(obj.uuid)
                except Exception, e:
                    log.alert(e, "Failed to delete object: %s", obj)
                    success = False
                        
        else:
            obj = self._objects
            obj.raw_data = self.attr_data
            try:
                self.project.save_object(obj)
            except Exception, e:
                log.error(e, "Failed to save: %s", obj.uuid)
                success = False    
        
        return success
    
    def get_title(self):
        if self.is_batch():
            return 'Batch Edit %s' % self.clazz.name
        else:
            return self._objects.name
