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

import time


def normpath(p):     
    p = p.replace('/', os.path.sep)
    p = p.replace('\\', os.path.sep)
    return p    

    
def get_absolute_path(path, relative_to):
    """Gets absolute path of "path", which was relative to "relative_to"
    
    Args:
        path: an absolute path, or a path which is relative to "relative_to"
        relative_to:
        
    Returns:
        Absolute path    
    """
    path = normpath(path)
    if os.path.isabs(path):
        return path
    
    p = os.path.join(relative_to, path)
    p = os.path.abspath(normpath(p))
    return p
    

def get_relative_path(path, relative_to):
    """Gets relative path of "path" relatives to "relative_to"
    
    Args:
        path: absolute path, or relative path which is relative to current working directory
        relative_to:
        
    Returns:
        Path relative to "relative_to"
    """
    
    abs_path = normpath(os.path.abspath(path))
    p = normpath(abs_path)        
    p2 = normpath(relative_to)
    sep = os.path.sep
    
    if p == p2:
        return '.'  
    
    drive, p = os.path.splitdrive(p)
    drive2, p2 = os.path.splitdrive(p2)
    
    if drive2 != drive:
        return abs_path
    
    p = p.split(sep)
    p2 = p2.split(sep)
    n = min(len(p), len(p2))
    i = 0
    while i < n:        
        if p[i] != p2[i]:        
            break
        i += 1
        
    r = ''.join(['..%s' % sep] * (len(p2)-i))
    r += sep.join(p[i:])
    return r


def is_sub_sequence(a, b):
    """
    Determines whether a is a sub sequence of b. (NOTE: not sub list!)
    :param list | tuple a:
    :param list | tuple b:
    :return: True if a is sub sequence of b, otherwise False
    :rtype: bool
    """
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
        j += 1
    return i >= len(a)


def seconds_to_dhms(seconds):
    """
    Converts seconds to a tuple of (days, hours, minutes, seconds)
    :param float seconds:
    :rtype: (int, int, int, float)
    """
    seconds_int = int(seconds)
    tmp = seconds - seconds_int
    minutes, seconds_int = divmod(seconds_int, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return days, hours, minutes, seconds_int + tmp


def dhms_to_seconds(d, h, m, s):
    h += d * 24
    m += h * 60
    s += m * 60
    return s


def dhms_to_str(days, hours, minutes, seconds):
    d = ''
    if days:
        d = '%sd ' % days

    s = '%s%02d:%02d:%.3f' % (d, hours, minutes, seconds)
    s = s.rstrip('0').rstrip('.')
    if s[-2] == ':':
        s += '0'
    return s


def str_to_dhms(s):
    tmp = s.split(' ')

    days = 0
    if len(tmp) > 1:
        assert tmp[0][-1] == 'd'
        days = int(tmp[0][:-1])

    h, m, s = tmp[-1].split(':')
    return days, int(h), int(m), float(s)


def utc_str_to_timestamp(s):
    # val = ' '.join(val.split(' ')[:2])
    tz = - time.timezone / 3600
    return time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')) + 3600 * tz


def utc_timestamp_to_str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))


if __name__ == '__main__':
    # print get_relative_path('/a/b/c', '/a')
    # print get_relative_path('/a', '/a/b/c')
    # print get_relative_path('/a/', '/a/b/c')
    # print get_relative_path('/a/d', '/a/b/c')
    print dhms_to_str(*seconds_to_dhms(129))

