# coding=utf-8
__author__ = 'Timothy'

import re
import keyword
from base import BaseExporter
from structer.stype.attr_types import (ATInt, ATStr, ATStruct, ATUnion, ATBool, ATEnum, ATFile, ATFloat, ATFolder,
                                       ATList, ATRef)


PY_CLASS_TEMPLATE = 'class %s(object):\n%s'


def get_pytype_by_python_value(val):
    type_ = type(val)
    if type_ == list:
        return 'tuple'
    return type_.__name__


def py_get_default_by_type(py_type):
    if py_type == 'int':
        return '0'
    if py_type == 'float':
        return '0.0'
    if py_type == 'str':
        return "''"
    if py_type == 'unicode':
        return "u''"
    if py_type.startswith('['):
        return '()'
    return 'None'


def py_generate_member(py_type, name, description=None):
    if keyword.iskeyword(name):
        name += '_'

    code = ''
    if description:
        code += '    u"""%s"""\n' % description
    code += '    %s = %s\n' \
            '    """:type: %s"""' % (name, py_get_default_by_type(py_type), py_type)
    return code


def get_py_class_name(name):
    return 'Res%s' % name


def get_py_var_name_by_class_name(name):
    words = re.findall('[A-Z][a-z0-9]*', name)
    assert ''.join(words) == name, 'invalid class/struct name: %s' % name
    return '_'.join(map(unicode.lower, words))


class PyCodeExporter(BaseExporter):
    def get_pytype_by_attrtype(self, at):
        if isinstance(at, (ATInt, ATBool)):
            return 'int'
        if isinstance(at, ATFloat):
            return 'float'
        if isinstance(at, ATRef):
            return get_py_class_name(at.clazz_name)
        if isinstance(at, (ATStr, ATFile, ATFolder)):
            return 'unicode'
        if isinstance(at, ATStruct):
            # # customized
            # if at.struct.exporter:
            #     # ???
            #     val = at.get_default(self.project)
            #     exported = at.export(val, self.project)
            #     return get_pytype_by_python_value(exported)
            return get_py_class_name(at.struct.name)
        if isinstance(at, ATUnion):
            # # customized
            # if at.union.exporter:
            #     val = at.get_default(self.project)
            #     exported = at.export(val, self.project)
            #     return get_pytype_by_python_value(exported)
            return get_py_class_name(at.union.name)
        if isinstance(at, ATEnum):
            if at.enum.export_names or not at.enum.convert_to_int:
                return 'str'
            else:
                return 'int'
        if isinstance(at, ATList):
            element_type = self.get_pytype_by_attrtype(at.element_type)
            if element_type == get_py_class_name('YieldItemWithRate'):
                return 'Yield'
            if element_type == get_py_class_name('CostItem'):
                return 'Cost'
            return 'tuple[%s]' % element_type
        raise Exception('unsupported type: %s %s' % (at.__class__.__name__, at.name))

    def _export_struct(self, struct):
        attr_defs = []
        for attr in struct.iterate():
            py_type = self.get_pytype_by_attrtype(attr.type)
            attr_defs.append(py_generate_member(py_type, attr.name, attr.description))

        return PY_CLASS_TEMPLATE % (get_py_class_name(struct.name), '\n\n'.join(attr_defs))

    def _export_union(self, union):
        attr_defs = ['    key = ""']
        for name in union.names():
            atstruct = union.get_atstruct(name)
            attr_defs.append(py_generate_member(self.get_pytype_by_attrtype(atstruct), name))
        return PY_CLASS_TEMPLATE % (get_py_class_name(union.name), '\n\n'.join(attr_defs))

    def _export_consts(self):
        project = self.project

        # constants
        consts = []
        # enum constants
        for enum in project.type_manager.get_enums():
            for name in enum.names:
                val = name if enum.export_names else enum.value_of(name)
                if type(val) is str or type(val) is unicode:
                    val = '"%s"' % val
                consts.append((('%s_%s' % (enum.name, name)).upper(), val))
                consts.append((None, None))
            consts.append((None, None))

        # union constants
        for union in project.type_manager.get_unions():
            enum = union.atenum.enum
            for name in enum.names:
                val = name if enum.export_names else enum.value_of(name)
                if type(val) is str or type(val) is unicode:
                    val = '"%s"' % val
                consts.append((('%s_%s' % (union.name, name)).upper(), val))
                consts.append((None, None))
            consts.append((None, None))

        consts_str = ''.join([('\n' if n is None else ('%s = %s' % (n, v))) for n, v in consts])
        return consts_str

    # def _export_object_list(self):
    #     clazz_names = []
    #     for clazz in self.project.type_manager.get_clazzes():
    #         clazz_names.append(clazz.name)
    #
    #     return 'CLASS_NAMES = [%s]\n' % (', '.join('"%s"' % name for name in clazz_names))

    def export(self):
        res_classes = []
        lists = []

        for clazz in self.project.type_manager.get_clazzes():
            res_classes.append(self._export_struct(clazz.atstruct.struct))

            var_name = get_py_var_name_by_class_name(clazz.name)
            lists.append('    %ss = {}\n'
                         '    """:type: dict[str, %s]"""\n' % (var_name, get_py_class_name(clazz.name)))

        for struct in self.project.type_manager.get_structs():
            res_classes.append(self._export_struct(struct))

        for union in self.project.type_manager.get_unions():
            res_classes.append(self._export_union(union))

        code = '# coding=utf-8\n\n'
        code += self._export_consts()
        # code += self._export_object_list()
        # code += self._export_types()

        # ResXXX
        code += '\n\n'
        code += '\n\n\n'.join(res_classes)
        code += '\n\n\n'

        # ResManager
        code += PY_CLASS_TEMPLATE % ('ResManagerBase', '\n'.join(lists))

        self.save('gen_structer_types.py', code.encode('utf-8'))
