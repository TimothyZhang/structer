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
import time

from structerui import hotkey
from str_editor import GridCellStrEditor


class GridCellTimeEditor(GridCellStrEditor):
    def __init__(self):
        GridCellStrEditor.__init__(self)

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellTimeEditor()

    def BeginEdit(self, row, col, grid):
        self._canceled = False
        self._grid = grid
        self._attr_type = self._grid.GetTable().get_attr_type(row, col)

        val = grid.GetTable().GetValue(row, col)

        # convert to 2014/10/10 10:10:10
        self._ctrl.SetValue(time.strftime('%Y-%m-%d %H:%M:%s', time.gmtime(val)))
        self._ctrl.SetSelection(-1, -1)
        self._ctrl.SetFocus()

    def get_value(self, vlog=None):
        val = self._ctrl.GetValue().strip()

        # noinspection PyBroadException
        try:
            # must be seconds if it is a number
            return float(val)
        except:
            pass

        try:
            return time.strptime(val, '%Y-%m-%d %H:%M:%s')
        except Exception, e:
            if vlog:
                vlog.error('invalid time: %s (%s)', val, e)
            return None

    def StartingKey(self, evt):
        # todo: we may use 'ymdhms' to inc/dec each part of the time respectively
        # key_str = hotkey.build_keystr(evt)
        # if hotkey.check(hotkey.INCREASE, key_str):
        #     val = self.get_value() + 1
        #     self._ctrl.SetValue(unicode(val))
        #     self._grid.DisableCellEditControl()
        # elif hotkey.check(hotkey.DECREASE, key_str):
        #     val = self.get_value() - 1
        #     self._ctrl.SetValue(unicode(val))
        #     self._grid.DisableCellEditControl()

        GridCellStrEditor.StartingKey(self, evt)
