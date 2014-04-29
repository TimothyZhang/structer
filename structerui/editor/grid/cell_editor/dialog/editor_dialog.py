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

from structerui import hotkey

class EditorDialog(wx.Dialog):
    def __init__(self, parent, editor_context):                
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)        
        
        self.SetMinSize((640, 480))        
        self.editor_context = editor_context
        # avoid cyclic import
        from structerui.editor.panel import EditorPanel, adjust_topwindow_size
        self.editor_panel = ep = EditorPanel(self, editor_context)
        
        self.SetTitle( self.get_title() )    
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)
        
        adjust_topwindow_size(self, ep.get_preferred_size())        
    
    def get_title(self):
        title = self.editor_context.get_title()
        if self.editor_context.read_only:
            title += ' (ReadOnly)'
        return title
    
    def OnCharHook(self, evt):
        keystr = hotkey.build_keystr(evt)
        
        if hotkey.check(hotkey.CLOSE_DIALOG, keystr):
            if not self.editor_panel.grid.IsCellEditControlEnabled ():
                self.Close()
                return
        
        if hotkey.check(hotkey.SHOW_EXPLORER, keystr):
            self.editor_context.project.explorer.Raise()
            return
                
        evt.Skip()
    
