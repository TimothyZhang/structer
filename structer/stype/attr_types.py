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


# -*- coding: utf-8 -*-
import types
import copy
import string
import re
import os

from structer import log
from structer.util import get_absolute_path


"""
verifier: is a piece of python code which contains the body of a function.
 
    The code will be wrapped into a temporary function, and executed with following arguments. 
    If something was wrong, call error().
    
    NOTE: indent with 4 SPACES, TABs will be replaced with 4 spaces.
    
    Args:
        t: the AttrType instance
        v: the value
        p: the project
        error: a function to report errors. use like this:
            error(msg)
            error(fmt, *args)  -- equal to but maybe faster than error(fmt % tuple(args)) 
                 
    For example:
        #verifier code starts
        # we want the number to be even, OR >= 10
        if v%2==0:
            error('Needs an even number, but got an odd one: %s', v)
            return
        if v<10:
            error('Must greater or equal than 10, got: %s', v)
        #verifier code end
"""


def make_verifier(src):
    """Make a verifier function by source code
    
    Returns:
        a function object
    """
    src = src.replace('\t', ' ' * 4)
    # indent
    src = '\n'.join([' ' * 4 + l for l in src.split('\n')])
    src = 'def _verifier(t,v,p,error):\n' + src

    l = {}
    exec (src, {}, l)
    return l['_verifier']


"""
exporter: function body to export the AttrType
    This function will be called after default export function been called.

    Args:
        v: stored value
        d: originally exported data, which was exported by default export function.
        t: AttrType
        p: Project
        
    Returns:
        exported data
"""


def make_exporter(src):
    """Similar to make_exporter"""
    src = src.replace('\t', ' ' * 4)
    # indent
    src = '\n'.join([' ' * 4 + l for l in src.split('\n')])
    src = 'def _exporter(v,d,t,p):\n' + src

    l = {}
    exec (src, {}, l)
    return l['_exporter']


class Ref(object):
    def __init__(self, clazz_name, uuid):
        self.clazz_name = clazz_name
        self.uuid = uuid


class AttrVerifyError(object):
    def __init__(self, path, msg, *args):
        self.path = path
        self.msg = msg
        self.args = args

    def str(self):
        return self.msg % tuple(self.args)


class AttrVerifyLogger(object):
    def __init__(self, root_path='', uuid=None):
        self._path = root_path
        self._uuid = uuid

        # [(path, msg, args), ...]
        self._errors = []

    def push(self, path):
        self._path += "/" + path

    def pop(self):
        self._path = self._path.rsplit('/', 1)[0]

    def error(self, msg, *args):
        self._errors.append(AttrVerifyError(self._path, msg, *args))

    def has_error(self):
        return len(self._errors) > 0

    @property
    def errors(self):
        return self._errors

    def log_all(self, project, with_path=True):
        fs_path = ''
        if self._uuid:
            obj = project.object_manager.get_object(self._uuid)
            if obj:
                from structer import fs_util
                fs_path = fs_util.get_object_path(project, obj)

        for e in self._errors:
            log.error(u'%s %s %s %s', project.name, fs_path, e.path, e.str())


class AttrType(object):
    _default = None
    _name = None
    _verifier = None
    _exporter = None

    def __init__(self, name=None, verifier=None, exporter=None):
        if name:
            self._name = name
        else:
            self._name = self.__class__.__name__[2:]

        if verifier:
            self._verifier = make_verifier(verifier)

        if exporter:
            self._exporter = make_exporter(exporter)

    @property
    def name(self):
        u"""Get type name."""
        return self._name

    def get_refs(self, val, project):
        u"""Gets all objects reference by me

            return: [Ref, ...]
        """
        return []

    def verify(self, val, project, recurse=True, vlog=None):
        u"""verify the value"""
        if vlog is None:
            vlog = AttrVerifyLogger()

        self._verify(val, project, recurse, vlog)

        if self._verifier:
            try:
                self._verifier(self, val, project, vlog.error)
            except Exception, e:
                log.error(e, 'error in verifier of %s', self.name)
                vlog.error('verifier error: %s %s', e.__class__.__name__, str(e))

        return vlog

    def _verify(self, val, project, recurse=True, vlog=None):
        u"""override me"""
        pass

    def str(self, val, project):
        return unicode(val)

    def export(self, val, project):
        d = self._export(val, project)

        if self._exporter:
            d = self._exporter(val, d, self, project)

        return d

    def _export(self, val, project):
        return val

    def fix(self, val, fixer, project):
        return fixer(self, val, project)

    def compare(self, v1, v2):
        """Compares two values of this type
        
        By default just compare them with native comparator. But it's not correct for ATStruct. see ATStruct.compare()
        """
        return cmp(v1, v2)

    def get_default(self, project):
        return copy.deepcopy(self._default)

    def __unicode__(self):
        return self.name


