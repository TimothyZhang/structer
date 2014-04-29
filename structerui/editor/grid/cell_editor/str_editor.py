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



import string

import wx

from structer.stype import attr_types 
#from structerui.editor.dialog import EditorDialog
from structerui import hotkey

from base_editor import GridCellBaseEditor

'''
'''
class GridCellStrEditor(GridCellBaseEditor):
    def __init__(self):        
        GridCellBaseEditor.__init__(self)
        
        # If ESC is pressed, EndEdit will be called and get_value() will return an empty string
        # but we want the original value instead of empty string
        # I don't know how to correct this behavior, so I just hooked ESC key event.
        self._canceled = False
        
    def Create(self, parent, id_, evtHandler):
        self._ctrl = wx.TextCtrl(parent, -1)
        self._default_bg_color = self._ctrl.GetBackgroundColour()
        self._ctrl.Bind(wx.EVT_TEXT, self.OnCtrlText)
        self._ctrl.Bind(wx.EVT_CHAR_HOOK, self.OnCtrlCharHook)
        self.SetControl(self._ctrl)

        if evtHandler:
            self._ctrl.PushEventHandler(evtHandler)
            
    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellStrEditor()

    def OnCtrlText(self, evt):
        """Check the value while text value changed, show a tip if any error occurred"""
        self.update_tip()
        evt.Skip()
        
    def OnCtrlCharHook(self, evt):
        kc = evt.GetKeyCode()
        if kc == wx.WXK_ESCAPE:
            self._canceled = True
        evt.Skip()
        
    def update_tip(self):
        self._grid.hide_tip()
        
        # try to get current vale
        vlog = attr_types.AttrVerifyLogger()
        val = self.get_value(vlog)       
        
        if not vlog.has_error():
            # got an int value, verify it        
            self._attr_type.verify(val, self._grid.editor_context.project, vlog = vlog)
        
        if vlog.has_error():    # has error.  might be eval error, or verify error            
            new_color = wx.RED
            # show a hint
            self._grid.show_tip(self._grid.GetGridCursorRow(), self._grid.GetGridCursorCol(), vlog)
        else:
            new_color = self._default_bg_color
        
        # set background color
        cur_color = self._ctrl.GetBackgroundColour();
        if cur_color != new_color:
            self._ctrl.SetBackgroundColour( new_color )
            self._ctrl.Refresh(True)
                

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        # should be an enum        
        #at = grid.GetTable().get_attr_type(row, col)
        self._canceled = False
        self._grid = grid
        self._attr_type = self._grid.GetTable().get_attr_type(row, col)
        
        val = grid.GetTable().GetValue(row, col)    
        
        self._ctrl.SetValue(unicode(val))
        self._ctrl.SetSelection(-1, -1)        
        self._ctrl.SetFocus()
        
    def get_value(self, vlog=None):
        val = self._ctrl.GetValue()
        return val        
    
    def EndEdit(self, row, col, grid, oldVal):
        """
        End editing the cell.  This function must check if the current
        value of the editing control is valid and different from the
        original value (available as oldval in its string form.)  If
        it has not changed then simply return None, otherwise return
        the value in its string form.
        *Must Override*
        """        
        if self._canceled:
            return None
        
        val = self.get_value()
        if val is None:
            return None
            
        at = grid.GetTable().get_attr_type(row, col)                                
        if at.compare(val, oldVal) != 0:
            return val
        else:
            return None
        

    def ApplyEdit(self, row, col, grid):
        """
        This function should save the value of the control into the
        grid or grid table. It is called only after EndEdit() returns
        a non-None value.
        *Must Override*
        """        
        grid.GetTable().SetValue(row, col, self.get_value() )                        
        self.Reset()

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """             
        self._grid = None   
        self._attr_type = None
                
        # change value won't fire a TEXT event
        self._ctrl.ChangeValue("")   
        self._ctrl.SetBackgroundColour( self._default_bg_color )
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
    def StartingKey(self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        
        keystr = hotkey.build_keystr(evt)
        if hotkey.check(hotkey.INSERT_FRONT, keystr):
            self._ctrl.SetSelection(0, 0)
            self._ctrl.SetInsertionPoint(0)            
        elif hotkey.check(hotkey.INSERT_TAIL, keystr):
            self._ctrl.SetSelection(0, 0)
            self._ctrl.SetInsertionPointEnd()
#         elif hotkey.check(hotkey.INCREASE, keystr):            
#             val = self.get_value() + 1
#             self._ctrl.SetValue(unicode(val))
#             self._grid.DisableCellEditControl()
#         elif hotkey.check(hotkey.DECREASE, keystr):
#             val = self.get_value() - 1
#             self._ctrl.SetValue(unicode(val))
#             self._grid.DisableCellEditControl()
        elif hotkey.check(hotkey.CELL_BEGIN_EDIT, keystr):
            evt.Skip()
        else:
            key = evt.GetKeyCode()
            if 0<=key<=255:
                ch = chr(key)
                if evt.ShiftDown():
                    ch = ch.upper()
                if ch in string.printable:
                    self._ctrl.SetValue(ch)
                    self._ctrl.SetInsertionPointEnd()
                else:
                    evt.Skip()            
            else:            
                evt.Skip()        

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

