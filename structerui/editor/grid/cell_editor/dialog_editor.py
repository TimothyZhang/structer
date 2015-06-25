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

from dialog import EditorDialog
from structerui.editor.context import EditorContext

from base_editor import GridCellBaseEditor

def print_(s):
    print s
            
class GridCellDialogEditor(GridCellBaseEditor):
    '''Opens a new dialog to editor the grid cell'''
    
    def __init__(self, dialog_class = None):
        '''
        Args:
            dialog_class: the Class object of dialog. use EditorDialog by default.
        '''
        GridCellBaseEditor.__init__(self)
        
        if dialog_class is None:
            dialog_class = EditorDialog
        self.dialog_class = dialog_class
    
    def Create(self, parent, id_, evtHandler):
        self._ctrl = wx.StaticText(parent, id_, "", style=wx.TE_PROCESS_ENTER |                                    
                                   wx.ST_NO_AUTORESIZE | 
                                   wx.ST_ELLIPSIZE_END)
        #self._ctrl = wx.TextCtrl(parent, id_, "", style=wx.TE_PROCESS_ENTER )        
        self.SetControl(self._ctrl)

        if evtHandler:
            self._ctrl.PushEventHandler(evtHandler)
            
    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellDialogEditor()

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """        
        #print 'setsize:', rect.x, rect.y, rect.width, rect.height
        self._ctrl.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)
        #self._ctrl.SetSize( wx.Size(rect.width, rect.height) )
        #self._ctrl.SetPosition( wx.Point(rect.x, rect.y) )       


    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.
        """        
        super(GridCellDialogEditor, self).Show(show, attr)
        
        if show:
            self._ctrl.SetBackgroundColour( wx.GREEN )
            #self._ctrl.SetBackgroundColour( wx.GREEN )
            if attr:
                self._ctrl.SetForegroundColour( attr.GetTextColour() )
                self._ctrl.SetFont( attr.GetFont() )        
        

#     def PaintBackground(self, rect, attr, p):
#         """
#         Draws the part of the cell not occupied by the edit control.  The
#         base  class version just fills it with background colour from the
#         attribute.  In this class the edit control fills the whole cell so
#         don't do anything at all in order to reduce flicker.
#         """
#         #print_("MyCellEditor: PaintBackground\n")
#         pass


    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        #print 'begineditor'
        self._grid = grid
        self._row = row
        self._col = col
        
        tbl = grid.GetTable()
        at = tbl.get_attr_type(row, col)
        val = tbl.get_attr_value(row, col)
        
        ### create context for new dialog        
        # This a a little tricky!
        # val will not been copied, since val is always a container
        # If val was copied, UndoManager will NOT work properly!!!
        self._dlg_ctx = ctx = tbl.editor_context.create_sub_context(at, val)
        
        ### display current value (backgrond is green highlighted)
        self._ctrl.SetLabel(at.str(val, grid.editor_context.project))          
        
        # create dialog
        dlg = self.dialog_class(self._ctrl, ctx)
        self._set_dialog_position(dlg, grid.get_cell_rect_on_screen(row, col) )
        
        # ShowModal() will block the entire app, while ShowWindowModal() is only availabe on osx
        # so we should not use ShowModal() on EditorDialog
        if type(dlg) is EditorDialog:                         
            dlg.Bind(wx.EVT_CLOSE, self.OnDialogClose)
            
            ### disable current TopLevelWindow(Frame or Dialog)
            # find TopLevelWindow
            p = grid
            while p.GetParent() and not p.IsTopLevel():
                p = p.GetParent()
            self._top_level_window = p
            # disable it
            p.Enable(False)
        
            ### undo manager        
            from structerui.editor.undo import OpenDialogAction
            ctx.undo_manager.add(OpenDialogAction(row, col))

            dlg.Show()

        else:
            # wx.FileDialog can ONLY work with ShowModal(), and also EVT_CLOSE is not working on it.
            # So we have not choice but blocking the entire application with ShowModal(), and then
            # fetch it's value manually
            if wx.ID_OK == dlg.ShowModal():
                ctx.attr_data = dlg.get_attr_data()               
            dlg.Destroy()

            # end edit, right after Dialog closes
            grid.DisableCellEditControl()

    def OnDialogClose(self, evt):        
        dlg = evt.GetEventObject()
        assert dlg
        
        ### undo manager
        if type(dlg) is EditorDialog:
            from structerui.editor.undo import CloseDialogAction
            self._dlg_ctx.undo_manager.add( CloseDialogAction(self._row, self._col) )
            
        ### restore TopLevelWindow
        self._top_level_window.Enable(True)
        
        ### edit finished. 
        # Must be placed at last, since it'll call Reset() indirectly
        self._grid.DisableCellEditControl()            
        
        evt.Skip()
    
    def _set_dialog_position(self, dlg, parent_rect_on_screen):
        '''Sets postions of new dialog
        
        Args:
            parent_rect_on_screen: the rect of cell been editing, in screen coordinates.
        '''
        r = parent_rect_on_screen        
        w, h = dlg.GetSizeTuple()
        sw, sh = wx.DisplaySize()
        
        # bottom,left
        x, y = r.left, r.bottom+1
        
        if y + h >= sh:
            # top
            y = r.top - h - 1
            if y < 0:
                y = 0
        
        if x + w >= sw:
            x = sw - w - 1
        
        dlg.SetPosition( wx.Point(x, y) )
    
    def EndEdit(self, row, col, grid, oldVal):
        """
        End editing the cell.  This function must check if the current
        value of the editing control is valid and different from the
        original value (available as oldval in its string form.)  If
        it has not changed then simply return None, otherwise return
        the value in its string form.
        *Must Override*
        """
        
        #print 'EndEdit'

        ### For EditorDialog, val and oldVal is not only equal but the same object! Since val is a list or dict
        # and we used it directly. But it might be different for other dialogs.                
        #val =             
        if self._dlg_ctx.is_modified():                        
            return self._dlg_ctx.attr_data
        else:
            return None
        

    def ApplyEdit(self, row, col, grid):
        """
        This function should save the value of the control into the
        grid or grid table. It is called only after EndEdit() returns
        a non-None value.
        *Must Override*
        """        
        #print 'ApplyEdit'
        grid.GetTable().SetValue(row, col, self._dlg_ctx.attr_data )                        
        self.Reset()

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        pass        
        #print 'Reset'
        self._dlg_ctx = None        
        self._grid = None
        self._top_level_window = None
        self._row = self._col = None
        
        self._ctrl.SetLabel("")

