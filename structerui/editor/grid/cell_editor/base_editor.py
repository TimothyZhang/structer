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

class GridCellBaseEditor(grid.PyGridCellEditor):
    def __init__(self):        
        grid.PyGridCellEditor.__init__(self)
    
#     def Draw(self, grid, attr, dc, rect, row, col, isSelected):
#         dc.SetBackgroundMode(wx.SOLID)
#         dc.SetBrush(wx.Brush(attr.GetBackgroundColour(), wx.SOLID))
#         dc.SetPen(wx.TRANSPARENT_PEN)
#         dc.DrawRectangleRect(rect)
# 
#         dc.SetBackgroundMode(wx.TRANSPARENT)
#         dc.SetFont(attr.GetFont())
# 
#         #text = grid.GetCellValue(row, col)
#         text = self._get_object_name(grid, row, col)
#         
#         dc.SetTextForeground( attr.GetTextColour() )
#         #dc.SetBrush(wx.TRANSPARENT_BRUSH)        
#         dc.DrawText(text, rect.x+1, rect.y+1)
#         
#     def GetBestSize(self, grid, attr, dc, row, col):
#         text = self._get_object_name(grid, row, col)  # grid.GetCellValue(row, col)
#         dc.SetFont(attr.GetFont())
#         w, h = dc.GetTextExtent(text)
#         return wx.Size(w, h)
    
#     def _get_object_name(self, grid, row, col):
#         p = grid.editor_context.project
#         uuid = grid.GetCellValue(row, col)
#         obj = p.get_object(uuid)
#         if obj:
#             return obj.name
#         
#         #todo: return what?
#         return uuid

#     def Clone(self):
#         return GridCellBaseEditor()
