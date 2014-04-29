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


import json
#from zipfile import ZipFile

class Exporter(object):
    def get_name(self):
        u'''Returns the name of current exporter'''
        return 'No name'
    
    def get_exported_wildcard(self):
        u'''Returns the wildcard of exported file, or None if export to a folder
        
        eg:  "Zip archive (*.zip)|*.zip" 
        '''
        return None

    def export(self, project, writefunc):
        raise
    

class DefaultExporter(Exporter):
    def __init__(self):
        pass
    
    def get_name(self):
        return "Default Exporter" 
    
    def get_exported_wildcard(self):
        return "Zip archive (*.zip)|*.zip"
    
    def export(self, project, writefunc): #, path):
        #zf = ZipFile(path, 'w')
        
        for clazz in project.type_manager.get_clazzes():            
            clazz_all = []
            for obj in project.object_manager.get_objects(clazz):
                clazz_all.append( obj.export() )
                
            data = json.dumps(clazz_all)
            writefunc('%s.json' % clazz.name, data)
        
        consts = []
        for enum in project.type_manager.get_enums():
            for name in enum.names:
                val = name if enum.export_names else enum.value_of(name)
                if type(val) is str or type(val) is unicode:
                    val = '"%s"' % val
                consts.append( ( ('%s_%s'%(enum.name, name)).upper(), val) )
                
        for union in project.type_manager.get_unions():
            enum = union.atenum.enum
            for name in enum.names:
                val = name if enum.export_names else enum.value_of(name)
                if type(val) is str or type(val) is unicode:
                    val = '"%s"' % val
                consts.append( (('%s_%s'%(union.name, name)).upper(), val) )
        
        consts_str = '\n'.join(['%s = %s'%(n,v) for n,v in consts])
        writefunc('consts.txt', consts_str)
        
        #zf.close()
