# coding=utf-8
__author__ = 'Timothy'

from base import BaseExporter
from structer.stype.attr_types import (ATInt, ATStr, ATStruct, ATUnion, ATBool, ATEnum, ATFile, ATFloat, ATFolder,
                                       ATList, ATRef)


JS_CLASS_TEMPLATE = 'kd.%sBase = ff.Class.extend({\n%s\n});'


def get_jstype_by_python_value(val):
    if isinstance(val, (int, float)):
        return 'number'
    if isinstance(val, (str, unicode)):
        return 'string'
    if isinstance(val, list):
        # items might have different types
        # if len(val):
        #    return 'Array.<%s>' % get_jstype_by_python_value(val[0])
        return 'Array'
    if isinstance(val, dict):
        # items might have different types
        # if len(val):
        #     k, v = val.iteritems().next()
        #     return 'Object.<%s, %s>' % (get_jstype_by_python_value(k), get_jstype_by_python_value(v))
        return 'Object'
    raise Exception("Can't convert python val to jstype: %s" % val)


def js_get_default_by_type(js_type):
    if js_type == 'number':
        return '0'
    if js_type == 'string':
        return "''"
    if js_type.startswith('Array'):
        return '[]'
    if js_type.startswith('Object'):
        return {}
    return 'null'


def js_generate_member(js_type, name):
    return '    /**\n'\
           '    * @type {%s}\n'\
           '    */\n'\
           '    "%s": %s' % (js_type, name, js_get_default_by_type(js_type))


class JsTypeExporter(BaseExporter):
    def get_jstype_by_attrtype(self, at):
        if isinstance(at, (ATInt, ATFloat, ATRef)):
            return 'number'
        if isinstance(at, (ATStr, ATFile, ATFolder)):
            return 'string'
        if isinstance(at, ATStruct):
            # customized
            if at.struct.exporter:
                val = at.get_default(self.project)
                exported = at.export(val, self.project)
                return get_jstype_by_python_value(exported)
            return '%sBase' % at.struct.name
        if isinstance(at, ATUnion):
            # customized
            if at.union.exporter:
                val = at.get_default(self.project)
                exported = at.export(val, self.project)
                return get_jstype_by_python_value(exported)
            return '%sBase' % at.union.name
        if isinstance(at, ATBool):
            return 'boolean'
        if isinstance(at, ATEnum):
            if at.enum.export_names or not at.enum.convert_to_int:
                return 'string'
            else:
                return 'number'
        if isinstance(at, ATList):
            return 'Array.<%s>' % self.get_jstype_by_attrtype(at.element_type)
        raise Exception('unsupported type: %s %s' % (at.__class__.__name__, at.name))

    def export_struct(self, struct):
        attr_defs = []
        for attr in struct.iterate():
            js_type = self.get_jstype_by_attrtype(attr.type)
            attr_defs.append(js_generate_member(js_type, attr.name))

        return JS_CLASS_TEMPLATE % (struct.name, ',\n\n'.join(attr_defs))

    def export_union(self, union):
        attr_defs = ['    "key": ""']
        for name in union.names():
            atstruct = union.get_atstruct(name)
            attr_defs.append(js_generate_member(self.get_jstype_by_attrtype(atstruct), name))
        return JS_CLASS_TEMPLATE % (union.name, ',\n\n'.join(attr_defs))

    def export(self):
        js_classes = []
        lists = []

        for clazz in self.project.type_manager.get_clazzes():
            js_classes.append(self.export_struct(clazz.atstruct.struct))

            var_name = clazz.name[0].lower() + clazz.name[1:]
            lists.append('    /**\n'
                         '    * @type {Object.<string, kd.%sBase>}\n'
                         '    */\n'
                         '    "%ss": {}' % (clazz.name, var_name))

        for struct in self.project.type_manager.get_structs():
            js_classes.append(self.export_struct(struct))

        for union in self.project.type_manager.get_unions():
            js_classes.append(self.export_union(union))

        code = "'use strict';\n" \
               '/**\n' \
               ' * @fileoverview This file is auto-generated. DO NOT MODIFY!\n' \
               ' */\n' \
               'var kd = kd || {};\n\n'

        code += '\n\n'.join(js_classes)
        code += '\n\n'

        # ResManager
        code += 'kd.ResManagerBase = ff.Class.extend({\n' \
                '%s\n'\
                '});\n' % (',\n\n'.join(lists))

        self.save('structer_types.js', code)