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

import wx
import wx.grid as grid

from structer.stype.attr_types import *
from structerui import hotkey

from base_grid import GridBase, TableBase, CLIPBOARD_DATA_FORMAT

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
        #todo: what to show?        
        return self.attr_type.element_type.name
    
    def _create_default(self):
        return self.attr_type.element_type.get_default(self._ctx.project)
    
    def InsertRows(self, pos, numRows):
        self._insert_row_datas(pos, numRows)
                    
        msg = grid.GridTableMessage(self,          # The table
           grid.GRIDTABLE_NOTIFY_ROWS_INSERTED,    # what we did to it
           pos,                                      # from which row
           numRows                                       # how many
        )
                
        cc = self.GetView().GetGridCursorCol()
        if cc == -1: 
            cc = 0
        
        self.GetView().ProcessTableMessage(msg)        
        #self.GetView().SetGridCursor(pos, cc)
        self.GetView().GoToCell(pos, cc)
        
        # Scrollbar might appear after new rows inserted
        # todo: is there an event for scrollbar showing/hidding?
        self.GetView().auto_size()

    def _insert_row_datas(self, pos, numRows):
        for i in xrange(numRows):        
            item = self.attr_type.element_type.get_default(self._ctx.project)        
            self.attr_data.insert(pos, item)
    
    def DeleteRows(self, pos, numRows):
        for i in xrange(numRows):
            self.attr_data.pop(pos)
        
        msg = grid.GridTableMessage(self,          # The table
           grid.GRIDTABLE_NOTIFY_ROWS_DELETED,    # what we did to it
           pos,                                      # from which row
           numRows                                       # how many
        )
                
        cc = self.GetView().GetGridCursorCol()
        if cc == -1: 
            cc = 0
        
        self.GetView().ProcessTableMessage(msg)
        
        if pos >= self.GetRowsCount():
            pos = self.GetRowsCount() - 1
        self.GetView().SetGridCursor(pos, cc)

class ListGrid(GridBase):
    def __init__(self, parent, editor_context, table = None):
        if table is None:
            table = ListTable(editor_context)
        GridBase.__init__(self, parent, table)
        
        # hot keys
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    
    def OnKeyDown(self, evt):
        keystr = hotkey.build_keystr(evt)
        
        if self._ctx.read_only:
            evt.Skip()
            return
        
        if hotkey.check(hotkey.LIST_APPEND_HEAD, keystr):
            #self.InsertRows(0, 1)
            self.insert(0, 1, add_undo=True)
        elif hotkey.check(hotkey.LIST_APPEND_TAIL, keystr):         
            self._append(add_undo=True)
            return
        elif hotkey.check(hotkey.LIST_INSERT, keystr):  
            self.insert(add_undo=True)   
            return
        elif hotkey.check(hotkey.LIST_DELETE, keystr):
            self.delete()
            return
        elif hotkey.check(hotkey.LIST_SELECT_ROWS, keystr):
            self._select_rows()
            return
        elif hotkey.check(hotkey.LIST_CUT, keystr):
            self._cut()
            return
        elif hotkey.check(hotkey.LIST_INSERT_COPIED, keystr):
            self.insert_copied()
            return
        elif hotkey.check(hotkey.LIST_APPEND_COPIED_HEAD, keystr):
            self.insert_copied( 0 )
            return
        elif hotkey.check(hotkey.LIST_APPEND_COPIED_TAIL, keystr):
            self.insert_copied( self.GetNumberRows() )
            return
        evt.Skip()    
    
    def insert(self, pos=-1, rows=1, add_undo=False):
        '''
        Args:
            pos: -1 means cursor row
        '''
        if pos==-1:
            pos = self.GetGridCursorRow()
        if pos == -1:
            pos = 0
        self.InsertRows(pos, rows)
        
        if add_undo:
            from structerui.editor.undo import ListInsertAction            
            attr_type_names, datas = self.make_copy_data( (pos, 0, pos+rows-1, self.GetNumberCols()-1))
            self._ctx.undo_manager.add( ListInsertAction(pos, attr_type_names, datas) )            
    
    def _append(self, rows=1, add_undo=False):
        # append a new row
        pos = self.GetNumberRows()
        self.insert(pos, rows, add_undo)
        
    def insert_copied(self, pos=-1):
        attr_type_names, datas = self._get_clipboard()
        if attr_type_names is None:
            return        
        
        if len(attr_type_names) != self.GetNumberCols():
            wx.MessageBox(u"data column count mismatch: expeteced=%s, got=%s" %(self.GetNumberCols(), len(attr_type_names) ))
            return
        
        tbl = self.GetTable()
        for i in xrange(self.GetNumberCols()):
            if tbl.get_attr_type(0, i).name != attr_type_names[i]:
                wx.MessageBox(u"data type to insert mismatch: col=%s, expected=%s, got=%s" % 
                              (tbl.GetColLabelValue(i), 
                              tbl.get_attr_type(0, i).name, 
                              attr_type_names[i]))
                return
                
        self.insert_datas(attr_type_names, datas, pos)   
        
        from structerui.editor.undo import ListInsertAction            
        attr_type_names, datas = self.make_copy_data( (pos, 0, pos+len(datas)-1, self.GetNumberCols()-1))
        self._ctx.undo_manager.add( ListInsertAction(pos, attr_type_names, datas) )      
        
    def insert_datas(self, attr_type_names, datas, pos=-1):
        self.insert(pos, len(datas))
        
        cursor_row = self.GetGridCursorRow()
        self.paste_data(attr_type_names, datas, (cursor_row, 0, cursor_row+len(datas)-1, self.GetNumberCols()-1))        
    
