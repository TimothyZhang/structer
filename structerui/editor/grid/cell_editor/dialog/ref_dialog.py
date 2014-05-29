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

from structerui import hotkey
from ref_dialog_xrc import xrcRefDialog

class RefSearchResultTable(grid.PyGridTableBase):
    _COL_LABELS = ['Class', 'ID', 'Name', 'UUID']
    def __init__(self, editor_context):
        grid.PyGridTableBase.__init__(self)
        self._ctx = editor_context
        self._objects = []
        
        self._cell_attr = ca = grid.GridCellAttr()
        ca.SetReadOnly(True)
        
    def GetNumberRows(self):
        return len(self._objects)
    
    def GetNumberCols(self):
        # id, name, uuid
        return 4
    
    def GetColLabelValue(self, col):
        return self._COL_LABELS[col]
    
    def GetAttr(self, row, col, kind):
        self._cell_attr.IncRef()
        return self._cell_attr
    
    def GetValue(self, row, col):
        obj = self._objects[row]
        if col == 0:
            return obj.clazz.name
        if col == 1:
            return obj.id
        if col == 2:
            en = obj.name

            name = obj.get_attr_value('name')
            if type(name) is dict:
                cn = name.get('cn')
                if cn and cn != en:
                    en = '%s(%s)' % (en, cn)
            return en
        if col == 3:
            return obj.uuid        
    
    def set_objects(self, objects):
        old_rows = self.GetNumberRows()
        self._objects = objects
        self._refresh(old_rows, len(objects))
    
    def get_object(self, row):
        if 0<=row<len(self._objects):
            return self._objects[row]        
        
    def _refresh(self, old_rows, new_rows):
        msg = grid.GridTableMessage(self,          # The table
           grid.GRIDTABLE_NOTIFY_ROWS_DELETED,    # what we did to it
           0,                                      # from which row
           old_rows                          # how many
        )
        self.GetView().ProcessTableMessage(msg)
        
        msg = grid.GridTableMessage(self,          # The table
           grid.GRIDTABLE_NOTIFY_ROWS_INSERTED,    # what we did to it
           0,                                      # from which row
           new_rows                                       # how many
        )
        self.GetView().ProcessTableMessage(msg)
        
        if new_rows > 0:
            self.select_row(0)  
            
    def select_row(self, row):        
        self.GetView().SetGridCursor(row, 0)
        self.GetView().ClearSelection()
        self.GetView().SelectRow(row)      
    

class RefDialog(xrcRefDialog):     
    def __init__(self, parent, editor_context):
        self.editor_context = editor_context
        self.attr_type = editor_context.attr_type
        self.project = editor_context.project
        
        xrcRefDialog.__init__(self, parent)
        
        self._post_create()

    def _post_create(self): 
        self.grid.HideRowLabels()
        self.grid.SetTable(RefSearchResultTable(self.editor_context))
        self.grid.SetSelectionMode(grid.Grid.wxGridSelectRows)
        
        #self.grid.AcceptsFocus = lambda x: False
        self.grid.Bind(wx.EVT_SET_FOCUS, self.OnGridFocus)
        self.grid.Bind(wx.EVT_SIZE, self.OnGridSize)
        self.grid.Bind(grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnGridCellLeftDClick)
        
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.OnTextCtrlKeyDown)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.OnTextCtrlText)
        self.text_ctrl.Bind(wx.EVT_TEXT_ENTER, self.OnTextCtrlTextEnter)
        
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)
        
        self._search(u'')
        
    def OnGridCellLeftDClick(self, evt):     
        row = evt.GetRow()   
        if 0 <= row < self.grid.GetNumberRows():
            self._select_search_result( row )        
        
    def _select_search_result(self, row):
        obj = self.grid.GetTable().get_object( row )
        print obj
        if obj:
            value = obj.uuid
        else:
            value = u''
            
        self.editor_context.attr_data = value
        self.Close()
        
    def get_attr_data(self):
        return self.editor_context.attr_data
    
    def OnGridFocus(self, evt):        
        #evt.Veto()
        prev = evt.GetWindow()
                
        if prev == self.text_ctrl:
            next_ = self.tree_ctrl
        else:
            next_ = self.text_ctrl
        
        wx.CallLater(0.0001, next_.SetFocus)
            
        
    def OnTextCtrlText(self, evt):
        self._search( self.text_ctrl.GetValue() )
        evt.Skip()

    def OnTextCtrlTextEnter(self, evt):
        print 'OnTextCtrlTextEnter', self.grid.GetGridCursorRow()
        self._select_search_result( self.grid.GetGridCursorRow() ) 

    def OnCharHook(self, evt):        
        keystr = hotkey.build_keystr(evt)
        if hotkey.check(hotkey.CLOSE_DIALOG, keystr):            
            self.Close()
            return
        evt.Skip()
    
    def OnTextCtrlKeyDown(self, evt):            
        key = evt.GetKeyCode()
        rows = self.grid.GetNumberRows()
        if rows > 0:
            if key == wx.WXK_UP:
                row = max(0, self.grid.GetGridCursorRow() - 1)                
                self.grid.GetTable().select_row(row)
                return            
            elif key == wx.WXK_DOWN:
                row = min(rows-1, self.grid.GetGridCursorRow() + 1)
                self.grid.GetTable().select_row(row)
                return
        
        evt.Skip()
        
    def OnGridSize(self, evt):
        w, _ = self.grid.GetSizeTuple()
        self.grid.SetColSize(0, w * 0.2)
        self.grid.SetColSize(1, w * 0.2)
        self.grid.SetColSize(2, w * 0.4)
        self.grid.SetColSize(3, w * 0.2)
        evt.Skip()
        
    def _search(self, keyword):
        objects = self.project.object_manager.get_objects(self.attr_type.clazz_name, filter_=keyword)        
        self.grid.GetTable().set_objects(objects)                     
            
