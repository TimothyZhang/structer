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



#coding=utf-8
'''
Created on 2013-11-21

@author: Administrator
'''
import os
import traceback
import json

import const
from stype import editor_types
from stype.type_manager import TypeManager
from stype.attr_types import ATInt, ATUnion

from fs_manager import FileSystemManager
import fs_util
from ref_manager import RefManager
from obj_manager import ObjectManager
from event_manager import EventManager

import log, util


class Project(object):
    '''Holds all information of a project.
    
    Attributes:
        path: Path of project root.
        is_type_editor: bool. True if the project is used by type editor, load types from editor_types.py
        auto_create_clazz_folder: automaticly creates a folder for each clazz under root
         
        type_manager: An instance of TypeManager, which holds all Clazz infos.
        fs_manager: An instance of FileSystemManager
        ref_manager: An instance of RefManager, which manages all relations between all objects.
    '''    
    def __init__(self, root, is_type_editor):
        '''
        Args:
            root: path of project root folder
            is_type_editor: bool. see class docstring                
        '''
        self.path = util.normpath(os.path.abspath(root))
        self.is_type_editor = is_type_editor        
        self._auto_create_clazz_folder = True
        
        # Must be the first
        self.event_manager = EventManager()        
        self.type_manager = TypeManager()        
        self.fs_manager = FileSystemManager(self, os.path.join(self.path, const.PROJECT_FOLDER_DATA) )
        # should after fs_manager
        self.object_manager = ObjectManager(self)
        # should after object_manager
        self.ref_manager = RefManager()        
        
        #self._langauges = ('en', )
        self._default_language = 'en'
        self._translations = {}
        
        self.tags = set()
        
        self._next_ids = {}  # {clazz_name: next_id}
        self._has_error = False
        self._loaded = False
    
    @property
    def name(self):
        p = os.path.split(self.path)
        return p[-1]
        
    def load(self):
        ''' Load the project 
        Returns:
            True if it's a new project, otherwise False
        '''
        assert not self._loaded
        self._loaded = True
        self._has_error = False
        
        if self.is_type_editor:
            self.type_manager.load_editor_types()
                        
        else:
            self._editor_project = p = Project( os.path.join(self.path, const.PROJECT_FOLDER_TYPE), True )
            p.load()
            
            try:
                self.type_manager.load_types(p)
            except:
                traceback.print_exc()
                self._has_error = True
                                        
            # load setting
            setting_objs = p.object_manager.get_objects(editor_types.CLAZZ_NAME_SETTING)        
            if len(setting_objs)==1:
                setting_obj = setting_objs[0]                
                self._translations = dict( setting_obj.get_attr_value('translations') )
                self.tags = set(setting_obj.get_attr_value('tags',[]) )
                self.tags.add('export')
                self._auto_create_clazz_folder = setting_obj.get_attr_value('auto_create_clazz_folder')
            elif len(setting_objs)>1:
                log.error('too many Setting objects: %s', len(setting_objs))
            
        is_new = self.fs_manager.load()            
                
        if not self.object_manager.load():
            self._has_error = True         
        
        # todo: enable evt_manager here. previously events should be ignored.
                
        # Creates root folder for each Clazz, if it's a new project
        if self._auto_create_clazz_folder:
            for clazz in self.type_manager.get_clazzes():
                if not self.fs_manager.root.get_sub_folder_by_name(clazz.name):                    
                    self.fs_manager.create_folder(self.fs_manager.root, clazz.name)

        # Creates project file
        if is_new and not self.is_type_editor:
            proj = {'version': 2}
            open(os.path.join(self.path, const.PROJECT_FILE), 'wb').write(json.dumps(proj))
                
        return is_new
        
    def has_error(self, print_=False):
        '''todo: this method is slow!'''
        if self._has_error:
            print 'project error'
            return True
        
        if not self.is_type_editor:
            if self.get_editor_project().has_error(print_):
                print 'editor project error'
                return True
        
        for obj in self.object_manager.iter_all_objects():
            if obj.has_error():
                return True
            
        for clazz in self.type_manager.get_clazzes():
            vlog = clazz.verify(self)
            if vlog.has_error():
                if print_:  # this is ugly!                    
                    vlog.log_all(self)
                return True
        
        return False
    
    def get_editor_project(self):
        assert not self.is_type_editor
        return self._editor_project
        
    @property
    def default_language(self):
        return self._default_language
    
    def translate(self, text):
        '''Translates text with user defined translation dictionary in Setting''' 
        return self._translations.get(text, text)

    def get_object(self, uuid, clazz_or_name = None):        
        return self.object_manager.get_object(uuid, clazz_or_name)
    
    def get_object_by_fsfile(self, fs_file):
        return self.get_object( fs_file.uuid, fs_util.get_object_clazz_name(fs_file) )

    def create_object(self, folder, clazz, data=None):
        '''Creates a new object.
        
        Args:
            folder: where the new object should be
            clazz: type of new object
            data: data of new object, NOT node!. default values will be used if it's None
            
        Returns:
            Object
        '''
        
        # number limit      
        count = len(self.object_manager.get_objects(clazz))
        if count >= clazz.max_number:
            raise Exception(u'%s number reached max limit: %s' % (clazz.name, clazz.max_number))
                         
        file_data = fs_util.generate_file_data_by_clazz(self, clazz, data)
        file_ = self.fs_manager.create_file(folder, 'object', '', file_data )
        obj = self.object_manager.get_object(file_.uuid, clazz.name)
        
        # auto increase id if need
        next_id = self.next_object_id(clazz)
        if next_id != None:                    
            obj.set_attr_value('id', next_id)
            self.save_object(obj)
        return obj
        #return self.object_manager.create_object(clazz, file_.uuid)
        
    def next_object_id(self, clazz):
        """return next available id, or None if default value is Okay. """
        struct = clazz.atstruct.struct
        if not struct.has_attr('id'):
            return
            
        at = struct.get_attr_by_name('id').type
        if not (type(at) is ATInt and 'id' in clazz.unique_attrs):
            return
                
        next_id = self._next_ids.get(clazz.name)
        if next_id is None:            
            next_id = at.min                
            for obj2 in self.object_manager.iter_objects(clazz):
                id2 = obj2.get_attr_value('id')
                if id2 >= next_id:
                    next_id = id2+1
            self._next_ids[clazz.name] = next_id
                
        self._next_ids[clazz.name] += 1        
        return next_id            
    
    def save_object(self, obj):
        self.fs_manager.save_file(obj.uuid, fs_util.generate_file_data_by_object(obj))        
    
    def delete_object(self, obj):
        self.fs_manager.delete(obj.uuid)

    def fix_all(self, fixer):
        for obj in self.object_manager.iter_all_objects():
            obj.fix(fixer)
            
    def fix_struct_add_attr(self, struct_name=None, attr_name=None):
        from stype.attr_types import ATStruct
        struct_name = '%s@'%struct_name if struct_name else None

        def fixer(at, val, project):
            if type(at) is ATStruct and (not struct_name or at.name == struct_name):
                if attr_name: # specified attr
                    if val.get(attr_name) is None:
                        attr = at.get_attr(attr_name)
                        val[attr_name] = attr.type.get_default(project)
                else: # all missing attrs
                    for attr in at.struct.iterate():
                        if val.get(attr.name) is None:
                            val[attr.name] = attr.type.get_default(project)
                    
            return val
        self.fix_all(fixer)
        
    def fix_struct_reset(self, struct_name, attr_name):
        from stype.attr_types import ATStruct
        struct_name = '%s@'%struct_name

        def fixer(at, val, project):
            if type(at) is ATStruct and (at.name == struct_name):                                
                attr = at.get_attr(attr_name)
                val[attr_name] = attr.type.get_default(project)                
                    
            return val
        
        self.fix_all(fixer)
        
    def fix_struct_rename_attr(self, struct_name, new_name, old_name):
        from stype.attr_types import ATStruct
        struct_name = '%s@'%struct_name

        def fixer(at, val, project):
            if type(at) is ATStruct and (at.name == struct_name):                
                if val.get(new_name) is None and old_name in val:
                    val[new_name] = val[old_name]
                    del val[old_name]
            return val
        
        self.fix_all(fixer)        
    
    def fix_struct_attr(self, struct_name, attr_name, func):
        '''fix attr of struct by provided func
            
            func(name, oldval, type, project) -> newval
        '''
        from stype.attr_types import ATStruct
        struct_name = '%s@'%struct_name

        def fixer(at, val, project):
            if type(at) is ATStruct and (at.name == struct_name):
                val[attr_name] = func(attr_name, val[attr_name], at, project)                
            return val
        
        self.fix_all(fixer)

    def fix_union_dict(self):
        def fixer(at, val, project):
            if isinstance(at, ATUnion) and isinstance(val, list):
                r = dict({'key': val[0]})
                r[val[0]] = val[1]
                return r
            return val

        self.fix_all(fixer)
                
if __name__ == '__main__':
    p = Project("c:\\test", False)
    p.load()


