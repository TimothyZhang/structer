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

# coding=utf-8

# folder to store objects, under project root 
PROJECT_FOLDER_DATA = "data"

# folder to store type infomations, under project root 
PROJECT_FOLDER_TYPE = "type"

FILE_TYPE_OBJECT = 'object'
FILE_TYPE_FILTER = 'filter'

kFileTypeModel = 1 << 1
kFileTypeDir = 1 << 2
kFileTypeFilter = 1 << 3

# TODO: refactor names
kFilterExt = ".filt"  # filters
kVdir = u"vdir"  # virtual dir
kFileExt = ".json"  # data file
kVSep = ":"  # path seperator of virtual path

# STRUCTER_ERROR_OK    = 0
# STRUCTER_ERROR_TYPES = 100
