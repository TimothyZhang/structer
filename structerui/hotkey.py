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

'''
Hotkey settings

'''

_keycode_map = {wx.WXK_NUMPAD0: '0',
                wx.WXK_NUMPAD1: '1',
                wx.WXK_NUMPAD2: '2',
                wx.WXK_NUMPAD3: '3',
                wx.WXK_NUMPAD4: '4',
                wx.WXK_NUMPAD5: '5',
                wx.WXK_NUMPAD6: '6',
                wx.WXK_NUMPAD7: '7',
                wx.WXK_NUMPAD8: '8',
                wx.WXK_NUMPAD9: '9',
                wx.WXK_INSERT:  'Insert',
                wx.WXK_DELETE:  'Delete',
                wx.WXK_UP:      'Up',
                wx.WXK_DOWN:    'Down',
                wx.WXK_LEFT:    'Left',   
                wx.WXK_RIGHT:   'Right',
                wx.WXK_ESCAPE:  'Esc',
                wx.WXK_TAB:     'Tab',
                wx.WXK_BACK:    'Back',
                wx.WXK_RETURN:  'Enter',
                wx.WXK_NUMPAD_ENTER: 'Enter',
                wx.WXK_F2:       'F2',
}

def get_key_name(keycode):    
    ch = _keycode_map.get(keycode)
    if ch is not None:
        return ch
         
    if 0 <= keycode < 256 and chr(keycode) in string.printable:
        return chr(keycode).upper()
    
    return 'Unknown'

def build_keystr(evt):
    s = []
    if evt.ControlDown():
        s.append('Ctrl')
    if evt.AltDown():
        s.append('Alt')
    if evt.ShiftDown():
        s.append("Shift")
        
    key = evt.GetKeyCode()
    s.append(get_key_name(key))
    
    return '+'.join(s)
            
def check(keydef, keystr):    
    if type(keydef) is tuple:
        return keystr in keydef
    
    return keydef == keystr        

CLOSE_DIALOG = 'Esc', 'Ctrl+Q'
CLOSE_EDITOR_FRAME = 'Esc', 'Ctrl+Q'
SAVE = 'Ctrl+S'
SHOW_EXPLORER = '`'

# grid
COPY = 'Ctrl+C'
PASTE = 'Ctrl+V'
UNDO = 'Ctrl+Z'
REDO = 'Ctrl+Y'

# list
LIST_APPEND_HEAD = 'Ctrl+,'
LIST_APPEND_TAIL = 'Ctrl+.'
LIST_INSERT = 'Ctrl+I', 'Ctrl+Insert'
LIST_DELETE = 'Ctrl+D', 'Ctrl+Delete'
LIST_SELECT_ROWS = 'Ctrl+R'
LIST_SELECT_COLS = 'Ctrl+L'
LIST_CUT  = 'Ctrl+X'
LIST_INSERT_COPIED = 'Ctrl+Alt+I'
LIST_APPEND_COPIED_HEAD = 'Ctrl+Alt+,'
LIST_APPEND_COPIED_TAIL = 'Ctrl+Alt+.'

# cell
INSERT_FRONT = ','
INSERT_TAIL  = '.'
CELL_BEGIN_EDIT = ' '
INCREASE = 'I'
DECREASE = 'D'
GOTO_REF = 'Ctrl+G'
DELETE = 'Delete'  # set to default

# explorer
EXPLORER_OPEN = 'Enter', 'Alt+Down'
EXPLORER_UP_LEVEL = 'Alt+Up'
EXPLORER_HISTORY_PREV = "Alt+Left", "Back"
EXPLORER_HISTORY_NEXT = "Alt+Right"
EXPLORER_RENAME = 'F2'
