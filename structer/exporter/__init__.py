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



'''   
todos:
     
layout:
zip or folder?
1 obj per file, or 1 clazz per file?

object selection
tags?        
selected/all
how to deal with errors?

object format
json / binary?
format of each type
    enum?
    union?
XClass?
XTable?        
'''

from default_exporter import DefaultObjectExporter
from js_code_exporter import JsCodeExporter
from py_code_exporter import PyCodeExporter
from type_exporter import JsonTypeExporter