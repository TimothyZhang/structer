# coding=utf-8
__author__ = 'Timothy'

from base import BaseExporter
from structer.stype.attr_types import (ATInt, ATStr, ATStruct, ATUnion, ATBool, ATEnum, ATFile, ATFloat, ATFolder,
                                       ATList, ATRef)


JS_KEYWORDS = {'abstract', 'arguments', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
               'continue', 'debugger', 'default', 'delete', 'do', 'double', 'else', 'enum', 'eval', 'export',
               'extends', 'false', 'final', 'finally', 'float', 'for', 'function', 'goto', 'if', 'implements',
               'import', 'in', 'instanceof', 'int', 'interface', 'let', 'long', 'native', 'new', 'null', 'package',
               'private', 'protected', 'public', 'return', 'short', 'static', 'super', 'switch', 'synchronized',
               'this', 'throw', 'throws', 'transient', 'true', 'try', 'typeof', 'var', 'void', 'volatile', 'while',
               'with', 'yield'}


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


def js_get_default_by_type(js_type, js_val=None):
    if js_val is not None:
        if isinstance(js_val, (str, unicode)):
            return "'%s'" % js_val
        return js_val

    if js_type == 'number':
        return '0'
    if js_type == 'string':
        return "''"
    if js_type.startswith('Array'):
        return '[]'
    if js_type.startswith('Object'):
        return {}
    return 'null'


def is_js_keyword(name):
    return name in JS_KEYWORDS


def js_get_safe_var_name(name):
    if is_js_keyword(name):
        name = '_%s' % name

    if '.' not in name:
        name = 'var %s' % name

    return name


class JsCodeGenerator(object):
    def __init__(self, root_class='ff.Class', indent=0, indents=4):
        self._root_class = root_class
        self._indent = indent
        self._indents = indents

        self._lines = []
        self._is_first_member = True
        self._next_iterator = 0

    def _get_next_iterator(self):
        self._next_iterator += 1
        return 'i%s' % self._next_iterator

    def add_line(self, line=None):
        if line is None:
            self._lines.append('')
        else:
            self._lines.append(' ' * self._indent * self._indents + line)

    def add_empty_lines(self, count=1):
        for i in xrange(count):
            self.add_line()

    def begin_file(self):
        self.add_line("'use strict';")

    def end_file(self):
        pass

    def begin_comment(self):
        self.add_line('/**')

    def add_block_comment(self, tag, description):
        if tag:
            self.add_line(' *@%s %s' % (tag, description))
        else:
            self.add_line(' *%s' % description)

    def add_type_comment(self, type_):
        self.add_block_comment('type', '{%s}' % type_)

    def end_comment(self):
        self.add_line(' */')

    def indent(self):
        self._indent += 1

    def unindent(self):
        self._indent -= 1

    def _add_comment_for_var(self, type_=None, comment=None):
        if not (type_ or comment):
            return

        self.begin_comment()
        if comment:
            self.add_block_comment('', comment)
        if type_:
            self.add_type_comment(type_)
        self.end_comment()

    def add_var(self, name, val=None, expr=None, type_=None, comment=None):
        self._add_comment_for_var(type_, comment)
        if not expr:
            expr = js_get_default_by_type(type_, val)

        name = js_get_safe_var_name(name)
        self.add_line('%s = %s;' % (name, expr))

    def add_member_var(self, name, val=None, expr=None, type_=None, comment=None):
        self._add_comma_for_prev_member()
        self._add_comment_for_var(type_, comment)

        if not expr:
            expr = js_get_default_by_type(type_, val)

        if is_js_keyword(name):
            name = '_%s' % name
        self.add_line('%s: %s' % (name, expr))

    def begin_class(self, name, base_class=None):
        if not base_class:
            base_class = self._root_class

        name = js_get_safe_var_name(name)
        self.add_line('%s = %s.extend({' % (name, base_class))
        self._is_first_member = True
        self._indent += 1

    def end_class(self):
        self._indent -= 1
        self.add_line('});')
        self.add_line()

    def _add_comma_for_prev_member(self):
        is_first = self._is_first_member
        self._is_first_member = False

        if is_first:
            return

        for i in xrange(len(self._lines)-1, -1, -1):
            if self._lines[i]:
                self._lines[i] += ','
                self.add_empty_lines()
                break

    def begin_method(self, name, *params):
        self._add_comma_for_prev_member()
        self.add_line('%s: function (%s) {' % (name, ','.join(params)))
        self._indent += 1

    def end_method(self):
        self._indent -= 1
        self.add_line('}')

    def begin_function(self, name, *params):
        name = js_get_safe_var_name(name)
        self.add_line('%s = function(%s) {' % (name, ','.join(params)))
        self.indent()

    def end_function(self):
        self.unindent()
        self.add_line('};')

    def begin_for_loop_array(self, array):
        i = self._get_next_iterator()
        self.add_line('for (var %s=0; i<%s.length; %s++) {' % (i, array, i))
        self._indent += 1
        return i

    def end_for_loop(self):
        self._indent -= 1
        self.add_line('}')

    def get_code(self):
        return '\n'.join(self._lines).encode('utf-8')


