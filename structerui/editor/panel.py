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

from grid import get_grid_by_context
from structerui.util import get_bitmap
from structerui import hotkey


class EditorPanel(wx.Panel):
    def __init__(self, parent, editor_context):
        wx.Panel.__init__(self, parent, -1)
        
        self._editor_context = ctx = editor_context
        
        if ctx.read_only:
            self.SetBackgroundColour(wx.RED)
        
        # create grid according to attr type
        grid_class = get_grid_by_context(ctx)
        self.grid = grid_class(self, ctx)
        """:type: structerui.editor.grid.base_grid.GridBase"""

        self.grid_actions = self.grid.get_actions()
        # toolbar
        self._tool_bar = self.create_toolbar()

        # grid fits whole panel, with margin
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddSpacer(2)
        vbox.Add(self._tool_bar, 0, wx.EXPAND)
        vbox.AddSpacer(2)
        vbox.Add(self.grid, 1, wx.ALL | wx.EXPAND)
        vbox.AddSpacer(2)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(2)
        hbox.Add(vbox, 1, wx.ALL | wx.EXPAND)
        hbox.AddSpacer(2)
        
        self.SetSizer(hbox)
        hbox.Fit(self)

        self.Bind(wx.EVT_KEY_DOWN, self.__on_key_down)

    @property
    def editor_context(self):
        return self._editor_context

    def create_toolbar(self):
        toolbar = wx.ToolBar(self, -1, style=wx.BORDER_SIMPLE)
        toolbar.SetToolBitmapSize(wx.Size(32, 32))
        tool_size = toolbar.GetToolBitmapSize()
        size = (tool_size.width, tool_size.height)

        def wrap(func):
            def f(x):
                _ = x
                return func()
            return f

        def wrap_check(func):
            def f(evt):
                evt.Enable(func())
            return f

        for action in self.grid_actions:
            if not action.icon:
                continue

            label = ('%s(%s)' % (action.label, action.hot_key_tr)) if action.hot_key_tr else action.label
            if action.is_check_type:
                tool = toolbar.AddCheckTool(wx.NewId(), get_bitmap(action.icon, size, self.editor_context.project),
                                            shortHelp=label)
            else:
                tool = toolbar.AddTool(wx.NewId(), get_bitmap(action.icon, size, self.editor_context.project),
                                       shortHelpString=label)
            toolbar.Bind(wx.EVT_TOOL, wrap(action.callback), id=tool.GetId())
            if action.check_enable:
                toolbar.Bind(wx.EVT_UPDATE_UI, wrap_check(action.check_enable), id=tool.GetId())

        toolbar.Realize()
        return toolbar
    
    def get_preferred_size(self):
        """Returns a tuple (w,h)"""
        w, h = self.grid.get_preferred_size()
        return w+4, h+4

    def __on_key_down(self, evt):
        # print '>>>__OnKeyDown', evt.GetKeyCode()
        keystr = hotkey.build_keystr(evt)

        for action in self.grid_actions:
            if action.check_enable and not action.check_enable():
                continue
            if hotkey.check(action.hot_key_tr, keystr):
                action.callback()
                return

        evt.Skip()

    
def adjust_topwindow_size(top_window, content_size):
    # w, h = ep.get_preferred_size()
    w, h = content_size
    if h < w * 0.7:
        h = int(w * 0.7)
    if h > w * 3:
        h = w * 3
    size = top_window.ClientToWindowSize(wx.Size(w, h))
    sw, sh = wx.DisplaySize()
    size.width = min(size.width, sw*0.9)
    size.height = min(size.height, sh*0.9)
    top_window.SetSize(size)