#     def IsAcceptedKey(self, evt):
#         """
#         Return True to allow the given key to start editing: the base class
#         version only checks that the event has no modifiers.  F2 is special
#         and will always start the editor.
#         """
#         print_("MyCellEditor: IsAcceptedKey: %d\n" % (evt.GetKeyCode()))
# 
#         ## We can ask the base class to do it
#         #return super(MyCellEditor, self).IsAcceptedKey(evt)
# 
#         # or do it ourselves
#         return (not (evt.ControlDown() or evt.AltDown()) and
#                 evt.GetKeyCode() != wx.WXK_SHIFT)
# 
# 
#     def StartingKey(self, evt):
#         """
#         If the editor is enabled by pressing keys on the grid, this will be
#         called to let the editor do something about that first key if desired.
#         """
#         print_("MyCellEditor: StartingKey %d\n" % evt.GetKeyCode())
#         key = evt.GetKeyCode()
#         ch = None
#         import string
#         if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, 
#                     wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, 
#                     wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
#                     ]:
# 
#             ch = ch = chr(ord('0') + key - wx.WXK_NUMPAD0)
#             
#         elif key < 256 and key >= 0 and chr(key) in string.printable:
#             ch = chr(key)
# 
#         if ch is not None:
#             # For this example, replace the text.  Normally we would append it.
#             #self._tc.AppendText(ch)
#             if ch == ',':
#                 self._tc.AppendText(ch)
#             else:
#                 self._tc.SetValue(ch)
#                 self._tc.SetInsertionPointEnd()
#         else:
#             evt.Skip()


#     def StartingClick(self):
#         """
#         If the editor is enabled by clicking on the cell, this method will be
#         called to allow the editor to simulate the click on the control if
#         needed.
#         """
#         print_("MyCellEditor: StartingClick\n")
# 
# 
#     def Destroy(self):
#         """final cleanup"""
#         print_("MyCellEditor: Destroy\n")
#         super(GridCellPopupEditor, self).Destroy()



