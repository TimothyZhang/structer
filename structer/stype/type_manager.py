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



# -*- coding: utf-8 -*-
#import os, types, copy, ast, imp, inspect

#from structer import log

from structer import const, util
from clazz import Clazz
from composite_types import *
from attr_types import *
import editor_types

'''
Terminology
  AttrType: type of attributes. eg: int, float, list, ref, ...
  Attr: attribute. An attribute is composed of a name(str) and a type(AttrType).
  Object: is what we want to edit. In a MMORPG, each monster, or each buff is an object.
  Clazz: object type. Eg: Monster, Skill, NPC, Buff  
'''

class TypeManager(object):
    def __init__(self):
        # name -> ObjectType
        self._clazzes = {}
#         self._enums = {}
#         self._structs = {}
#         self._unions = {}
        
    def get_clazzes(self):
        #for k,v in self._clazzes.iteritems():
        #    yield k,v
        return self._clazzes.values()
    
    def get_clazz_by_name(self, name):
        return self._clazzes.get(name)
    
    def get_struct_by_name(self, name):
        return self._parsed_structs.get(name)
    
    def load_editor_types(self):        
        for _, v in vars(editor_types).iteritems():
            if isinstance(v, Clazz):
                self._clazzes[v.name] = v
            
    def load_types(self, project):
        """ project: project of "Type Project" """
        
        self._parsed_enums = {}
        self._parsed_unions = {}
        self._parsed_structs = {}
        
        try:
            clazze_objs = project.object_manager.get_objects(editor_types.CLAZZ_NAME_CLAZZ)        
            for clazz_obj in clazze_objs:
                atstruct, data = clazz_obj.clazz.atstruct, clazz_obj.raw_data
                
                
                #struct = self._parse_struct(data, project, False)
                name = data['name']
                attrs = self._parse_struct_attrs(data['attrs'], project)
                exporter = data.get('exporter', u'')
