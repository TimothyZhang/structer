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

from structer.stype.attr_types import ATList, ATStruct, ATUnion
from structer.stype.composite_types import Attr, Struct


class UnionListListMapper(object):
    """
    Maps list[list[Union]] to list[Struct]

    usage:
        mapper = UnionListListMapper.create(ull_type, ull_data)
        if mapper:
            ...

    abbr:
        ull: Union List List
        sl: Struct List
    """
    def __init__(self, project, ull_type, ull_data, u_item_types):
        """
        internal use only.
        @see UnionListListMapper.create()
        """
        self._project = project
        self._ull_type = ull_type
        self._ull_data = ull_data
        self._u_item_types = u_item_types

        # { sl_attr_name: (union_index, union_attr_name) }
        # self._sl_names = {}
        self._sl_type = self._create_sl_type()
        self._sl_data = self._create_sl_data()

    def _create_sl_type(self):
        union = self._ull_type.element_type.element_type.union
        attrs = []
        for i, u_item_type in enumerate(self._u_item_types):
            # u_item_label = union.atenum.enum.label_of(u_item_type)
            atstruct = union.get_atstruct(u_item_type)
            for attr in atstruct.struct.iterate():
                # the new name of each attr is: <org_name>-<index>
                sl_attr_name = '%s-%s-%s' % (i+1, u_item_type, attr.name)
                attrs.append(Attr(sl_attr_name, attr.type, attr.description))
                # self._sl_names[sl_attr_name] = (i, attr.name)

        struct = Struct(self._ull_type.name, attrs)
        atstruct = ATStruct(struct)
        return ATList(atstruct, minlen=self._ull_type.minlen, maxlen=self._ull_type.maxlen)

    def _create_sl_data(self):
        union = self._ull_type.element_type.element_type.union

        sl_data = []
        for ul_data in self._ull_data:
            s_data = {}
            j = 0
            for i, u_item_type in enumerate(self._u_item_types):
                atstruct = union.get_atstruct(u_item_type)
                u_item_type2, u_item_data2 = None, None
                if j < len(ul_data):
                    u_item_type2 = ul_data[j]['key']
                    u_item_data2 = ul_data[j][u_item_type2]

                if u_item_type2 == u_item_type:
                    for attr in atstruct.struct.iterate():
                        sl_attr_name = '%s-%s-%s' % (i+1, u_item_type, attr.name)
                        s_data[sl_attr_name] = u_item_data2.get(attr.name)
                    j += 1
                else:
                    # for attr in atstruct.struct.iterate():
                    #    sl_attr_name = '%s-%s-%s' % (i+1, u_item_type, attr.name)
                    #    s_data[sl_attr_name] = attr.type.get_default(self._project)
                    pass
            sl_data.append(s_data)

        return sl_data

    def get_sl_type(self):
        return self._sl_type

    def get_sl_data(self):
        return self._sl_data

    def convert_sl_data_to_ull_data(self, sl_data):
        union = self._ull_type.element_type.element_type.union

        ull_data = []
        for s_data in sl_data:
            ul_data = []
            for i, u_item_type in enumerate(self._u_item_types):
                u_item_data = {}
                u_data = {'key': u_item_type, u_item_type: u_item_data}
                atstruct = union.get_atstruct(u_item_type)
                for attr in atstruct.struct.iterate():
                    sl_attr_name = '%s-%s-%s' % (i+1, u_item_type, attr.name)
                    u_item_data[attr.name] = s_data.get(sl_attr_name)

                nones = u_item_data.values().count(None)
                if nones != len(u_item_data):
                    if nones != 0:
                        print 'data incomplete!'
                        return None
                    ul_data.append(u_data)
            ull_data.append(ul_data)

        return ull_data

    @staticmethod
    def check_ull_type(ull_type):
        # check type
        if not isinstance(ull_type, ATList):
            return False
        ul_type = ull_type.element_type

        if not isinstance(ul_type, ATList):
            return False
        u_type = ul_type.element_type

        if not isinstance(u_type, ATUnion):
            return False
        return True

    @staticmethod
    def get_union_item_names(ull_type, ull_data):
        """
        :param structer.stype.attr_types.ATList ull_type: Union List List
        :param list ull_data: data of ull_type
        :return: union item name of each union data
        :rtype: list[str]
        """
        # check type
        if not UnionListListMapper.check_ull_type(ull_type):
            return None

        # check data
        if not ull_data:
            return None

        # get the max size one
        ul_data = max(ull_data, key=len)
        if not ul_data:
            return None

        u_type = ull_type.element_type.element_type

        # check whether ul_data is of type ul_type, and
        # extract and union item types
        u_item_types = []
        for u_data in ul_data:
            u_item_type = u_data['key']
            atstruct = u_type.union.get_atstruct(u_item_type)
            if not atstruct:
                return None

            u_item_types.append(u_item_type)

        # check that each ul_data has the same union items (is subsequence)
        for ul_data2 in ull_data:
            # if len(ul_data2) != len(ul_data):
            #    return None
            u_item_types2 = [u_data2['key'] for u_data2 in ul_data2]
            if not is_sub_sequence(u_item_types2, u_item_types):
                return None

        return u_item_types

    @staticmethod
    def create(project, ull_type, ull_data):
        """
        :param ull_type:
        :param ull_data:
        :return:
        :rtype: UnionListListMapper
        """
        u_item_types = UnionListListMapper.get_union_item_names(ull_type, ull_data)
        if not u_item_types:
            return None

        return UnionListListMapper(project, ull_type, ull_data, u_item_types)