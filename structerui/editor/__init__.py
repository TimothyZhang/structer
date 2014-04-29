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



'''All editing features here.

There're 3 types of editor:
    In-place editor for single object in Explorer
    Single object editor in new frame
    Multiple object editor in new frame

The key component is EditorPanel, which can be placed in Explorer, EditorFrame or EditorDialog 

The UI hierarchy of EditorPanel is:
    EditorPanel(BoxSizer)        
        Grid
            CellRenderer/CellEditor
        

context: stores data to be edit
frame:   edit an object, of a list of objects
dialog:  recusively edit complicated attributes
panel:   editor any kind of complicated attributes. can be put into frame or dialog
grid:    view and edit each attribute, by different editors/renderers
'''