class ATInt(AttrType):
    def __init__(self, min=-0x80000000, max=0x7FFFFFFF, default=None, **kwargs):
        AttrType.__init__(self, **kwargs)

        assert min <= max
        self.min = min
        self.max = max

        if default is None:
            default = 0
            if default < self.min:
                default = self.min
            if default > self.max:
                default = self.max
        self._default = default

    def _verify(self, val, project, recurse=True, vlog=None):
        if type(val) not in (types.IntType, types.LongType):
            vlog.error('invalid type for %s: %s', self.name, type(val))
            return

        if not self.min <= val <= self.max:
            vlog.error('%s value out of range(%s,%s) : %s', self.name, self.min, self.max, val)
            return


class ATBool(ATInt):
    def __init__(self, default=0, **kwargs):
        ATInt.__init__(self, 0, 1, default, **kwargs)

    def str(self, val, project):
        return 'YES' if val else 'NO'


class ATFloat(AttrType):
    def __init__(self, min=None, max=None, default=None, **kwargs):
        AttrType.__init__(self, **kwargs)

        assert min <= max
        self.min = min
        self.max = max

        if default is None:
            default = 0.0
            if self.min is not None and default < self.min:
                default = self.min
            if self.max is not None and default > self.max:
                default = self.max
        self._default = default

    def _verify(self, val, project, recurse=True, vlog=None):
        if not isinstance(val, float) and not isinstance(val, int):
            vlog.error('invalid type for %s: %s', self.name, type(val))
            return

        if (self.min is not None and self.min > val) or (self.max is not None and self.max < val):
            vlog.error('%s value out of range(%s,%s) : %s', self.name, self.min, self.max, val)
            return


class ATStr(AttrType):
    """value: unicode"""

    def __init__(self, minlen=0, maxlen=0x7FFFFFFF, default=u"", multiline=False, regex='', **kwargs):
        AttrType.__init__(self, **kwargs)

        assert 0 <= minlen <= maxlen
        self.minlen = minlen
        self.maxlen = maxlen
        self._default = default

        self._regex = regex
        self._pattern = None
        if regex:
            self._pattern = re.compile(regex)

    def _verify(self, val, project, recurse=True, vlog=None):
        if type(val) is not unicode:
            vlog.error('invaild type for %s: %s', self.name, type(val))
            return

        if not self.minlen <= len(val) < self.maxlen:
            vlog.error('%s length out of range(%s,%s): %s', self.name, self.minlen, self.maxlen, len(val))

        if self._pattern:
            if not self._pattern.match(val):
                vlog.error('regex not match: %s', self._regex)


class ATFile(AttrType):
    """value: str
    
    If possible, path is relative to project root, otherwise it's absolute.
    
    Attributes:
        extensions: list of allowed file extensions. If empty, any extension is allowed.
        optional: bool. True if file could be empty.
    """

    def __init__(self, extensions, optional, **kwargs):
        AttrType.__init__(self, **kwargs)

        self.extensions = extensions
        self.optional = optional

        self._default = u''

    def _verify(self, val, project, recurse=True, vlog=None):
        if not val:
            if not self.optional:
                vlog.error('No file specified.')
            return

        if type(val) is not unicode:
            vlog.error('invalid type for %s: %s', self.name, type(val))
            return

        if len(self.extensions):
            ext_match = False
            for ext in self.extensions:
                if val.endswith(ext):
                    ext_match = True
                    break
            if not ext_match:
                vlog.error('invalid file type: %s', val)

        path = get_absolute_path(val, project.path)
        if not os.path.exists(path):
            vlog.error('file not exists: %s', path)

        if os.path.isdir(path):
            vlog.error('not a file: %s', path)


