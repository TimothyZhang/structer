# coding=utf-8

import json
import copy

from base import BaseExporter
from structer.stype.attr_types import (ATInt, ATStr, ATStruct, ATUnion, ATBool, ATEnum, ATFile, ATFloat, ATFolder,
                                       ATList, ATRef)


"""
Types:
{'type': 'int'}
{'type': 'float'}
{'type': 'str'}
{'type': 'list', 'element_type': Type}
{'type': 'ref', 'class': ClassName}
{'type': 'enum', 'name': EnumName}
{'type': 'union', 'name': UnionName}
{'type': 'struct', 'name': StructName}

{'type': 'Cost'}
{'type': 'Yield'}

Class:
{'name': ClassName, 'struct': Struct}

Struct:
{'name': StructName, 'attrs': {name: Type}}

Union:
{'name': UnionName, 'enum': Enum, 'structs': [Struct]}

Enum:
{'name': EnumName, 'valtype': 'int'/'str', 'values': [...], 'names:': [...]}
"""


def _export_enum(enum):
    enum_type = dict({'name': enum.name})
    enum_type['valtype'] = 'int' if (enum.export_names and not enum.convert_to_int) else 'str'
    enum_type['names'] = copy.copy(enum.names)
    enum_type['values'] = [enum.value_of(name) for name in enum.names]
    return enum_type


def _export_at(at):
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
        return {'type': 'struct', 'name': at.struct.name}
    if isinstance(at, ATUnion):
        return {'type': 'union', 'name': at.union.name}
    if isinstance(at, ATEnum):
        return {'type': 'enum', 'name': at.enum.name}
    if isinstance(at, ATList):
        # fixme: ugly hack for kingdom
        if at.element_type.name == 'CostItem&':
            return {'type': 'Cost'}
        if at.element_type.name == 'YieldItemWithRate&':
            return {'type': 'Yield'}
        return {'type': 'list', 'element_type': _export_at(at.element_type)}

    raise Exception('unsupported type: %s %s' % (at.__class__.__name__, at.name))


def _export_struct(struct):
    attrs = {}
    for attr in struct.iterate():
        attrs[attr.name] = _export_at(attr.type)

    return {'name': struct.name, 'attrs': attrs}


class JsonTypeExporter(BaseExporter):
    def export(self):
        project = self.project

        types = {'classes': {}, 'structs': {}, 'enums': {}, 'unions': {}}

        for clazz in project.type_manager.get_clazzes():
            clazz_type = dict({'name': clazz.name})
            clazz_type['struct'] = _export_struct(clazz.atstruct.struct)
            types['classes'][clazz.name] = clazz_type

        for union in project.type_manager.get_unions():
            union_type = dict({'name': union.name})
            enum = union.atenum.enum
            union_type['enum'] = _export_enum(enum)
            union_type['structs'] = [_export_struct(union.get_atstruct(name).struct) for name in enum.names]
            types['unions'][union.name] = union_type

        for enum in project.type_manager.get_enums():
            types['enums'][enum.name] = _export_enum(enum)

        for struct in project.type_manager.get_structs():
            types['structs'][struct.name] = _export_struct(struct)

        self.save('structer_types.json', json.dumps(types, indent=4))
