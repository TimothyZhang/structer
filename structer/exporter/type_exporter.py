# coding=utf-8

import json
import copy

from base import BaseExporter
from structer.stype.attr_types import (ATInt, ATStr, ATStruct, ATUnion, ATBool, ATEnum, ATFile, ATFloat, ATFolder,
                                       ATList, ATRef)


class JsonTypeExporter(BaseExporter):
    def _export_at(self, at):
        if isinstance(at, (ATInt, ATBool)):
            return {'type': 'int'}
        if isinstance(at, ATFloat):
            return {'type': 'float'}
        if isinstance(at, ATStr):
            return {'type': 'string'}
        if isinstance(at, ATRef):
            return {'type': 'ref', 'class': at.clazz_name}
        if isinstance(at, (ATStr, ATFile, ATFolder)):
            return {'type': 'string'}
        if isinstance(at, ATStruct):
            return {'type': 'struct', 'name': at.name}
        if isinstance(at, ATUnion):
            return {'type': 'union', 'name': at.name}
        if isinstance(at, ATEnum):
            return {'type': 'enum', 'name': at.name}
        if isinstance(at, ATList):
            if at.element_type.name == 'CostItem&':
                return {'type': 'Cost'}
            if at.element_type.name == 'YieldItemWithRate&':
                return {'type': 'Yield'}
            return {'type': 'list', 'element_type': self._export_at(at.element_type)}

        raise Exception('unsupported type: %s %s' % (at.__class__.__name__, at.name))

    def _export_struct(self, struct):
        attrs = {}
        for attr in struct.iterate():
            attrs[attr.name] = self._export_at(attr.type)

        return {'name': struct.name, 'attrs': attrs}

    def _export_enum(self, enum):
        enum_type = dict({'name': enum.name})
        enum_type['valtype'] = 'int' if (enum.export_names and not enum.convert_to_int) else 'str'
        enum_type['names'] = copy.copy(enum.names)
        enum_type['values'] = [enum.value_of(name) for name in enum.names]
        return enum_type

    def export(self):
        project = self.project

        types = {'classes': {}, 'structs': {}, 'enums': {}, 'unions': {}}

        for clazz in project.type_manager.get_clazzes():
            clazz_type = dict({'name': clazz.name})
            clazz_type['struct'] = self._export_struct(clazz.atstruct.struct)
            types['classes'][clazz.name] = clazz_type

        for union in project.type_manager.get_unions():
            union_type = dict({'name': union.name})
            enum = union.atenum.enum
            union_type['enum'] = self._export_enum(enum)
            union_type['structs'] = [self._export_struct(union.get_atstruct(name).struct) for name in enum.names]
            types['unions'][union.name] = union_type

        for enum in project.type_manager.get_enums():
            types['enums'][enum.name] = self._export_enum(enum)

        for struct in project.type_manager.get_structs():
            types['structs'][struct.name] = self._export_struct(struct)

        self.save('structer_types.json', json.dumps(types, indent=4))
