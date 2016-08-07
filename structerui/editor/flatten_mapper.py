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

from structer.util import is_sub_sequence

from structer.stype.attr_types import AttrType, ATList, ATStruct, ATUnion, ATInt, ATStr, ATEnum, ATDict
from structer.stype.composite_types import Attr, Struct


class FlattenMapper(object):
    def __init__(self, project, column_names, attr_types, data):
        """
        :param Project project:
        :param list[str] column_names:
        :param list[AttrType] attr_types:
        :param list[list[*]] data:
        """
        self._project = project
        self._column_names = column_names
        self._attr_types = attr_types
        self._data = data

        self._mapped_type = None
        self._mapped_data = None
        self._init()

    def _init(self):
        mapped_attrs = []
        """:type: list[Attr]"""
        mapped_data = [{} for _ in self._data]
        """:type: list[dict]"""

        for i, at in enumerate(self._attr_types):
            col_name = self._column_names[i]

            if at.is_primitive():
                mapped_attrs.append(Attr(col_name, at))
                for j, row in enumerate(self._data):
                    mapped_data[j][col_name] = row[i]
            elif isinstance(at, ATStruct):
                for attr in at.struct.iterate():
                    attr_name = '%s-%s' % (col_name, attr.name)
                    mapped_attrs.append(Attr(attr_name, attr.type))
                    for j, row in enumerate(self._data):
                        mapped_data[j][attr_name] = row[i][attr.name]
            elif isinstance(at, ATList):
                pass
            elif isinstance(at, ATDict):
                pass
            elif isinstance(at, ATUnion):
                pass

        struct = Struct('flatten_editor', mapped_attrs)
        atstruct = ATStruct(struct)
        self._mapped_atstruct = atstruct
        self._mapped_type = ATList(atstruct)
        self._mapped_data = mapped_data

    def get_mapped_type(self):
        return self._mapped_type

    def get_mapped_data(self):
        return self._mapped_data

    def convert_data(self, mapped_data):
        assert len(mapped_data) == len(self._data)
        data = [[None for _j in self._column_names] for _i in self._data]

        for i, at in enumerate(self._attr_types):
            col_name = self._column_names[i]

            if at.is_primitive():
                for j, row in enumerate(self._data):
                    data[j][i] = mapped_data[j][col_name]
            elif isinstance(at, ATStruct):
                for j, row in enumerate(self._data):
                    data[j][i] = tmp = {}
                    for attr in at.struct.iterate():
                        attr_name = '%s-%s' % (col_name, attr.name)
                        tmp[attr.name] = mapped_data[j][attr_name]
            elif isinstance(at, ATList):
                pass
            elif isinstance(at, ATDict):
                pass
            elif isinstance(at, ATUnion):
                pass
        return data
