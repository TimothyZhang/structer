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

from structer import log
from attr_types import AttrVerifyLogger, verify_list_unique_attrs
from collections import Counter

#from composite_types import Struct
#from attr_types import ATStruct

class Clazz(object):
    '''Holds all the informations of the type of an object.
    
    Attributes:
        uique_attrs: list of str, attribute names. These attribute values must be unique among all instances.
        name_attr: attribute name. This attribute value if used to be the display name of an object. default is "name"
        max_number: max number of objects of this Clazz. default is 0x7FFFFFFF        
        min_number: min number of objects of this Clazz. default is 0
    '''
    def __init__(self, atstruct):
        self.__atstruct = atstruct
                
        self.unique_attrs = []        
        self.name_attr = 'name'
        self.max_number = 0x7FFFFFFF
        self.min_number = 0        
        self.icon = 'icons/object.png'
    
    @property
    def atstruct(self):
        return self.__atstruct
    
    @property
    def name(self):
        return self.__atstruct.struct.name
    
    def verify(self, project, vlog = None):
        if vlog==None:
            vlog = AttrVerifyLogger('/Clazz/%s'%self.name)
            
        objects = project.object_manager.get_objects(self)
        
        # number limit
        if len(objects) > self.max_number:
            vlog.error("%s number exceeds limit: %s/%s", self.name, len(objects), self.max_number)
        if len(objects) < self.min_number:
            vlog.error("insufficient number of %s: %s/%s", self.name, len(objects), self.min_number)
        
        # unique attrs
        val = [obj.raw_data for obj in objects]
        verify_list_unique_attrs(self.atstruct, self.unique_attrs, val, project, vlog)        
        return vlog        


class Object(object):
    def __init__(self, project, clazz, uuid, data=None):
        '''clazz: type of this object
           data:  holds all attributes of this object, or None if it's a new object
        '''
        self.__project = project
        self.__clazz   = clazz
        self.__uuid    = uuid
        
        # How many errors this object has? Should be refreshed when this object changes or any objects referenced
        # by this object changes 
        self.__error_count = 0
        
        if data is None:  # init with default value
            self.__data = self.clazz.atstruct.get_default(project)
        else:             # load value
            # assert type(data) is dict
            self.__data = data
            #self.raw_data = data            
        
    def has_error(self):
        return self.__error_count > 0
    
    @property
    def project(self):
        return self.__project
    
    @property
    def clazz(self):
        return self.__clazz
    
    @property
    def atstruct(self):
        return self.__clazz.atstruct
    
    @property
    def struct(self):
        return self.__clazz.atstruct.struct

    @property
    def uuid(self):
        return self.__uuid
    
    @property
    def name(self):
        struct = self.struct
        
        name = ''

        if struct.has_attr(self.clazz.name_attr):        
            name = self.get_attr_value(self.clazz.name_attr)
                                    
            if type(name) is dict:
                name = name.get(self.project.default_language, self.uuid)
                
        if not name:
            if struct.has_attr('id'):
                id_ = self.get_attr_value("id")
                name = '%s<%s>' % (self.clazz.name, id_)
         
        if not name:                    
            name = '%s<>' % self.clazz.name
                
        return name

    def get_label(self):
        if self.atstruct.str_template:
            return self.atstruct.str(self.__data, self.project)

        return self.name
    
    @property
    def id(self):
        struct = self.struct
        if struct.has_attr('id'):
            id_ = self.get_attr_value('id')
            return id_
        return None            
    
    @property
    def raw_data(self):
        return self.__data
    
    @raw_data.setter
    def raw_data(self, data):
        self.__data = data
        self._check_data()
            
    def export(self):
        return self.atstruct.export(self.__data, self.project)
    
    def verify(self):
        return self._check_data()
        
    def _check_data(self):
        vlog = AttrVerifyLogger(u'', self.uuid)
        self.clazz.atstruct.verify(self.__data, self.project, vlog=vlog)
        vlog.log_all(self.project)
        
        self.__error_count = len(vlog.errors)
        return vlog
    
    def check_data(self):
        prev = self.__error_count
        self._check_data()
        
        if prev != self.__error_count:
            #todo: post an change event
            pass               
    
    def has_attr(self, name):
        return self.atstruct.has_attr(name)
    
    def get_attr(self, name):
        '''return Attr'''
        return self.atstruct.get_attr(name)
    
    def get_attr_value(self, name, default=None):
        val = self.atstruct.get_attr_value(name, self.__data, self.project)
        if val is None:
            val = default
        return val
    
    def __getitem__(self, name):
        return self.get_attr_value(name)
    
    def set_attr_value(self, name, val):
        #todo: need to call atstruct.set_attr_value ?
        self.__data[name] = val
        
    def __setitem__(self, name, val):
        self.__data[name] = val
    
    def get_refs(self):
        return self.atstruct.get_refs(self.__data, self.project)
    
    def fix(self, fixer):
        old = copy.deepcopy(self.raw_data)
        new = self.atstruct.fix(self.raw_data, fixer, self.project)
        if old != new:
            self.raw_data = new
            self.project.save_object(self)
            log.info('fixed: %s', self.name) 
        
#     def iter_attrs(self):
#         '''yield [Attr, value]'''
#         for attr in self.__clazz.iterate():
#             yield attr, self.__data[attr.name]
#             
#     def get_value(self, name):
#         return self.__data[name]
    
    
if __name__=='__main__':
    Object(None,None,'123',{})    
