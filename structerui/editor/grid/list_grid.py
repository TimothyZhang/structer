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
import wx.lib.gridmovers as gridmovers

from structer.stype.attr_types import ATList

from structerui import hotkey
from base_grid import GridBase, TableBase, GridAction
from cell_editor.dialog.editor_dialog import EditorDialog
from structerui.editor.ull_mapper import UnionListListMapper
from structerui.editor.undo import OpenULLDialogAction, CloseULLDialogAction


# noinspection PyMethodOverriding
class ListTable(TableBase):
    def __init__(self, ctx):
        TableBase.__init__(self, ctx)
            
    @property
    def attr_type(self):
        return self._ctx.attr_type
    
    @property
    def attr_data(self):
        return self._ctx.attr_data
    
    def get_attr_type(self, row, col):
        return self.attr_type.element_type
    
    def get_attr_value(self, row, col):
        return self.attr_data[row]
    
    def GetNumberRows(self):        
        return len(self.attr_data)

    def GetNumberCols(self):
        # name, type, value, description
        return 1

#     def GetValue(self, row, col):
#         return self.get_cell_value(self.get_attr_type(row, col) ,self.attr_data[row])            

    def set_value(self, row, col, value):
        self.attr_data[row] = value
        
    def GetColLabelValue(self, col):
        # todo: what to show?
        return self.attr_type.element_type.name
    
    def _create_default(self):
        return self.attr_type.element_type.get_default(self._ctx.project)
    
    def InsertRows(self, pos, num_rows):
        self._insert_row_data(pos, num_rows)
                    
        msg = grid.GridTableMessage(self,                                   # The table
                                    grid.GRIDTABLE_NOTIFY_ROWS_INSERTED,    # what we did to it
                                    pos,                                    # from which row
                                    num_rows                                # how many
                                    )
                
        cc = self.GetView().GetGridCursorCol()
        if cc == -1: 
            cc = 0
        
        self.GetView().ProcessTableMessage(msg)        
        # self.GetView().SetGridCursor(pos, cc)
        self.GetView().GoToCell(pos, cc)
        
        # Scrollbar might appear after new rows inserted
        # todo: is there an event for scrollbar showing/hidden?
        self.GetView().auto_size()

    def _insert_row_data(self, pos, num_rows):
        for i in xrange(num_rows):
            item = self.attr_type.element_type.get_default(self._ctx.project)        
            self.attr_data.insert(pos, item)

    def move_row(self, from_, to):
        assert 0 <= from_ <= self.GetRowsCount()
        assert 0 <= to <= self.GetRowsCount()
        if from_ + 1 == to:
            return

        row = self.attr_data.pop(from_)
        if to > from_:
            self.attr_data.insert(to-1, row)
        else:
            self.attr_data.insert(to, row)

        # Notify the grid
        view = self.GetView()
        view.BeginBatch()
        msg = grid.GridTableMessage(self, grid.GRIDTABLE_NOTIFY_ROWS_DELETED, from_, 1)
        view.ProcessTableMessage(msg)
        msg = grid.GridTableMessage(self, grid.GRIDTABLE_NOTIFY_ROWS_INSERTED, to, 1)
        view.ProcessTableMessage(msg)
        view.EndBatch()
        view.UnsetSortingColumn()
    
    def DeleteRows(self, pos, num_rows):
        for i in xrange(num_rows):
            self.attr_data.pop(pos)
        
        msg = grid.GridTableMessage(self,                                   # The table
                                    grid.GRIDTABLE_NOTIFY_ROWS_DELETED,     # what we did to it
                                    pos,                                    # from which row
                                    num_rows                                # how many
                                    )
                
        cc = self.GetView().GetGridCursorCol()
        if cc == -1: 
            cc = 0
        
        self.GetView().ProcessTableMessage(msg)
        
        if pos >= self.GetRowsCount():
            pos = self.GetRowsCount() - 1
        self.GetView().SetGridCursor(pos, cc)