#                 # Add reserved attrs: tags & export
#                 attrs.insert(0, Attr('tags',   ATList(ATStr(1), unique=True), 'TAGS') )                
#                 attrs.insert(0, Attr('export', ATBool(0), 'export?') )
#                 
#                 # move "name" & "id" to front
#                 for attr_name in ['name', 'id']:
#                     for attr in attrs:
#                         if attr.name == attr_name:
#                             attrs.remove(attr)
#                             attrs.insert(0, attr)
#                             break                        
                
                struct = Struct(name, attrs, exporter=exporter) 
                clazz = Clazz(ATStruct(struct))
                
                # extra settings
                clazz.unique_attrs = clazz_obj.get_attr_value('unique_attrs',)
                #clazz.name_attr = atstruct.get_attr_value('name_attr')
                clazz.max_number = clazz_obj.get_attr_value('max_number')
                clazz.min_number = clazz_obj.get_attr_value('min_number')
                                
                icon = clazz_obj.get_attr_value('icon')
                if icon:
                    # icon path is relative to editor project root
                    icon = util.normpath(icon)
                    if not os.path.isabs(icon):
                        icon = util.normpath( os.path.join(const.PROJECT_FOLDER_TYPE, icon) )                        
                    clazz.icon = icon
                
                self._clazzes[clazz.name] = clazz
        finally:
            #del self._parsed_enums
            #del self._parsed_unions
            #del self._parsed_structs
            pass
        
    def get_enums(self):
        return self._parsed_enums.values()
    
    def get_unions(self):
        return self._parsed_unions.values()
    
    def _parse_type(self, type_data, project):
        '''Generate AttrType from type_data
    
        Args:
            type_data: value of ATUnion(editor_types.u_type)           
            project: project of "Editor Project"
    
        Returns:
            AttrType
        '''
        #print '_parse_type', type_data
        type_name = type_data[0]
        type_type = editor_types.u_type.get_atstruct(type_name)
        
        if type_type == editor_types.s_predefined_type:
            val = type_type.get_attr_value("predefined_type", type_data[1], project)
            obj = project.object_manager.get_object(val)
            data = obj.get_attr_value("predefined_type")
            #print '>>>', data
            return self._parse_type(data, project)
        
        class_args = {}        
        #if type_name == 'List' and u'element_type' not in type_data[1]:
        #    type_data[1]['element_type'] = type_data[1]['type']
        
        for attr in type_type.struct.iterate():
            val = type_type.get_attr_value(attr.name, type_data[1], project)
                        
            #if type_name == 'List':
            #    if attr.name == 'element_type':
            #        if val is None:
            #            val = type_type.get_attr_value('type', type_data[1], project)
            
            if type(attr.type) is ATRef: 
                ref = project.object_manager.get_object(val, attr.type.clazz_name)
                if ref:
                    if attr.type.clazz_name == editor_types.CLAZZ_NAME_CLAZZ:
                        val = ref.name
                    elif attr.type.clazz_name == editor_types.CLAZZ_NAME_STRUCT:                    
                        val = self._parse_struct(ref, project)
                    elif attr.type.clazz_name == editor_types.CLAZZ_NAME_ENUM:
                        val = self._parse_enum(ref, project)
                    elif attr.type.clazz_name == editor_types.CLAZZ_NAME_UNION:
                        val = self._parse_union(ref, project)
                else:
                    log.error("ref to %s is None: %s", attr.type.clazz_name, val)
                    return None
            elif attr.type.name == editor_types.atu_type.name: 
                #attr.type, 
                val = self._parse_type(val, project)
            
            
            class_args[attr.name] = val
        
        attr_type_class = globals()['AT%s'%type_name]
        
        #try:
        return attr_type_class(**class_args)
        #except Exception, e:
        #    print '>>>:',type_name
        #    raise
    
    def _parse_struct(self, struct_def_data, project, cache=True):
        struct_name = struct_def_data['name']
        
        if cache:
            if struct_name in self._parsed_structs:
                return self._parsed_structs[struct_name]
        
        attrs = self._parse_struct_attrs(struct_def_data['attrs'], project)
        str_template = struct_def_data['str_template']
        exporter = struct_def_data['exporter']
        struct = Struct(struct_name, attrs, str_template=str_template, exporter=exporter)
        
        if cache:
            self._parsed_structs[struct_name] = struct
        return struct 
    
    def _parse_struct_attrs(self, attrs_def_data, project):
        attrs = []
        for attr_def in attrs_def_data:
            attr_type = self._parse_type(attr_def['type'], project)           
            attrs.append( Attr(attr_def['name'], attr_type, attr_def['description']) )
        
        return attrs     
    
    def _parse_enum(self, enum_obj, project):
        ''' 
        Args:
            enum_obj: object of editor_types.clazz_enum
        
        Returns:
            Enum
        '''
        
        enum_name = enum_obj.get_attr_value('name')
        if enum_name in self._parsed_enums:
            return self._parsed_enums[enum_name]
        
        # [{'name':, 'value':}, ...]
        items = enum_obj.get_attr_value('items')
        # [[name,value], ...]
        items = [[item['name'],item['value'], item.get('label', item['name'])] for item in items]
        
        export_names = enum_obj.get_attr_value('export_names')
        convert_to_int = enum_obj.get_attr_value('convert_to_int')
                
        enum = self._parsed_enums[enum_name] = Enum(enum_name, items, export_names, convert_to_int=convert_to_int)
        return enum     
    
    def _parse_union(self, union_obj, project):
        union_name = union_obj.get_attr_value("name")
        if union_name in self._parsed_unions:
            return self._parsed_unions[union_name]
        
        # [{'name':,'value':,'attrs':}, ...]
        items = union_obj.get_attr_value("items")
        
        # [[Struct, value], ...]
        structs = []  
        for item in items:            
            attrs = self._parse_struct_attrs(item['attrs'], project)
            str_template = item.get('str_template', u'')
            exporter = item.get('exporter', u'')
            struct = Struct(item['name'], attrs, str_template=str_template, label=item.get('label'), exporter=exporter)
            structs.append( [ATStruct( struct ), item['value']] )
        
        export_names = union_obj.get_attr_value('export_names')
        convert_to_int = union_obj.get_attr_value('convert_to_int')
        union = self._parsed_unions[union_name] = Union(union_name, structs, export_names=export_names, convert_to_int=convert_to_int)
        
        return union
        
    def dump(self):
        print 'Clazzes:'
        for n, c in self._clazzes.iteritems():
            print '   ', n, c
                
def test():
    tm = TypeManager()
    tm.load_editor_types()
    tm.dump()

if __name__ == '__main__': 
    test()