class ATFolder(AttrType):
    def __init__(self, optional, **kwargs):
        AttrType.__init__(self, **kwargs)
        self.optional = optional

        self._default = u''

    def _verify(self, val, project, recurse=True, vlog=None):
        if not val:
            if not self.optional:
                vlog.error('No folder specified.')
            return

        if type(val) is not unicode:
            vlog.error("Invalid type for %s: %s", self.name, type(val))
            return

        path = get_absolute_path(val, project.path)
        if not os.path.exists(path):
            vlog.error('Folder not exists: %s', path)
            return

        if not os.path.isdir(path):
            vlog.error('Not a folder: %s', path)
            return


# class ATI18N(AttrType):
# """value: {language_code: text}"""
#     def __init__(self, minlen=0, maxlen=0x7FFFFFFF):
#         assert 0 <= minlen <= maxlen
#         self._minlen = minlen
#         self._maxlen = maxlen
#     
#     def _verify(self, val, project, recurse=True, log=None):
#         if type(val) is not dict:
#             log.error('invalid type for %s: %s', self.name, type(val))
#             return
#         
#         languages = project.languages
#         for lang in languages:
#             if lang not in val:
#                 log.error('language "%s" is missing', lang)     
#                 
#         for lang, text in val.iteritems():
#             if lang not in languages:
#                 log.warn('unknown language in %s: %s', self.name, lang)
#             if not self._minlen <= text <= self._maxlen:
#                 log.error('%s length out of range(%s,%s): %s', self.name, self._minlen, self._maxlen, len(text))
#         
#     def get_default(self, project):        
#         return dict([(lang, u'') for lang in project.languages])            


def _is_list_unique(l, cmp_):
    for i in xrange(len(l)):
        for j in xrange(i + 1, len(l)):
            if cmp_(l[i], l[j]) == 0:
                return False
    return True


def _verify_list_items(element_type, unique, unique_attrs, val, project, recurse, vlog):
    if unique:
        try:
            tmp = set(val)
            if len(tmp) != len(val):
                vlog.error('list not unique')
        except TypeError:  # unhashable
            if not _is_list_unique(val, lambda x, y: element_type.compare(x, y)):
                vlog.error('list not unique')

    if recurse:
        for i, element in enumerate(val):
            vlog.push(str(i))
            try:
                element_type.verify(element, project, recurse, vlog)
            finally:
                vlog.pop()

    verify_list_unique_attrs(element_type, unique_attrs, val, project, vlog)


def verify_list_unique_attrs(element_type, unique_attrs, val, project, vlog):
    # unique attrs
    if unique_attrs:
        for attr_name in unique_attrs:
            values = []
            duplicates = []  # duplicated values
            for element in val:
                value = element_type.get_attr_value(attr_name, element, project)
                if value in values:
                    if value not in duplicates:  # only repeat 1 error for 1 value
                        vlog.error('duplicated attribute "%s": %s', attr_name, value)
                        duplicates.append(value)
                else:
                    values.append(value)


class ATList(AttrType):
    """value: list
    
        @todo: support primary key(s) ?
    """

    def __init__(self, element_type, unique=False, minlen=0, maxlen=0x7FFFFFFF, delimiter='; ', unique_attrs=(),
                 **kwargs):
        """
           unique_attrs: If element type is ATStruct, attributes in unique_attrs must be unique.
        """
        AttrType.__init__(self, "[%s]" % element_type.name, **kwargs)

        self.element_type = element_type
        self._unique = unique
        self._minlen = minlen
        self._maxlen = maxlen
        self._delimiter = delimiter
        self._unique_attrs = unique_attrs

        if unique_attrs and type(element_type) is not ATStruct:
            log.error('"unique_attrs" can only be applied to list of structs')

        self._default = []

    @property
    def minlen(self):
        return self._minlen

    @property
    def maxlen(self):
        return self._maxlen

    @property
    def unique(self):
        return self._unique

    def _verify(self, val, project, recurse=True, vlog=None):
        if type(val) is not list:
            vlog.error('invalid type for %s: %s', self.name, type(val))
            return

        if not self._minlen <= len(val) <= self._maxlen:
            vlog.error('%s length out of range(%s,%s): %s', self.name, self._minlen, self._maxlen, len(val))

        _verify_list_items(self.element_type, self._unique, self._unique_attrs, val, project, recurse, vlog)

    def get_refs(self, val, project):
        if type(val) is not list:
            return []

        return sum([self.element_type.get_refs(i, project) for i in val], [])

    def str(self, val, project):
        strs = [self.element_type.str(i, project) for i in val]
        return self._delimiter.join(strs)

    def compare(self, v1, v2):
        if type(v1) != list:
            return -1
        if type(v2) != list:
            return 1

        r = cmp(len(v1), len(v2))
        if r != 0:
            return r

        for i in xrange(len(v1)):
            r = self.element_type.compare(v1[i], v2[i])
            if r != 0:
                return r

        return 0

    def _export(self, val, project):
        return [self.element_type.export(element, project) for element in val]

    def fix(self, val, fixer, project):
        newval = fixer(self, val, project)
        if val is None:
            return
        return [self.element_type.fix(element, fixer, project) for element in newval]


