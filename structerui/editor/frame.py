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

from structerui import hotkey, log

from panel import EditorPanel, adjust_topwindow_size
from structerui.util import get_clazz_bitmap, FRAME_ICON_SIZE


class EditorFrame(wx.Frame):
    def __init__(self, parent, editor_context):
        _ = parent
        super(EditorFrame, self).__init__(None, -1, style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((640, 480))
        # self.Maximize()
        
        self.editor_context = editor_context
        self.editor_panel = ep = EditorPanel(self, editor_context)
        
        self.SetTitle(self.get_title())
        
        # icon
        bmp = get_clazz_bitmap(editor_context.clazz, FRAME_ICON_SIZE, editor_context.project)
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(bmp)            
        self.SetIcon(icon)

        # self.Bind(wx.EVT_MOVE, self.OnMoved)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # should AFTER EVT_MOVE
        adjust_topwindow_size(self, ep.get_preferred_size())
        self.Centre(wx.BOTH)
        
        # editor_context.project.explorer.editor_frames.append(self)
#     def OnMoved(self, evt):
#         # tip position might be wrong after frame moved, reset it
#         self.editor_panel.grid.position_tip()
#         
#         evt.Skip()
    
    def get_title(self):
        title = self.editor_context.get_title()
        if self.editor_context.read_only:
            title += ' (ReadOnly)'
        return title
    
    def OnKeyDown(self, evt):
        key_str = hotkey.build_keystr(evt)
        
        if hotkey.check(hotkey.CLOSE_EDITOR_FRAME, key_str):
            if not self.editor_panel.grid.IsCellEditControlEnabled():
                self.Close()
                return
            
        if hotkey.check(hotkey.SAVE, key_str):
            self.save()
            return
        
        if hotkey.check(hotkey.SHOW_EXPLORER, key_str):
            self.editor_context.project.explorer.Raise()
            return
                
        evt.Skip()
        
    def OnClose(self, evt):        
        self.editor_panel.grid.DisableCellEditControl()
        
        # debug
        if self.editor_context.read_only and self.editor_context.is_modified():            
            log.error('modified in a readonly frame!')
        
        if not self.editor_context.read_only and self.editor_context.is_modified():
            self.Raise()
            r = wx.MessageBox("Save before exit?", "Confirm",  wx.YES_NO | wx.CANCEL, self)
            if r == wx.YES:
                if not self.save():
                    log.alert("save failed!")                                        
                    return                
            elif r == wx.CANCEL:                    
                return
        
        self.editor_context.project.explorer.remove_editor(self)
        evt.Skip()
            
    def save(self):
        self.editor_panel.grid.DisableCellEditControl()
        if self.editor_context.is_modified():
            return self.editor_context.save()
        return True
    
    def close(self):
        self.Close()
        pass