class CustomCodeSearcher(object):
    def __init__(self):
        self._results = []

    def search(self, clazz):
        self._search((), clazz.atstruct)

    def _search(self, path, at):
        """
        :param path:
        :type path: tuple[str]
        :param at:
        :type at: AttrType
        :return:
        :rtype:
        """
        if isinstance(at, ATList):
            if at.element_type.name == 'CostItem&':
                self._results.append((path, 'Cost'))
            elif at.element_type.name == 'YieldItemWithRate@':
                self._results.append((path, 'Yield'))
            else:
                self._search(path + ('*',), at.element_type)
        elif isinstance(at, ATStruct):
            for attr in at.struct.iterate():
                self._search(path + (attr.name,), attr.type)

    def iterate(self):
        for r in self._results:
            yield r


class CustomCodeGenerator(object):
    def __init__(self):
        self._js_code_gen = None
        """:type: JsCodeGenerator"""

        self._class_name = None
        self._var_stack = []
        self._codes = []
        self._temp_var_index = 0

    def _reset(self):
        self._js_code_gen = None
        self._class_name = None
        self._var_stack = []
        self._codes = []
        self._next_iter_index = 0

    def _get_next_temp_var(self):
        self._temp_var_index += 1
        return 'tmp%s' % self._temp_var_index

    def _push_var(self, var):
        self._var_stack.append(var)

    def _pop_var(self):
        self._var_stack.pop()

    @property
    def current_var(self):
        return self._var_stack[-1]

    def generate(self, js_code_gen, root_var, path, class_name):
        self._reset()
        self._js_code_gen = js_code_gen
        self._class_name = class_name
        self._var_stack.append(root_var)
        self._generate(path)
        return '\n'.join(self._codes)

    def _generate(self, path):
        if not path:
            self._js_code_gen.add_line('%s = %s(%s);' % (self.current_var, self._class_name, self.current_var))
            return

        tmp_var = None
        if '[' in self.current_var:
            tmp_var = self._get_next_temp_var()
            self._js_code_gen.add_var(tmp_var, expr=self.current_var)
            self._push_var(tmp_var)


        if path[0] == '*':
            it = self._js_code_gen.begin_for_loop_array(self.current_var)
            self._push_var('%s[%s]' % (self.current_var, it))
            self._generate(path[1:])
            self._pop_var()
            self._js_code_gen.end_for_loop()
        elif isinstance(path[0], int):
            self._push_var('%s[%s]' % (self.current_var, path[0]))
            self._generate(path[1:])
            self._pop_var()
        else:
            self._push_var('%s["%s"]' % (self.current_var, path[0]))
            self._generate(path[1:])
            self._pop_var()

        if tmp_var:
            self._pop_var()


