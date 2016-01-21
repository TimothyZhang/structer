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



import const
from stype.clazz import Clazz, Object

def is_object(fs_node):
    return not fs_node.is_folder() and fs_node.file_type == const.FILE_TYPE_OBJECT

def is_filter(fs_node):
    return not fs_node.is_folder() and fs_node.file_type == const.FILE_TYPE_FILTER

def get_object_clazz_name(fs_node):
    return fs_node.data['clazz']

def generate_file_data_by_object(obj):
    return {'clazz': obj.clazz.name, 'data': obj.raw_data}

def generate_file_data_by_clazz(project, clazz, data=None):
    if data is None:
        data = clazz.atstruct.get_default(project)
    return {'clazz': clazz.name, 'data': data}    

def get_object_path(project, obj):
    node = project.fs_manager.get_node_by_uuid(obj.uuid)
    return node.parent.path + u'/' + obj.name
    
