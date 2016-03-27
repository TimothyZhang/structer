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

# from structerui import hotkey
from str_editor import GridCellStrEditor
from structer.util import seconds_to_dhms


class GridCellDurationEditor(GridCellStrEditor):
    def __init__(self):
        GridCellStrEditor.__init__(self)

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellDurationEditor()

    def BeginEdit(self, row, col, grid):
        self._canceled = False
        self._grid = grid
        self._attr_type = self._grid.GetTable().get_attr_type(row, col)

        todo: 已经是字符串了! time也是!
        val = grid.GetTable().GetValue(row, col)

        # convert to 1234 10:10:10
        self._ctrl.SetValue('%d/%02d:%02d:%02d' % seconds_to_dhms(val))
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
            tmp = val.split('/')

            days = 0
            if len(tmp) > 1:
                days = int(tmp[0])

            h, m, s = tmp[1].split(':')
            h = days * 24 + int(h)
            m = h * 60 + int(m)
            s = m * 60 + float(s)
            return s
        except Exception, e:
            if vlog:
                vlog.error('invalid duration: %s (%s)', val, e)
            return None

    def StartingKey(self, evt):
        # todo: we may use 'dhms' to inc/dec each part of the time respectively
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
