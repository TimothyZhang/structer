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



import wx
import wx.grid as grid

from structer.stype.attr_types import *

from base_grid import GridBase
from list_grid import ListGrid, ListTable
from structerui.editor.context import FrameEditorContext

class StructListTable(ListTable):
    def __init__(self, ctx):
        ListTable.__init__(self, ctx)
    
    @property
    def atstruct(self):    
        return self.attr_type.element_type
    @property
    def struct(self):
        return self.atstruct.struct
    
    def get_attr_type(self, row, col):
        attr = self.struct.get_attr_by_index(col)
        return attr.type

    def get_attr_value(self, row, col):
        attr = self.struct.get_attr_by_index(col)
        return self.atstruct.get_attr_value(attr.name, self.attr_data[row], self._ctx.project)        
    
    def GetNumberCols(self):        
        return self.struct.get_attr_count()
    
    def set_value(self, row, col, value):
        attr = self.struct.get_attr_by_index(col)
        self.attr_data[row][attr.name] = value
        
    def GetColLabelValue(self, col):
        attr = self.struct.get_attr_by_index(col)        
        return attr.name    

class StructListGrid(ListGrid):
    def __init__(self, parent, editor_context):
        ListGrid.__init__(self, parent, editor_context, StructListTable(editor_context))        
    
    def is_editing_objects(self):
        return type(self.editor_context) is FrameEditorContext
    
    def _cut(self):
        if self.is_editing_objects():
            wx.MessageBox("Operation not supported!")
            return
        
        ListGrid._cut(self)
        
    def insert(self, pos=-1, rows=1, add_undo=False):
        if self.is_editing_objects() and add_undo:
            # if wx.NO == wx.MessageBox("%s %s(s) will be created, continue?" % (rows, self.editor_context.clazz.name), style=wx.YES_NO | wx.ICON_WARNING):
            #    return
            pass
            
        ListGrid.insert(self, pos, rows, add_undo)
    
    def insert_copied(self, pos=-1):
        if self.is_editing_objects():
            attr_type_names, datas = self._get_clipboard()
            if attr_type_names and datas:
                if wx.NO == wx.MessageBox("%s %s(s) will be created, continue?" % (len(datas), self.editor_context.clazz.name), style=wx.YES_NO | wx.ICON_WARNING):
                    return  
        
        ListGrid.insert_copied(self, pos)
        
    def delete(self, pos=None, rows=None, add_undo=True):
        if self.is_editing_objects() and add_undo:
            if pos is None or rows is None:
                # selection block 
                block = self._get_selection_block()
                if not block:
                    wx.MessageBox("Invalid selection area", "Error")
                    return
                
                top,left,bottom,right = block
                
                pos = top
                rows = bottom - top + 1
                
            if wx.NO==wx.MessageBox("%s %s will be deleted, and can NOT undo!!!\nContinue?"%(rows, self.editor_context.clazz.name), style=wx.YES_NO|wx.ICON_WARNING):
                return
        
        ListGrid.delete(self, pos, rows)
        
        #todo: it'd be better to support undo
        if self.is_editing_objects() and add_undo:
            self.editor_context.undo_manager.clear()        
    
    
if __name__ == '__main__':
    pass    
