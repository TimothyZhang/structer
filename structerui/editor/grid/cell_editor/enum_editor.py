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

#from structerui.editor.dialog import EditorDialog
#from structerui.editor.context import EditorContext

from base_editor import GridCellBaseEditor

'''
'''
class GridCellEnumEditor(GridCellBaseEditor):
    def __init__(self):        
        GridCellBaseEditor.__init__(self)
    
    def Create(self, parent, id_, evtHandler):
        self._ctrl = wx.ComboBox(parent, id_, style=wx.CB_READONLY|wx.TE_PROCESS_ENTER|wx.WANTS_CHARS)
        self.SetControl(self._ctrl)

        if evtHandler:
            self._ctrl.PushEventHandler(evtHandler)
            
    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellEnumEditor()

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        # should be an enum
        #self._grid = grid
        at = grid.GetTable().get_attr_type(row, col)
        label = grid.GetTable().GetValue(row, col)

        #print at,type(at),at.name
        labels = at.labels
        self._ctrl.SetItems(labels)
        
        if label not in labels:
            val = at.get_default(grid.GetTable().editor_context.project)
            label = at.enum.label_of(val)

        # select original value
        self._ctrl.SetStringSelection(label)
        self._oldLabel = label
        
        self._ctrl.Popup()
        
    def get_selected_label(self, row, col, grid):
        # index = self._ctrl.GetSelection()
        sel = self._ctrl.GetStringSelection()
        at = grid.GetTable().get_attr_type(row, col)

        # empty if cancelled
        return sel
        
    def EndEdit(self, row, col, grid, oldVal):
        """
        End editing the cell.  This function must check if the current
        value of the editing control is valid and different from the
        original value (available as oldval in its string form.)  If
        it has not changed then simply return None, otherwise return
        the value in its string form.
        *Must Override*
        """
        at = grid.GetTable().get_attr_type(row, col)
        label = self.get_selected_label(row, col, grid)
        if not label:  # cancelled
            return None

        val = at.enum.name_of_label(label)
        print oldVal, val, label
        oldVal = at.enum.name_of_label(oldVal)
        # print '...', val, oldVal
        if val and at.compare(val, oldVal) != 0:
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
        at = grid.GetTable().get_attr_type(row, col)
        label = self.get_selected_label(row, col, grid)
        if label:
            val = at.enum.name_of_label(label)
            grid.GetTable().SetValue(row, col, val)
        else:  # cancelled
            pass

        self.Reset()

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """                
        #self._ctrl.SetLabel("")
        #del self._grid
        self._ctrl.SetItems([""])

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