# class ATDict(AttrType):
#     """value: dict"""
#     def __init__(self, element_type, unique=False, minlen=0, maxlen=0x7FFFFFFF, unique_attrs=[]):
#         self.element_type = element_type
#         self._unique = unique            # whether value is unique
#         self._minlen = minlen
#         self._maxlen = maxlen
#         self._unique_attrs = unique_attrs
# 
#         if unique_attrs and type(element_type)!=ATStruct:
#             log.error('"unique_attrs" can only be applied to dict of structs')
#            
#         self._default = {}
#         self._name = "{%s}" % self.element_type.name
#         
#     def _verify(self, val, project):
#         if type(val) is not dict:
#             log.error('invalid type for %s: %s', self.name, type(val))
#             return
#         
#         if not self._minlen <= len(val) <= self._maxlen:
#             log.error('%s length out of range(%s,%s): %s', self.name, self._minlen, self._maxlen, len(val))
# 
#         _verify_list_items(self.element_type, self._unique, self._unique_attrs, val.values(), project)
#         
# 
#     def get_refs(self, val, project):
#         return sum([self.element_type.get_refs(i, project) for i in val.itervalues()], [])
#     
#     def str(self, val, project):
#         strs = ['%s: %s'%(n, self.element_type.str(v, project)) for n,v in val.itervalues()]
#         #todo: delimiter
#         return '\n'.join(strs)


class ATRef(AttrType):
    """value: uuid or None"""

    def __init__(self, class_name, nullable=False, **kwargs):
        AttrType.__init__(self, '%s*' % class_name, **kwargs)

        self._clazz_name = class_name
        self._nullable = nullable

        self._default = u''

    @property
    def nullable(self):
        return self._nullable

    @property
    def clazz_name(self):
        return self._clazz_name

    def get_ref(self, val, project):
        obj = project.object_manager.get_object(val, self.clazz_name)
        return obj

    def _verify(self, val, project, recurse=True, vlog=None):
        if not val:
            if not self.nullable:
                vlog.error("null reference: %s", self.str(val, project))
            return

        if type(val) is not unicode:
            vlog.error('invalid type for %s: %s', self.name, type(val))
            return

        obj = project.object_manager.get_object(val, self.clazz_name)
        if not obj:
            vlog.error('invalid reference: %s', self.str(val, project))

    def get_refs(self, val, project):
        if val:
            return [Ref(self.clazz_name, val)]
        return []

    def str(self, val, project):
        if val:
            obj = project.object_manager.get_object(val, self.clazz_name)
            if obj:
                return obj.get_label()
        return "%s<%s>" % (self.clazz_name, val)

    def _export(self, val, project):
        # todo: export id?
        if val:
            obj = project.object_manager.get_object(val, self.clazz_name)
            if obj:
                return obj.id

        # null ref.
        clazz = project.type_manager.get_clazz_by_name(self.clazz_name)
        assert clazz
        atid = clazz.atstruct.struct.get_attr_by_name('id')
        assert atid

        if type(atid.type) is ATStr:
            return u''

        if type(atid.type) is ATInt:
            return -1

        return None