#     def _append_copied(self):
#         attr_type_names, datas = self._get_clipboard()
#         if attr_type_names is None:
#             return
#         self._append(len(datas))
#         self._paste()
    
    def _select_rows(self):
        # selection block 
        block = self._get_selection_block()
#         if not block:
#             wx.MessageBox("Invalid selection area", "Error")
#             return
        
        top,_,bottom,_ = block
        
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
            
            top,left,bottom,right = block
            
            pos = top
            rows = bottom - top + 1
            
        tbl = self.GetTable()
        
        #if (left!=right) and (left>0 or right<self.GetNumberCols()-1):
        #    wx.MessageBox("Can only delete entire rows", "Error")
        #    return
        
        # undo
        if add_undo:
            from structerui.editor.undo import ListDeleteAction            
            attr_type_names, datas = self.make_copy_data( (pos, 0, pos+rows-1, self.GetNumberCols()-1))
            self._ctx.undo_manager.add( ListDeleteAction(pos, attr_type_names, datas) )             
        
        tbl.DeleteRows(pos, rows)
    
    def _copy(self, block=None):
        # selection block 
        if block is None:
            block = self._get_selection_block()
            if not block:
                wx.MessageBox("Invalid selection area", "Error")
                return
        
        attr_type_names, datas = self.make_copy_data(block)
        self._set_clipboard(attr_type_names, datas)
        
    def make_copy_data(self, block):
        top,left,bottom,right = block
        tbl = self.GetTable()
        # create clip board data        
        attr_type_names = [tbl.get_attr_type(top, c).name for c in xrange(left, right+1)]
        datas = [[tbl.get_value(r,c) for c in xrange(left, right+1)] for r in xrange(top, bottom+1)]
        return attr_type_names, datas
    
    def _cut(self):
        # selection block 
        block = self._get_selection_block()
        if not block:
            wx.MessageBox("Invalid selection area", "Error")
            return
                
        #tbl = self.GetTable()
        
        #if (left!=right) and (left>0 or right<self.GetNumberCols()-1):
        #    wx.MessageBox("Can only cut entire rows", "Error")
        #    return
        top,left,bottom,right = block
        self._copy( (top, 0, bottom, self.GetNumberCols()-1) )
        
        self.delete()    

    def get_attr_type_names(self):
        t = self.GetTable()
        return [t.get_attr_type(c, 0).name for c in xrange(self.GetNumberCols())]

    def _paste_data(self, attr_type_names, datas):         
        self.paste_data(attr_type_names, datas, add_undo=True)
        
    def paste_data(self, attr_type_names, datas, block=None, add_undo=False):
        if block is None:
            # paste to selected area
            block = self._get_selection_block()
            
            top = left = bottom = right = -1  
            if block:
                top, left, bottom, right = block
            
            # only selected 1 cell, expand the area to exaclty match the data size
            if top==bottom and left==right:
                # calc target area
                top, left = self.GetGridCursorRow(), self.GetGridCursorCol()
                rows = len(datas)
                cols = len(datas[0])
                bottom, right = top+rows-1, left+cols-1
        else:
            top, left, bottom, right = block
        
        tbl = self.GetTable()
        # check data size
        if bottom >= self.GetNumberRows() or right >= self.GetNumberCols():
            wx.MessageBox("Too many data to paste", "Error")
            return
        
        # check attr types
        for i, c in enumerate(xrange(left, right+1)):
            at_name = tbl.get_attr_type(top, c).name
            if at_name != attr_type_names[i]:
                wx.MessageBox("type not match, expected: %s was: %s" % (at_name, attr_type_names[i]), "Error")
                return
        
        block = (top, left, bottom, right)
        self.batch_mutate( block, datas, add_undo=add_undo)
                
    
if __name__ == '__main__':
    pass    
