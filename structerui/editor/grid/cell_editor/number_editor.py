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

from structer import log
#from structerui.editor.dialog import EditorDialog
from structerui import hotkey

from str_editor import GridCellStrEditor

'''
'''
class GridCellIntEditor(GridCellStrEditor):
    def __init__(self):        
        GridCellStrEditor.__init__(self)
               
    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellIntEditor()
    
    def get_value(self, vlog=None):
        val = self._ctrl.GetValue()
        
        try:
            ret = eval(val, {}, {})
        except Exception, e:
            if vlog:
                vlog.error('invalid expression: %s', e)
            return None
            
        if type(ret) not in (int, long):
            if vlog:
                vlog.error('invalid type: %s', type(ret))
            return None
            
        return ret
    
    
    def StartingKey(self, evt):
        keystr = hotkey.build_keystr(evt)        
        if hotkey.check(hotkey.INCREASE, keystr):            
            val = self.get_value() + 1
            self._ctrl.SetValue(unicode(val))
            self._grid.DisableCellEditControl()
        elif hotkey.check(hotkey.DECREASE, keystr):
            val = self.get_value() - 1
            self._ctrl.SetValue(unicode(val))
            self._grid.DisableCellEditControl()
        
        GridCellStrEditor.StartingKey(self, evt)

class GridCellFloatEditor(GridCellIntEditor):
    def __init__(self):
        GridCellIntEditor.__init__(self)
        
    def Clone(self):
        return GridCellFloatEditor()
    
    def get_value(self, vlog=None):
        val = self._ctrl.GetValue()
        
        try:
            ret = eval(val, {}, {})
        except Exception, e:
            if vlog:
                vlog.error('invalid expression: %s', e)
            return None
            
        if type(ret) not in (int, long, float):
            if vlog:
                vlog.error('invalid type: %s', type(ret))
            return None
            
        return float(ret)
    