class ATEnum(AttrType):
    """value: enum itemname(str)"""

    def __init__(self, enum, default=None, filter=(), **kwargs):
        """
        Args:
            enum: Instance of Enum
            default: Name of default value
            filter: list of str. If not empty, only names in filter is allowed to use.
        """
        AttrType.__init__(self, '%s#' % enum.name, **kwargs)

        self.enum = enum
        assert not default or enum.has_name(default), u'ATEnum %s' % enum.name

        if not self.enum.has_name(default):
            if default:
                log.error('invalid default value for enum %s: %s' % (self.name, default))
            default = enum.names[0]
        self._default = default

        if filter:
            for name in filter:
                if not enum.has_name(name):
                    log.error('invalid filter for enum %s: %s', self.name, name)

        self._filter = filter

    @property
    def names(self):
        return self._filter if self._filter else self.enum.names

    @property
    def labels(self):
        if self._filter:
            return [self.enum.label_of(name) for name in self._filter]
        return self.enum.labels

    def get_name_by_index(self, index):
        if self._filter:
            return self._filter[index]
        return self.enum.get_name_by_index(index)

    def _verify(self, val, project, recurse=True, vlog=None):
        if type(val) is not unicode:
            vlog.error('invaild type for %s: %s', self.name, type(val))
            return

        if not self.enum.has_name(val):
            vlog.error('invalid enum value for %s: %s', self.name, val)
        else:
            if self._filter:
                if val not in self._filter:
                    vlog.error('enum value disabled for %s: %s', self.name, val)

    def str(self, val, project):
        return self.enum.label_of(val)

    def _export(self, val, project):
        if self.enum.export_names:
            return val

        return self.enum.value_of(val)


class ATUnion(AttrType):
    """ value: [itemname(str), {...}]"""

    atenum = None

    def __init__(self, union, filter=(), **kwargs):
        """
        :param Union union:
        :param filter:
        :param kwargs:
        :return:
        """
        AttrType.__init__(self, '%s&' % union.name, **kwargs)
        self.union = union

        # BE CAREFULL! editor_types.u_type was created with an empty union!!!
        # It's NOT used, since get_default() was overridden
        # self._default = ['', {}]  # it's an invalid value

        if filter:
            for name in filter:
                assert union.get_atstruct(name) is not None

        self._filter = filter
        # self.update_union()
        self.__atenum = None

    # def update_union(self):
    #     self.atenum = ATEnum(self.union.enum, filter=self._filter)
    @property
    def atenum(self):
        if self.__atenum is None:
            self.__atenum = ATEnum(self.union.enum, filter=self._filter)
        return self.__atenum

    def get_default(self, project):
        key = self.atenum.names[0]
        atstruct = self.union.get_atstruct(key)
        val = atstruct.get_default(project)
        return {'key': key, key: val}

    def get_value_type(self, val):
        atstruct = self.union.get_atstruct(val['key'])
        return atstruct

    def get_value(self, val):
        return val[val['key']]

    def _verify(self, val, project, recurse=True, vlog=None):
        if not isinstance(val, dict) or 'key' not in val or val['key'] not in val or not isinstance(val[val['key']],
                                                                                                    dict):
            vlog.error("invalid data structure for %s: %s", self.name, val)
            return

        atstruct = self.union.get_atstruct(val['key'])
        if not atstruct:
            vlog.error('invalid union item for %s:% s', self.name, val['key'])
            return
        else:
            if self._filter:
                if val['key'] not in self._filter:
                    vlog.error('union value disabled for %s: %s', self.name, val['key'])
                    return

        # check struct
        if recurse:
            atstruct.verify(val[val['key']], project, recurse, vlog)

    def compare(self, v1, v2):
        r = cmp(v1['key'], v2['key'])
        if r != 0:
            return r

        atstruct = self.union.get_atstruct(v1['key'])
        # if not atstruct:
        #     # error...
        #     return cmp(v1[v1['key']], v2[v2['key']])

        for attr in atstruct.struct.iterate():
            r = attr.type.compare(v1[v1['key']].get(attr.name), v2[v2['key']].get(attr.name))
            if r != 0:
                return r
        return 0

    def get_refs(self, val, project):
        vlog = self.verify(val, project)
        if vlog.has_error():
            # self.verify(val, project)
            vlog.log_all(project)
            # raise Exception(vlog.errors)
            return []

        atstruct = self.union.get_atstruct(val['key'])
        return atstruct.get_refs(val[val['key']], project)

    def str(self, val, project):
        # todo: need verify?

        atstruct = self.union.get_atstruct(val['key'])
        # todo: ...
        return self.atenum.enum.label_of(val['key']) + ": " + atstruct.str(val[val['key']], project)

    def _export(self, val, project):
        # todo: need a flag

        exported_key = key = val['key']
        if not self.union.export_names:
            exported_key = self.atenum.enum.value_of(val['key'])

        atstruct = self.union.get_atstruct(key)
        exported_data = atstruct.export(val[val['key']], project)

        return [exported_key, exported_data]
        # return {'key': key, key: exported_data}

    def fix(self, val, fixer, project):
        newval = fixer(self, val, project)

        atstruct = self.union.get_atstruct(newval['key'])
        newval[newval['key']] = atstruct.fix(newval[newval['key']], fixer, project)

        return newval


