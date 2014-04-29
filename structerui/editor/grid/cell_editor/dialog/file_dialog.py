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

from structer.stype.attr_types import ATFile
from structer.util import get_relative_path

#wildcard = "Python source (*.py)|*.py|"     \
#           "Compiled Python (*.pyc)|*.pyc|" \
#           "SPAM files (*.spam)|*.spam|"    \
#           "Egg file (*.egg)|*.egg|"        \
#           "All files (*.*)|*.*"
           
class FileDialog(wx.FileDialog):
    def __init__(self, parent, editor_context):
        self.editor_context = editor_context
        
        at = editor_context.attr_type
        assert type(at) is ATFile
        
        if not at.extensions:
            wildcard = "All files (*.*)|*.*"
        else:
            tmp = ','.join(['*%s'%ext for ext in at.extensions])
            wildcard = "Files (%s)|%s" % (tmp, tmp)
        
        wx.FileDialog.__init__(self, 
                               parent, 
                               message="Choose a file",                               
                               defaultDir=self.project.path, 
                               defaultFile="",
                               wildcard=wildcard,
                               style=wx.OPEN | wx.FD_FILE_MUST_EXIST #wx.CHANGE_DIR
                               )
        self.SetPath(self.editor_context.attr_data)
        #It's not working....
        #self.Bind(wx.EVT_CLOSE, self._on_close)

    @property
    def project(self):
        return self.editor_context.project
    
    def get_attr_data(self):
        from structer import util
        path = util.normpath(self.GetPath())
        return get_relative_path(path, self.project.path)
    
#     def _on_close(self, evt):
#         path =  self.GetPath()
#         self.editor_context.attr_data = path
#         
#         evt.Skip()
#         
