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


import os
import platform

import wx
from structer.util import get_absolute_path
import log

ICON_FOLDER = 'icons/folder.png'
ICON_OBJECT = 'icons/object.png'
ICON_FILTER = 'icons/filter.png'

FRAME_ICON_SIZE = (16, 16)


class __Wxid(object):
    def __init__(self):        
        self.__dict = {}
    
    def __getattr__(self, name):
        # noinspection PyBroadException
        try:
            return self.__dict[name]
        except:            
            self.__dict[name] = new_id = wx.NewId()
            return new_id
        
_bmp_cache = {}


def get_image_path(filename, project):    
    # current
    if os.path.exists(filename):
        return filename
    
    if os.path.isabs(filename):
        return None
    
    # relative to project
    if project:
        path = get_absolute_path(filename, project.path)
        if os.path.exists(path):
            return path
    
    # res folder
    prefix = os.path.split(__file__)[0]
    path = os.path.join(prefix, 'res', filename)
    if os.path.exists(path):
        return path
    
    return None


def get_bitmap(pathname, size, project):
    """
    Args:
        pathname: path of image
        size: (w,h), or None if use original image size
        project: can be None
        
    Returns:
        bitmap, or None
    """
    path = get_image_path(pathname, project)
    if not path:
        log.warn('icon file not found: %s', pathname)
        return None
    
    if path in _bmp_cache:
        return _bmp_cache[(path, size)]
    else:        
        # http://trac.wxwidgets.org/ticket/15331
        prev = wx.Log.GetLogLevel()
        wx.Log.SetLogLevel(wx.LOG_Error)
        img = wx.Image(path)
        wx.Log.SetLogLevel(prev)
        
        if size:
            img = img.Scale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
        _bmp_cache[(path, size)] = img.ConvertToBitmap()
    # print bmp_cache
    return _bmp_cache[(path, size)]


def get_icon(name, size, project):
    bmp = get_bitmap('icons/%s' % name, size, project)
    if bmp:
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(bmp)
        return icon


def get_clazz_bitmap(clazz, size, project):
    bmp = get_bitmap(clazz.icon, size, project)
    if not bmp:
        bmp = get_bitmap('icons/object.png', size, project)
    return bmp


def get_app_data_path():
    from os.path import expanduser
    user_home = expanduser("~")
    app_data_path = os.path.join(user_home, '.structer')
    if not os.path.exists(app_data_path):
        # noinspection PyBroadException
        try:
            os.makedirs(app_data_path)
        except:
            pass
    return app_data_path

wxid = __Wxid()


def is_mac():
    return len(platform.mac_ver()[0]) > 0
