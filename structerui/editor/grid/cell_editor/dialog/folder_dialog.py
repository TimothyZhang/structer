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

from structer.util import get_relative_path

class FolderDialog(wx.DirDialog):
    def __init__(self, parent, editor_context):
        self.editor_context = editor_context
        
        wx.DirDialog.__init__(self, 
                              parent,
                              message = "Choose a directory",
                              defaultPath = self.project.path,
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        
    @property
    def project(self):
        return self.editor_context.project
    
    def get_attr_data(self):
        from structer import util
        path = util.normpath(self.GetPath())       
        return get_relative_path(path, self.project.path)
