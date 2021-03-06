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

"""
Defines all the types needed by TypeEditor.

5 Clazzes are defined:    
    Clazz: to define all Clazzes 
    Enum
    Struct
    Union
    Setting: project setting. Only 1 object is allowd
"""

from attr_types import *
from composite_types import *
from clazz import Clazz
from structer.util import utc_str_to_timestamp

CLAZZ_NAME_CLAZZ = u"Class"
CLAZZ_NAME_ENUM = u"Enum"
CLAZZ_NAME_STRUCT = u"Struct"
CLAZZ_NAME_UNION = u"Union"
CLAZZ_NAME_SETTING = u"Setting"
CLAZZ_NAME_PREDEFINED_TYPE = u'PredefinedType'

# structs for define AttrTypes

INT_MAX = 2**63-1
INT_MIN = -2**63
s_int_verifier = u"""
if not v['min']<=v['default']<=v['max']:
    error(u'default value out of range. %s<=%s<=%s' % (v['min'], v['default'], v['max']))
"""
s_int = ATStruct(Struct(u"Int", [Attr("min", ATInt(min=INT_MIN, max=INT_MAX, default=-0x80000000)),
                                 Attr("max", ATInt(min=INT_MIN, max=INT_MAX, default=0x7FFFFFFF)),
                                 Attr("default", ATInt(default=0)),
                                 Attr("verifier", ATStr(multiline=True, syntax='python')),
                                 Attr("exporter", ATStr(multiline=True, syntax='python'))],
                        str_template=u"Int ${default}, [${min}, ${max}]"),
                 verifier=s_int_verifier,
                 )

s_time = ATStruct(
    Struct(u"Time",
           [
               Attr("min", ATTime(min=utc_str_to_timestamp('1970-01-01 00:00:00'),
                                  max=utc_str_to_timestamp('2200-01-01 00:00:00'),
                                  default=utc_str_to_timestamp('1970-01-01 00:00:00'))),
               Attr("max", ATTime(min=utc_str_to_timestamp('1970-01-01 00:00:00'),
                                  max=utc_str_to_timestamp('2200-01-01 00:00:00'),
                                  default=utc_str_to_timestamp('2200-01-01 00:00:00'))),
               Attr("timezone", ATDuration(min=-12*3600, max=14*3600, default=0), u'Timezone offset(seconds)')
           ]
    )
)

s_duration = ATStruct(
    Struct(u"Duration",
           [
               Attr("min", ATDuration(min=0, max=3600 * 24 * 99999, default=0)),
               Attr("max", ATDuration(min=0, max=3600 * 24 * 99999, default=3600 * 24 * 99999)),
           ]
    )
)

