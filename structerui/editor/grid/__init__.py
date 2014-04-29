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



'''
Simple types are edited in grid cells, while complicated types are edited in an individual grid in a new dialog 

Hierachy:

base_grid
    list_grid                # editor for general ATList(except ATList of ATStruct)
        struct_list          # editor for ATList of ATStruct  
    struct                   # editor for ATStruct 
        union                # editor for ATUnion
    
cell_editor: customized cell editors for each type
'''

from struct import StructGrid
from list_grid import ListGrid
from struct_list import StructListGrid
from union import UnionGrid