class ListGrid(GridBase):
    def __init__(self, parent, editor_context, table=None):
        """
        :param parent:
        :param structerui.editor.context.EditorContext editor_context:
        :param table:
        :return:
        """
        if table is None:
            table = ListTable(editor_context)

        GridBase.__init__(self, parent, table)

        gridmovers.GridRowMover(self)
        self.Bind(gridmovers.EVT_GRID_ROW_MOVE, self.__OnRowMove, self)
        
    def get_actions(self):
        """
        :return:
        :rtype: list[GridAction]
        """
        actions = [GridAction(hotkey.LIST_INSERT_HEAD, self.insert_head, "Insert Head", "icons/insert_head.png"),
                   GridAction(hotkey.LIST_APPEND_TAIL, self._append, "Append Row", "icons/append_row.png"),
                   GridAction(hotkey.LIST_INSERT, self.insert, "Insert Row", "icons/insert_row.png"),
                   GridAction(hotkey.LIST_DELETE, self.delete, "Delete Row", "icons/delete_row.png"),

                   GridAction(hotkey.LIST_SELECT_ROWS, self._select_rows, "Select Rows", "icons/select_rows.png"),
                   GridAction(hotkey.LIST_SELECT_COLS, self._select_cols, "Select Columns", "icons/select_cols.png"),
                   GridAction(hotkey.LIST_CUT, self._cut, "Cut Rows", "icons/cut_rows.png"),
                   GridAction(hotkey.LIST_INSERT_COPIED, self.insert_copied, "Insert Rows", "icons/insert_rows.png"),
                   GridAction(hotkey.LIST_APPEND_COPIED_TAIL, self.append_copied, "Append Rows",
                              "icons/append_rows.png"),
                   GridAction(hotkey.LIST_ULL_EDITOR, self.show_ull_editor, "Super ULL Editor", "icons/ull_editor.png",
                              self.check_ull_editor)
                   ]

        return GridBase.get_actions(self) + actions

    def __OnRowMove(self, evt):
        frm = evt.GetMoveRow()          # Row being moved
        to = evt.GetBeforeRow()         # Before which row to insert
        self.GetTable().move_row(frm, to)

    def check_ull_editor(self):
        block = self._get_selection_block()
        if not block:
            return False

        top, left, bottom, right = block
        # should select only 1 column
        if left < right:
            return False

        # should select at least 2 rows
        if top == bottom:
            return False

        tbl = self.GetTable()
        attr_type = tbl.get_attr_type(top, left)
        return UnionListListMapper.check_ull_type(attr_type)

    def show_ull_editor(self):
        if not self.check_ull_editor():
            wx.MessageBox("Invalid type for ull_editor")
            return

        top, left, bottom, right = self._get_selection_block()
        tbl = self.GetTable()
        ul_type = tbl.get_attr_type(top, left)
        ull_type = ATList(ul_type)
        ull_data = [tbl.get_value(r, left) for r in xrange(top, bottom+1)]

        ull_mapper = UnionListListMapper.create(self.editor_context.project, ull_type, ull_data)
        if not ull_mapper:
            wx.MessageBox("Failed to create ull_editor")
            return

        ctx = self.editor_context.create_sub_context(ull_mapper.get_sl_type(), ull_mapper.get_sl_data())
        # ctx.freeze_none = True

        def on_close(evt):
            _ = evt
            ctx.undo_manager.add(CloseULLDialogAction())
            evt.Skip()
        
        ull_data = None
        while 1:
            ull_dlg = EditorDialog(self, ctx)
            ctx.undo_manager.add(OpenULLDialogAction())
            ull_dlg.Bind(wx.EVT_CLOSE, on_close)
            ull_dlg.ShowModal()
            # ctx.undo_manager.add(CloseULLDialogAction())

            if not ctx.is_modified():
                return

            ull_data = ull_mapper.convert_sl_data_to_ull_data(ctx.attr_data)
            # todo: should let use known where the problem is
            if ull_data is None:
                wx.MessageBox("INCOMPLETE!")

                # hack undo manager
                continue
            break

        # Write back modified data
        # NOTE: DialogEditor of composite types should modify the original value, not set a new one,
        # to keep UndoManager work properly.
        # self.editor_context.attr_data[:] = ull_data
        for i, r in enumerate(xrange(top, bottom+1)):
            tbl.SetValue(r, left, ull_data[i])

        # close current dialog
        p = self
        while p.GetParent() and not p.IsTopLevel():
            p = p.GetParent()

        if not isinstance(p, EditorDialog):
            return

        p.Close()

    def insert_head(self):
        self.insert(0, 1, add_undo=True)

    def append_copied(self):
        self.insert_copied(self.GetNumberRows())
    
    def insert(self, pos=-1, rows=1, add_undo=False):
        """
        Args:
            pos: -1 means cursor row
        """
        if pos == -1:
            pos = self.GetGridCursorRow()
        if pos == -1:
            pos = 0
        self.InsertRows(pos, rows)
        
        if add_undo:
            from structerui.editor.undo import ListInsertAction            
            attr_type_names, data = self.make_copy_data((pos, 0, pos+rows-1, self.GetNumberCols()-1))
            self._ctx.undo_manager.add(ListInsertAction(pos, attr_type_names, data))
    
    def _append(self, rows=1, add_undo=False):
        # append a new row
        pos = self.GetNumberRows()
        self.insert(pos, rows, add_undo)
        
    def insert_copied(self, pos=-1):
        attr_type_names, data = self._get_clipboard()
        if attr_type_names is None:
            return        
        
        if len(attr_type_names) != self.GetNumberCols():
            wx.MessageBox(u"data column count mismatch: expected=%s, got=%s" %
                          (self.GetNumberCols(), len(attr_type_names)))
            return
        
        tbl = self.GetTable()
        for i in xrange(self.GetNumberCols()):
            if tbl.get_attr_type(0, i).name != attr_type_names[i]:
                wx.MessageBox(u"data type to insert mismatch: col=%s, expected=%s, got=%s" % 
                              (tbl.GetColLabelValue(i), 
                               tbl.get_attr_type(0, i).name,
                               attr_type_names[i]))
                return
                
        self.insert_data(attr_type_names, data, pos)
        
        from structerui.editor.undo import ListInsertAction            
        attr_type_names, data = self.make_copy_data((pos, 0, pos+len(data)-1, self.GetNumberCols()-1))
        self._ctx.undo_manager.add(ListInsertAction(pos, attr_type_names, data))
        
    def insert_data(self, attr_type_names, data, pos=-1):
        self.insert(pos, len(data))
        
        cursor_row = self.GetGridCursorRow()
        self.paste_data(attr_type_names, data, (cursor_row, 0, cursor_row+len(data)-1, self.GetNumberCols()-1))
    
    def _select_rows(self):
        # selection block 
        block = self._get_selection_block()
