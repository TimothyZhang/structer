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


import string
      
class Attr(object):
    def __init__(self, name, attr_type, description=''):
        self.name = name        
        self.type = attr_type        
        self.description = description  
        
class Enum(object):
    def __init__(self, name, items, export_names=False, convert_to_int=False):
        ''' item: [[name(str), value(int), label(str)], ...] or [[name(str), value(int)], ...]'''
        self.name = name
        assert len(items)>0, u'Enum %s has no item'%name
                
        self.__names = [item[0] for item in items]
        
        self.__name2values = {}
        self.__value2names = {}
        self.__name2labels = {}
        self.__label2names = {}

        for item in items:
            self.add_item(item)
            
        self._export_names = export_names
        self._convert_to_int = convert_to_int
        
    def add_item(self, item):
        if len(item) == 2:
            n, v = item
            l = n
        else:
            n, v, l = item
            
        self.__name2values[n] = v
        self.__value2names[v] = n
        self.__name2labels[n] = l
        self.__label2names[l] = n
    
    @property
    def convert_to_int(self):
        return self._convert_to_int
    
    @property
    def export_names(self):
        return self._export_names
    
    @property
    def names(self):
        return self.__names
    
    @property
    def labels(self):
        return [self.label_of(name) for name in self.__names]
    
    def has_name(self, name):
        return name in self.__name2values
    
    def value_of(self, name):
        val = self.__name2values[name]
        if self.convert_to_int:            
            val = int(val)            
        return val        
            
    def has_value(self, value):
        return value in self.__value2names
    
    def name_of(self, value):
        if self.convert_to_int:
            return self.__value2names[value]
        return value
    
    def label_of(self, name):
        l = self.__name2labels.get(name)
        if not l:
            l = u'Invalid: %s'%name
        return l
    
    def name_of_label(self, label):
        n = self.__label2names.get(label)
        if not n:
            n = ''
        return n
    
    def get_name_by_index(self, index):
        return self.__names[index]
       
                
class Struct(object):
    def __init__(self, name, attrs, str_template = u"", label=u'', exporter= u'', verifier=u''):
        ''' attrs: [Attr, ...] '''
        self.name = name
        self.label = label if label else name
        
        self._str_template = string.Template(str_template) if str_template else None
        self.exporter_str = exporter
        self.verifier_str = verifier
        
        self.__attrs = attrs        
        self.__attr_map = {}
        for attr in attrs:
            self.__attr_map[attr.name] = attr
    
    @property
    def str_template(self):
        return self._str_template
    
    def get_attr_count(self):
        return len(self.__attrs)
    
    def get_attr_by_index(self, index):
        return self.__attrs[index]
    
    def get_attr_by_name(self, name):
        return self.__attr_map[name]
    
    def has_attr(self, name):
        return name in self.__attr_map
    
    def iterate(self):
        return iter(self.__attrs)
    

class Union(object):
    def __init__(self, name, structs, export_names = False, convert_to_int=False):
        ''' structs: [[ATStruct, value], ...]'''
        self.name = name
        self._export_names = export_names
        self._convert_to_int = convert_to_int
                
        self.set_structs(structs)
        
    @property
    def convert_to_int(self):
        return self._convert_to_int
    
    @property
    def export_names(self):
        return self._export_names   
    
    def set_structs(self, structs):
        #self.__structs = structs
        self.__structs_map = {}
        
        enum_items = [] 
        for atstruct, value in structs:
            assert atstruct.struct.name not in self.__structs_map
            self.__structs_map[atstruct.struct.name] = atstruct
            enum_items.append( [atstruct.struct.name, value, atstruct.struct.label] )
            
        from attr_types import ATEnum
        self.enum = Enum('%s_keys'%self.name, enum_items, export_names=self.export_names, convert_to_int=self.convert_to_int)
        self.__at_enum = ATEnum(self.enum) 
    
    @property
    def atenum(self):
        return self.__at_enum
    
    #@property
    #def atstructs(self):
        #return self.__structs
    
    def get_atstruct(self, name):
        return self.__structs_map.get(name)
        
    def names(self):
        return self.__structs_map.keys()
    
    #def value_of(self, name):
    #    return self.__at_enum.enum.value_of(name) 
