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
from structer.stype.attr_types import ATDict, ATStruct, ATList
from structer.stype.composite_types import Struct, Attr
from structerui.editor.grid.cell_editor import GridCellDialogEditor


class DictEditor(GridCellDialogEditor):
    def __init__(self):
        GridCellDialogEditor.__init__(self)

        self._original_dict_type = None

    def _get_editing_type_and_value(self, row, col, grid):
        tbl = grid.GetTable()
        at = tbl.get_attr_type(row, col)
        val = tbl.get_attr_value(row, col)

        assert isinstance(at, ATDict)

        # todo: can not undo, because we lost item order
        self._original_dict_type = atdict = at
        atstruct = ATStruct(Struct(atdict.name,
                                   [Attr('key', atdict.key_type), Attr('value', atdict.val_type)]))
        at2 = ATList(atstruct, unique_attrs=('key',), minlen=atdict.minlen, maxlen=atdict.maxlen)
        val2 = []
        for k, v in val:
            val2.append({'key': k, 'value': v})
        return at2, val2

    # noinspection PyMethodMayBeStatic
    def _get_result_value(self, val):
        assert isinstance(val, list)
        r = []
        for tmp in val:
            r.append([tmp['key'], tmp['value']])

        return r
