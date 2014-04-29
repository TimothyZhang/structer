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

from grid import StructGrid, StructListGrid, ListGrid, UnionGrid
from structer.stype.attr_types import ATList, ATStruct, ATUnion

class EditorPanel(wx.Panel):
    def __init__(self, parent, editor_context):
        wx.Panel.__init__(self, parent, -1)
        
        ctx = editor_context
        
        if ctx.read_only:
            self.SetBackgroundColour( wx.RED )
        
        # create grid according to attr type
        att = type(ctx.attr_type) 
        #print 'panel with:', att
        if att is ATList:   
            if type(ctx.attr_type.element_type) is ATStruct:
                grid = StructListGrid(self, ctx)
            else:         
                grid = ListGrid(self, ctx)
        elif att is ATStruct:
            grid = StructGrid(self, ctx) 
        elif att is ATUnion:
            grid = UnionGrid(self, ctx)
        #todo else ...
        else:
            #grid = wx.StaticText(self, -1, "Invalid type to edit: %s" % ctx.attr_type.name)
            raise Exception("invalid type to edit: %s" % ctx.attr_type.name)
        self.grid = grid
        
        # grid fits whole panel, with margin
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddSpacer(2)
        vbox.Add(grid, 1, wx.ALL|wx.EXPAND)
        vbox.AddSpacer(2)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(2)
        hbox.Add(vbox, 1, wx.ALL|wx.EXPAND)
        hbox.AddSpacer(2)
        
        self.SetSizer(hbox)
        hbox.Fit(self)
    
    def get_preferred_size(self):
        '''Returns a tuple (w,h)'''
        w, h = self.grid.get_preferred_size()
        return (w+4, h+4) 
    
def adjust_topwindow_size(top_window, content_size):
    #w, h = ep.get_preferred_size()
    w, h = content_size
    if h < w * 0.7:
        h = int(w * 0.7)
    if h > w * 3:
        h = w * 3
    size = top_window.ClientToWindowSize( wx.Size(w, h))
    sw, sh = wx.DisplaySize()
    size.width = min(size.width, sw*0.9)
    size.height = min(size.height, sh*0.9)
    top_window.SetSize( size )    