class JsCodeExporter(BaseExporter):
    _js_code_gen = JsCodeGenerator()

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
            return 'kd.Res%s' % at.struct.name
        if isinstance(at, ATUnion):
            # customized
            if at.union.exporter:
                val = at.get_default(self.project)
                exported = at.export(val, self.project)
                return get_jstype_by_python_value(exported)
            return 'kd.Res%s' % at.union.name
        if isinstance(at, ATBool):
            return 'boolean'
        if isinstance(at, ATEnum):
            if at.enum.export_names or not at.enum.convert_to_int:
                return 'string'
            else:
                return 'number'
        if isinstance(at, ATList):
            print 'ele name:', at.element_type.name
            if at.element_type.name == 'CostItem&':
                return 'kd.Cost'
            if at.element_type.name == 'YieldItemWithRate@':
                return 'kd.Yield'
            return 'Array.<%s>' % self.get_jstype_by_attrtype(at.element_type)
        raise Exception('unsupported type: %s %s' % (at.__class__.__name__, at.name))

    def _export_struct(self, struct):
        cg = self._js_code_gen
        cg.begin_class('kd.Res%s' % struct.name)

        for attr in struct.iterate():
            js_type = self.get_jstype_by_attrtype(attr.type)
            cg.add_member_var(attr.name, type_=js_type, comment=attr.description)

        cg.end_class()

    def _fix_custom_code(self, clazz):
        cg = self._js_code_gen
        ccs = CustomCodeSearcher()
        ccs.search(clazz)

        ccg = CustomCodeGenerator()
        cg.begin_function('kd.fixRes%s' % clazz.name, 'obj')
        for path, custom_class in ccs.iterate():
            ccg.generate(cg, 'obj', path, 'kd.%s' % custom_class)
        cg.end_function()

    def _export_union(self, union):
        cg = self._js_code_gen
        cg.begin_class('kd.Res%s' % union.name)

        cg.add_member_var('key', val='')
        for name in union.names():
            atstruct = union.get_atstruct(name)
            cg.add_member_var(name, type_=self.get_jstype_by_attrtype(atstruct))
        cg.end_class()

    def _export_consts(self):
        project = self.project
        cg = self._js_code_gen

        # enum constants
        for enum in project.type_manager.get_enums():
            for name in enum.names:
                val = name if enum.export_names else enum.value_of(name)
                cg.add_var('kd.%s_%s' % (enum.name.upper(), name.upper()), val=val)
            cg.add_line()

        # union constants
        for union in project.type_manager.get_unions():
            enum = union.atenum.enum
            for name in enum.names:
                val = name if enum.export_names else enum.value_of(name)
                if type(val) is str or type(val) is unicode:
                    val = '"%s"' % val
                cg.add_var('kd.%s_%s' % (union.name.upper(), name.upper()), val=val)
            cg.add_line()

    def export(self):
        cg = self._js_code_gen
        cg.begin_file()

        # 文件头
        cg.begin_comment()
        cg.add_block_comment('fileoverview', 'This file is auto-generated. DO NOT MODIFY!')
        cg.end_comment()
        cg.add_var('kd', expr='kd || {}')
        cg.add_empty_lines()

        # 常量
        self._export_consts()

        containers = []
        # class
        for clazz in self.project.type_manager.get_clazzes():
            self._export_struct(clazz.atstruct.struct)
            self._fix_custom_code(clazz)
            cg.add_empty_lines()

            var_name = clazz.name[0].lower() + clazz.name[1:] + 's'
            type_ = 'Object.<string, kd.Res%s>' % clazz.name
            containers.append((var_name, type_))

        # struct
        for struct in self.project.type_manager.get_structs():
            self._export_struct(struct)

        # union
        for union in self.project.type_manager.get_unions():
            self._export_union(union)

        # ResManager
        cg.begin_class('kd.ResManagerBase')
        for name, type_ in containers:
            cg.add_member_var(name, type_=type_)
        cg.end_class()

        self.save('gen_structer_types.js', cg.get_code())