class ATStruct(AttrType):
    """value: {attrname: attrvalue}"""

    def __init__(self, struct, str_template=None, **kwargs):
        """
        :param Struct struct:
        :param str_template:
        :param kwargs:
        :return:
        """
        AttrType.__init__(self, '%s@' % struct.name, **kwargs)

        self.__struct = struct
        self._str_template = string.Template(str_template) if str_template else None

    @property
    def str_template(self):
        if self._str_template:
            return self._str_template
        return self.__struct.str_template

    @property
    def struct(self):
        return self.__struct

    def has_attr(self, name):
        return self.__struct.has_attr(name)

    def get_attr(self, name):
        return self.__struct.get_attr_by_name(name)

    def get_attr_value(self, name, val, project):
        """Get the attribute value"""
        # NOTE: DO NOT recurse, it would be slow, and returned data structer might be unexpected
        # attr = self.get_attr(name)
        # return attr.get_value(val[name], project)
        r = val.get(name)
        # if r is None:
        #     attr = self.get_attr(name)
        #     r = attr.type.get_default(project)
        return r

    #        if name in val:
    #            return val[name]
    #
    #        attr = self.struct.get_attr_by_name(name)
    #        if attr:
    #            return attr.type.get_default(project)

    def get_default(self, project):
        return dict([(attr.name, attr.type.get_default(project)) for attr in self.struct.iterate()])

    def _verify(self, val, project, recurse=True, vlog=None):
        if type(val) is not dict:
            vlog.error("invalid type for %s: %s", self.name, type(val))
            return

        if recurse:
            for attr in self.struct.iterate():
                vlog.push(attr.name)
                try:
                    attr.type.verify(val.get(attr.name), project, recurse, vlog)
                finally:
                    vlog.pop()

    def compare(self, v1, v2):
        """ATStruct values are dicts. But some of them might contains redundant key/values if any Struct attr was removed.         
        """
        if type(v1) is not dict:
            return -1
        if type(v2) is not dict:
            return 1

        for attr in self.struct.iterate():
            r = attr.type.compare(v1.get(attr.name), v2.get(attr.name))
            if r != 0:
                return r
        return 0

    def get_refs(self, val, project):
        if type(val) is not dict:
            return []
        return sum([attr.type.get_refs(val.get(attr.name), project) for attr in self.struct.iterate()], [])

    def str(self, val, project):
        if type(val) is not dict:
            return unicode(val)

        # templating
        st = self.str_template
        if st:
            return st.safe_substitute(_StructTemplateMap(self, val, project))

        # dictstr
        return unicode(
            dict([(attr.name, attr.type.str(val.get(attr.name), project)) for attr in self.struct.iterate()]))

    def _export(self, val, project):
        r = {}
        for attr in self.struct.iterate():
            v = val.get(attr.name)
            r[attr.name] = attr.type.export(v, project)
        return r

    def fix(self, val, fixer, project):
        newval = fixer(self, val, project)
        for attr in self.struct.iterate():
            v = newval.get(attr.name)
            newval[attr.name] = attr.type.fix(v, fixer, project)
        return newval


class _StructTemplateMap(object):
    """ For faster speed
        Only get attr of attributes when requested
    """

    def __init__(self, atstruct, val, project):
        self._atstruct = atstruct
        self._val = val
        self._project = project

        self._cache = {}

    def __getitem__(self, key):
        v = self._cache.get(key)
        if v is not None:
            return v

        attr = self._atstruct.get_attr(key)
        v = attr.type.str(self._val[key], self._project)

        self._cache[key] = v
        return v