#         if not block:
#             wx.MessageBox("Invalid selection area", "Error")
#             return
        
        top, _, bottom, _ = block
        
        self.SelectRow(top, False)
        for r in xrange(top+1, bottom+1):
            self.SelectRow(r, True)
    
    def delete(self, pos=None, rows=None, add_undo=True):
        if pos is None or rows is None:
            # selection block 
            block = self._get_selection_block()
            if not block:
                wx.MessageBox("Invalid selection area", "Error")
                return
            
            top, left, bottom, right = block
            
            pos = top
            rows = bottom - top + 1
            
        tbl = self.GetTable()
        
        # if (left!=right) and (left>0 or right<self.GetNumberCols()-1):
        #    wx.MessageBox("Can only delete entire rows", "Error")
        #    return
        
        # undo
        if add_undo:
            from structerui.editor.undo import ListDeleteAction            
            attr_type_names, data = self.make_copy_data((pos, 0, pos+rows-1, self.GetNumberCols()-1))
            self._ctx.undo_manager.add(ListDeleteAction(pos, attr_type_names, data))
        
        tbl.DeleteRows(pos, rows)
    
    def _copy(self, block=None):
        # selection block 
        if block is None:
            block = self._get_selection_block()
            if not block:
                wx.MessageBox("Invalid selection area", "Error")
                return
        
        attr_types, data = self.make_copy_data(block)
        self._set_clipboard(attr_types, data)
        
    def make_copy_data(self, block):
        top, left, bottom, right = block
        tbl = self.GetTable()
        # create clip board data        
        attr_types = [tbl.get_attr_type(top, c) for c in xrange(left, right+1)]
        data = [[tbl.get_value(r, c) for c in xrange(left, right+1)] for r in xrange(top, bottom+1)]
        return attr_types, data
    
    def _cut(self):
        # selection block 
        block = self._get_selection_block()
        if not block:
            wx.MessageBox("Invalid selection area", "Error")
            return
                
        # tbl = self.GetTable()
        # if (left!=right) and (left>0 or right<self.GetNumberCols()-1):
        #    wx.MessageBox("Can only cut entire rows", "Error")
        #    return
        top, left, bottom, right = block
        self._copy((top, 0, bottom, self.GetNumberCols()-1))
        
        self.delete()    

    def get_attr_type_names(self):
        t = self.GetTable()
        return [t.get_attr_type(c, 0).name for c in xrange(self.GetNumberCols())]

    def _paste_data(self, attr_type_names, data):
        self.paste_data(attr_type_names, data, add_undo=True)
        
    def paste_data(self, attr_type_names, data, block=None, add_undo=False):
        if block is None:
            # paste to selected area
            block = self._get_selection_block()
            
            top = left = bottom = right = -1  
            if block:
                top, left, bottom, right = block
            
            # only selected 1 cell, expand the area to exactly match the data size
            if top == bottom and left == right:
                # calc target area
                top, left = self.GetGridCursorRow(), self.GetGridCursorCol()
                rows = len(data)
                cols = len(data[0])
                bottom, right = top+rows-1, left+cols-1
        else:
            top, left, bottom, right = block
        
        tbl = self.GetTable()
        # check data size
        if bottom >= self.GetNumberRows() or right >= self.GetNumberCols():
            wx.MessageBox("Too many data to paste", "Error")
            return
        
        # check attr types
        tmp_data = zip(*data)
        for i, c in enumerate(xrange(left, right+1)):
            attr_type = tbl.get_attr_type(top, c)
            can_paste, new_values = self.check_paste(attr_type, attr_type_names[i], tmp_data[i])
            if not can_paste:
                # wx.MessageBox("type not match, expected: %s was: %s" % (attr_type.name, attr_type_names[i]), "Error")
                return
            tmp_data[i] = new_values

        data = zip(*tmp_data)
        block = (top, left, bottom, right)
        self.batch_mutate(block, data, add_undo=add_undo)
                
    
if __name__ == '__main__':
    pass    