s_bool = ATStruct(Struct(u"Bool", [Attr("default", ATBool()),
                                   Attr("verifier", ATStr(multiline=True, syntax='python')),
                                   Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                  str_template=u"Bool ${default}")

s_float = ATStruct(Struct(u"Float", [Attr("min", ATFloat(default=-9999999999999.9)),
                                     Attr("max", ATFloat(default=9999999999999.9)),
                                     Attr("default", ATFloat(default=0.0)),
                                     Attr("verifier", ATStr(multiline=True, syntax='python')),
                                     Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                   str_template=u"Float ${default}, [${min}, ${max}]")

s_str = ATStruct(Struct(u"Str", [Attr("minlen", ATInt(default=0)),
                                 Attr("maxlen", ATInt(default=1024)),
                                 Attr("default", ATStr()),
                                 Attr("multiline", ATBool()),
                                 Attr("regex", ATStr(), "Python regular expression with which the value must match."),
                                 Attr("verifier", ATStr(multiline=True, syntax='python')),
                                 Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                 str_template=u"Str [${minlen}, ${maxlen}]")

s_file = ATStruct(Struct(u'File', [
    Attr("extensions", ATList(ATStr(), unique=True), u'Allowed file extensions. If empty, any file type is allowed.'),
    Attr('optional', ATBool(1), u'Is this attribute optional?'),
    ]), str_template=u"${extensions}")
s_folder = ATStruct(Struct(u'Folder', [Attr('optional', ATBool(1), u'Is this attribute optional?'), ]),
                    str_template=u"Folder")

# u_type represents an AttrType
# Note: cyclic ref: utype needs slist, slist need utype
# So we create a dummy u_type first, it'll be completed later
u_type = Union("TypeDef", [[s, s.struct.name] for s in [s_int, s_bool, s_float, s_str, s_time, s_duration]],
               show_value_in_label=False)
atu_type = ATUnion(u_type)
atu_key_type = ATUnion(u_type, filter=(u'Bool', u'Int', u'Str', u'Enum', u'Ref'))

s_list = ATStruct(Struct(u"List", [Attr("element_type", atu_type),
                                   Attr("minlen", ATInt(default=0)),
                                   Attr("maxlen", ATInt(default=1024)),
                                   Attr("delimiter", ATStr(default=u"; "), 'delimiter of items. usually ";" or "\n"'),
                                   Attr("unique_attrs", ATList(ATStr(1, 255), True),
                                        '[ONLY if element type is Struct]names of attributes must be unique'),
                                   Attr("verifier", ATStr(multiline=True, syntax='python')),
                                   Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                  str_template=u"[${element_type}] [${minlen}, ${maxlen}]")

# todo: should verify key type
s_dict = ATStruct(Struct(u"Dict", [Attr("key_type", atu_key_type, 'primitive type ONLY(bool/int/str/enum/ref)'),
                                   Attr("val_type", atu_type),
                                   Attr("minlen", ATInt(default=0)),
                                   Attr("maxlen", ATInt(default=1024)),
                                   Attr("verifier", ATStr(multiline=True, syntax='python')),
                                   Attr("exporter", ATStr(multiline=True, syntax='python'))]))

s_ref = ATStruct(Struct(u"Ref", [Attr("class_name", ATRef(CLAZZ_NAME_CLAZZ)),
                                 Attr("nullable", ATBool(1)),
                                 Attr("verifier", ATStr(multiline=True, syntax='python')),
                                 Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                 str_template=u"${class_name}")

s_struct = ATStruct(Struct(u"Struct", [Attr("struct", ATRef(CLAZZ_NAME_STRUCT)),
                                       Attr("str_template", ATStr(), u'This will override str_template of the Struct'),
                                       Attr("verifier", ATStr(multiline=True, syntax='python')),
                                       Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                    str_template="${struct}")

s_union_verifier = """for name in v['filter']:
    if not self.union.get_struct(name): 
        error('invalid filter value: %s', name)
"""
s_union = ATStruct(Struct(u"Union", [Attr("union", ATRef(CLAZZ_NAME_UNION)),
                                     Attr("filter", ATList(ATStr(1, 255), unique=True)),
                                     Attr("verifier", ATStr(multiline=True, syntax='python')),
                                     Attr("exporter", ATStr(multiline=True, syntax='python'))]),
                   verifier=s_union_verifier,
                   str_template=u"${union}")

s_predefined_type = ATStruct(Struct(u"PredefinedType", [Attr("predefined_type", ATRef(CLAZZ_NAME_PREDEFINED_TYPE))]),
                             str_template=u"${predefined_type}")

s_enum_verifier = """
enum_obj = p.object_manager.get_object(v[u'enum'], u"Enum")
if not enum_obj:
    return

items = enum_obj.get_attr_value(u'items')
names = [i['name'] for i in items]
for name in v['filter']:    
    if name not in names:
        error('invalid filter value for %s: %s', enum_obj.name, name)
if v[u'default'] and v[u'default'] not in names:
    error('invalid default value for %s: %s', enum_obj.name, v[u'default'])
"""
s_enum = ATStruct(Struct(u"Enum", [Attr("enum", ATRef(CLAZZ_NAME_ENUM)),
                                   Attr("default", ATStr(0, 255, u"")),
                                   Attr("filter", ATList(ATStr(1, 255), unique=True)),
                                   Attr("verifier", ATStr(multiline=True, syntax='python'))],
                         str_template=u'${enum}'),
                  verifier=s_enum_verifier)


# u_type was not completed
u_type.set_structs([[s, s.struct.name] for s in [s_int, s_bool, s_float, s_str, s_time, s_duration, s_file, s_folder,
                                                 s_list, s_dict, s_ref, s_struct, s_union, s_enum, s_predefined_type]])
# atu_type.update_union()
# u_int_or_str = Union("IntOrStr", [Struct("Int", [Attr("value", ATInt())]),
#                                  Struct("Str", [Attr("value", ATStr())])])

regex_identifier = "^[A-Za-z_][a-zA-Z0-9_]*$"
atstr_identifier = ATStr(1, 255, regex=regex_identifier)
attr_attr_name = Attr("name", atstr_identifier, 'Attribute name')
s_attr = Struct("AttrDef", [attr_attr_name,
                            Attr("type", atu_type, "Type of this attribute"),
                            Attr("description", ATStr(0, 1024), "A description for this attribute")],
                str_template=u'${name}')


def _clazz(name, attrs, **kwargs):
    return Clazz(ATStruct(Struct(name, attrs), **kwargs))

################################################################################
# Class
################################################################################
clazz_attrs_verifier = """names = [a['name'] for a in v]
for name in ['id', 'name']:
    if name not in names:
        error('required attr "%s" is missing', name)
for name in ['tags', 'enable']:
    if name in names:
        error('reserved attr "%s" should not present', name)
for a in v:
    if a['name'] == 'id':
        at = a['type']
        # if at['key'] == 'Int' and at[at['key']]['min'] < 0:
        #     error(u'class id MUST >= 0')
        if at['key'] != 'Str':
            error(u'class id should be Str!')
        
"""
clazz_clazz = _clazz(CLAZZ_NAME_CLAZZ, [Attr("name", atstr_identifier, "Name of the class. eg: Monster, Skill, NPC"),
                                        Attr("attrs", ATList(ATStruct(s_attr), unique_attrs=['name'],
                                                             verifier=clazz_attrs_verifier),
                                             'Attribute List. "id" and "name" are required, "id" should be Str.'),
                                        Attr("unique_attrs", ATList(ATStr(1, 255), True),
                                             'Attributes names must be unique. eg: "id"'),
                                        Attr("str_template", ATStr(0, 255, u'${name}'), "how to display this object."),
                                        Attr("max_number", ATInt(1, default=0x7FFFFFFF), "max number of objects"),
                                        Attr("min_number", ATInt(default=0), "min number of objects"),
                                        Attr("icon", ATFile(['.png'], True),
                                             "Icon for this class to be shown in editor"),
                                        Attr("verifier", ATStr(multiline=True, syntax='python')),
                                        Attr("exporter", ATStr(multiline=True, syntax='python')),
                                        ])
clazz_clazz.icon = "icons/class.png"
# todo: verify unique_attrs

################################################################################
# Enum
################################################################################
class_enum_verifier = u"""
# names must be valid variables.
import re
regex = re.compile('^[a-zA-Z0-9_]+$')
for item in v['items']:
    if not regex.match(item['name']):
        error(u'Invalid enum item name: %s', item['name'])

# values must be unique
values = [item['value'] for item in v['items']]
if not v['export_names']:
    # values must be unique    
    import collections
    counter = collections.Counter(values)
    for val, cnt in counter.iteritems():
        if cnt>1:
            error(u'duplicated value: %s', val)
            
if v['convert_to_int']:
    for val in values:
        try:
            int(val)
        except:
            error("can't convert to int: %s", val)            
"""
clazz_enum = _clazz(CLAZZ_NAME_ENUM, [Attr("name", ATStr(1, 255)),
                                      # Attr("items", ATList(ATStruct(s_enum_item)))] )
                                      Attr("items", ATList(ATStruct(
                                          Struct("EnumItem", [
                                              Attr("name", ATStr(1, 255),
                                                   u"Never change names once they've been used."),
                                              Attr("value", ATStr(0, 255),
                                                   u"Values rather than name are exported by default"),
                                              Attr("label", ATStr(0, 255),
                                                   u'Label of this item. If empty, use name instead.'),
                                              Attr("comment", ATStr(0, 255))],
                                                 str_template=u'${name}')), True, 1, unique_attrs=['name'])),
                                      Attr('export_names', ATBool(0),
                                           'export names instead of values(value by default)'),
                                      Attr('convert_to_int', ATBool(0), u'convert values to integers'),
                                      Attr('show_value_in_label', ATBool(1))
                                      ],
                    verifier=class_enum_verifier)
clazz_enum.icon = "icons/enum.png"

clazz_struct = _clazz(CLAZZ_NAME_STRUCT, [Attr("name", atstr_identifier, "Name of the struct"),
                                          Attr("attrs", ATList(ATStruct(s_attr), unique_attrs=['name'])),
                                          Attr("str_template", ATStr(),
                                               'eg: "ID: ${id}, Name: $name, Price: $$${price}'),
                                          Attr("verifier", ATStr(multiline=True, syntax='python')),
                                          Attr("exporter", ATStr(multiline=True, syntax='python'))])
clazz_struct.icon = "icons/struct.png"

################################################################################
# Union
################################################################################
class_union_verifier = class_enum_verifier
clazz_union = _clazz(CLAZZ_NAME_UNION, [Attr("name", ATStr(0, 255)),
                                        # Attr("structs", ATList(ATRef(CLAZZ_NAME_STRUCT)))
                                        Attr("items", ATList(ATStruct(
                                            Struct("UnionItem", [
                                                Attr("name", ATStr(0, 255),
                                                     u"Never change names once they've been used."),
                                                Attr('value', ATStr(0, 255), u"Values are exported by default"),
                                                Attr('label', ATStr(0, 255), u'Label of this item'),
                                                Attr("attrs", ATList(ATStruct(s_attr))),
                                                Attr("str_template", ATStr(),
                                                     u'eg: "ID: ${id}, Name: $name, Price: $$${price}'),
                                                Attr("verifier", ATStr(multiline=True, syntax='python')),
                                                Attr("exporter", ATStr(multiline=True, syntax='python')),
                                                Attr("comment", ATStr(multiline=True))], str_template=u'${name}')),
                                            minlen=1, unique_attrs=['name'])
                                            ),
                                        Attr('export_names', ATBool(0),
                                             u'export names instead of values(value by default)'),
                                        Attr('convert_to_int', ATBool(0), u'convert values to integers'),
                                        Attr('exporter', ATStr(), u'custom exporter'),
                                        Attr('show_value_in_label', ATBool(1))
                                        ],

                     verifier=class_union_verifier)

clazz_union.icon = "icons/union.png"


################################################################################
# Setting
################################################################################
e_file_path = Enum(u'FilePathExport', [[u'FullPath', 0], [u'NameOnly', 1], [u'RelativePath', 2]])
clazz_setting = _clazz(CLAZZ_NAME_SETTING, [
    # Attr("languages", ATList(ATStr(2,8,u"en"), unique=True)),
    # Attr("default_language", ATStr(2,8,u"en")),
    Attr("translations",
         ATList(ATStruct(Struct("Dictionary", [Attr("keyword", ATStr(1), "str to translate(NOT used now!)"),
                                               Attr("translation", ATStr(), "translated")
                                               ])), unique_attrs=['keyword'])),
    Attr('tags', ATList(ATStr(1)), u'Tags which can be used to group objects'),
    Attr('auto_create_clazz_folder', ATBool(0), 'Automatically creates a folder for each Clazz under root.'),
    Attr('export_file_path', ATEnum(e_file_path, 'RelativePath'), 'How to export file paths'),
    Attr('export_relative_root', ATFolder(True), 'Relative root. Only valid if "RelativePath" was selected.'),
    Attr('export_files', ATBool(), 'Export referenced files or not?'),
    Attr("verifier", ATStr(multiline=True, syntax='python')),
])
clazz_setting.icon = "icons/setting.png"
# 1 and only 1 setting object
clazz_setting.max_number = 1
clazz_setting.min_number = 0

################################################################################
# PredefinedType
################################################################################
clazz_predefined_type = _clazz(CLAZZ_NAME_PREDEFINED_TYPE, [Attr("name", ATStr(0, 255)),
                                                            Attr("predefined_type", atu_type, "Type to be reused.")])
clazz_predefined_type.icon = "icons/predefined_type.png"
