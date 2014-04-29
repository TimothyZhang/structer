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



import wx.grid as grid

from structer.stype.composite_types import Attr

from struct import StructGrid, StructTable

'''Union editor is much like a Struct editor, except its "struct attributes" are dynamicly
created according to union key.

The first row is union key, 
The second and belowing rows refers to attributes of the struct of that key.  

Once the first row(union key) changed, all the other rows are changed.
'''

class UnionTable(StructTable):
    def __init__(self, ctx):
        StructTable.__init__(self, ctx)
        
        # temporary attr for editing union key
        self._attr_key = Attr(u'name', self.atenum, u'the name of union item')
        
    @property
    def union(self):
        return self._ctx.attr_type.union
    
    @property
    def atenum(self):
        return self._ctx.attr_type.atenum
        
    @property
    def atstruct(self):
        key = self._ctx.attr_data[0]
        return self.union.get_atstruct(key)
    
    @property
    def struct(self):
        return self.atstruct.struct
        
    def get_attr_of_row(self, row):
        if row == 0:
            attr = self._attr_key
        else:
            if row-1 < self.struct.get_attr_count():
                attr = self.struct.get_attr_by_index(row-1)
            else:
                attr = None
        return attr
    
    def GetNumberRows(self):        
        return 1 + self.struct.get_attr_count()

    def get_value_of_col2(self, row):
        attr = self.get_attr_of_row(row)
            
        if row == 0:
            val = self._ctx.attr_data[0]
        else:
            val = self._ctx.attr_data[1].get(attr.name)        
        return val

    def set_value(self, row, col, value):
        if col != 2:
            return
        
        if row == 0:
            old = self._ctx.attr_data[0]
            if old != value:
                self._clear_rows()
                self._ctx.attr_data[0] = value
                self._ctx.attr_data[1] = self.atstruct.get_default(self._ctx.project)
                self._add_rows()
        else: 
            attr = self.struct.get_attr_by_index(row-1)
            self._ctx.attr_data[1][attr.name] = value        

    def _clear_rows(self):
        #self.GetView().ForceRefresh()
        msg = grid.GridTableMessage(self,          # The table
           grid.GRIDTABLE_NOTIFY_ROWS_DELETED,     # what we did to it
           1,                                      # from which row
           self.GetRowsCount()-1                   # how many
        )
                
        self.GetView().ProcessTableMessage(msg)
    
    def _add_rows(self):
        msg = grid.GridTableMessage(self,          # The table
           grid.GRIDTABLE_NOTIFY_ROWS_INSERTED,     # what we did to it
           1,                                      # from which row
           self.GetRowsCount()-1                   # how many
        )
                
        self.GetView().ProcessTableMessage(msg)
        
    #--------------------------------------------------
    # Some optional methods
    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        labels = ('Name', 'Type', 'Value', 'Description')
        return labels[col]


class UnionGrid(StructGrid):
    def __init__(self, parent, editor_context):
        StructGrid.__init__(self, parent, editor_context, UnionTable(editor_context))
                
