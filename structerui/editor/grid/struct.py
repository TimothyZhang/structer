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


from base_grid import *


class StructTable(TableBase):
    def __init__(self, ctx):
        TableBase.__init__(self, ctx)

        self._sort_by_attr_name = False
        self._attrs = list(self.struct.iterate())
               
    @property
    def atstruct(self):
        return self._ctx.attr_type
    
    @property
    def struct(self):
        return self._ctx.attr_type.struct

    def set_sort_by_attr_name(self, sort_):
        if sort_ == self._sort_by_attr_name:
            return

        if sort_:
            self._attrs.sort(key=lambda x: x.name)
        else:
            self._attrs = list(self.struct.iterate())

        self._sort_by_attr_name = sort_

    def is_sort_by_attr_name(self):
        return self._sort_by_attr_name

    def get_attr_by_index(self, index):
        return self._attrs[index]
    
    def get_attr_type(self, row, col):        
        if col == 2:
            attr = self.get_attr_of_row(row)
            return attr.type if attr else None
            # return self.struct.get_attr_by_index(row).type
    
    def get_attr_value(self, row, col):
        attr = self.get_attr_of_row(row)
        if col == 0:
            return attr.name            
        elif col == 1:
            return attr.type.name
        elif col == 2:
            return self.get_value_of_col2(row)            
        elif col == 3:
            return attr.description            
    
    def GetAttr(self, row, col, kind):
        """kind: Any, Cell, Row, Col"""
        if col != 2:
            return self._get_cell_attr("static_readonly")
        
        # return self._get_cell_attr("default")
        return TableBase.GetAttr(self, row, col, kind)

    # noinspection PyMethodOverriding
    def GetNumberRows(self):
        return self.struct.get_attr_count()

    # noinspection PyMethodOverriding
    def GetNumberCols(self):
        # name, type, value, description
        return 4
    
    def get_value_of_col2(self, row):
        attr = self.get_attr_by_index(row)
        return self.atstruct.get_attr_value(attr.name, self._ctx.attr_data, self._ctx.project)
    
    def get_attr_of_row(self, row):
        return self.get_attr_by_index(row)

    def set_value(self, row, col, value):
        if col != 2:
            return
        
        attr = self.get_attr_by_index(row)
        self._ctx.attr_data[attr.name] = value

    # noinspection PyMethodOverriding
    def GetColLabelValue(self, col):
        labels = ('Name', 'Type', 'Value', 'Description')
        return labels[col]


class StructGrid(GridBase):
    def __init__(self, parent, editor_context, table=None):
        if table is None:
            table = StructTable(editor_context) 
        GridBase.__init__(self, parent, table)
        
        self.Bind(grid.EVT_GRID_SELECT_CELL, self.OnCellSelected)
        self.Bind(grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        # self.Bind(grid.EVT_GRID_CELL_BEGIN_DRAG, self.OnDrag)
        
        self.SetGridCursor(0, 2)

    def get_actions(self):
        """
        :return:
        :rtype: list[GridAction]
        """
        actions = [GridAction(hotkey.LIST_SELECT_COLS, self._select_cols, "Select Columns", "icons/select_cols.png"),
                   GridAction(None, self._toggle_sort, "Sort by attr name", "icons/sort.png",
                              is_check_type=True)
                   ]
        return GridBase.get_actions(self) + actions

    def _toggle_sort(self):
        tbl = self.GetTable()
        tbl.set_sort_by_attr_name(not tbl.is_sort_by_attr_name())
        self.Refresh()

    # noinspection PyPep8Naming,PyUnusedLocal
    def OnRangeSelect(self, evt):
        block = self._get_selection_block()
        if not block:
            self.ClearSelection()
            return
                
        top, left, bottom, right = block
        # Only col 2 can be selected
        if not left == right == 2:
            self.SelectBlock(top, 2, bottom, 2)
            return

    # noinspection PyPep8Naming
    def OnCellSelected(self, evt):
        row, col = evt.GetRow(), evt.GetCol()

        # Only col 2 could be selected
        if col != 2:
            self.GoToCell(row, 2)
            evt.Veto()
            return
        
        evt.Skip()
        
    def _copy(self):
        block = self._get_selection_block()       
       
        attr_types, data = self.make_copy_data(block)
        if attr_types:
            self._set_clipboard(attr_types, data)
    
    def make_copy_data(self, block):
        if not block:
            wx.MessageBox("Invalid selection area", "Error")
            return None, None
        
        top, left, bottom, right = block
        if not left == right == 2:
            wx.MessageBox("Invalid selection area", "Error")
            return None, None
        
        tbl = self.GetTable()
        attr_types = [tbl.get_attr_type(row, 2) for row in xrange(top, bottom+1)]
        data = [[tbl.get_value_of_col2(row) for row in xrange(top, bottom+1)]]
        return attr_types, data

    def _paste_data(self, attr_type_names, data):
        # I can only accept 1 data row
        if len(data) > 1:
            wx.MessageBox("Too many rows to paste", "Error")
            return
        
        # current grid cursor should be at col 2
        row, col = self.GetGridCursorRow(), self.GetGridCursorCol()
        if col != 2:
            wx.MessageBox("Should select column 2")
            return
        
        # data to paste has too many columns
        if row + len(attr_type_names) > self.GetNumberRows():
            wx.MessageBox("types not match", "Error")
            return
        
        # check each AttrType
        tbl = self.GetTable()
        tmp_data = zip(*data)
        for i in xrange(len(attr_type_names)):
            attr_type = tbl.get_attr_type(row+i, 2)
            can_paste, new_values = self.check_paste(attr_type, attr_type_names[i], tmp_data[i])
            if not can_paste:
                # wx.MessageBox("type not match, expected: %s was: %s" % (attr_type.name, attr_type_names[i]), "Error")
                return
            tmp_data[i] = new_values

        data = zip(*tmp_data)
        block = (row, 2, row+len(data)-1, 2)
        self.batch_mutate(block, data, True)
