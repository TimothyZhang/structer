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
import calendar
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
    negative = False
    if seconds < 0:
        seconds = -seconds
        negative = True

    seconds_int = int(seconds)
    tmp = seconds - seconds_int
    minutes, seconds_int = divmod(seconds_int, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if negative:
        return -days, -hours, -minutes, -(seconds_int + tmp)
    return days, hours, minutes, seconds_int + tmp


def dhms_to_seconds(d, h, m, s):
    if d < 0 or h < 0 or m < 0 or s < 0:
        assert d <= 0 and h <= 0 and m <= 0 and s <= 0

    h += d * 24
    m += h * 60
    s += m * 60
    return s


def dhms_to_str(days, hours, minutes, seconds):
    negative = False
    if days < 0 or hours < 0 or minutes < 0 or seconds < 0:
        assert days <= 0 and hours <=0 and minutes <= 0 and seconds <= 0
        days, hours, minutes, seconds = -days, -hours, -minutes, -seconds
        negative = True

    d = ''
    if days:
        d = '%sd ' % days

    seconds_int = int(seconds)
    seconds_fraction = seconds - seconds_int
    s = '%s%02d:%02d:%02d' % (d, hours, minutes, seconds_int)
    if seconds_fraction != 0:
        assert 0 < seconds_fraction < 1
        fraction = '%.3f' % seconds_fraction
        s += fraction[1:].rstrip('0').rstrip('.')
    if negative:
        s = '-' + s
    return s


def str_to_dhms(s):
    s = s.strip()
    if not s:
        return 0

    negative = False
    if s[0] == '-':
        negative = True
        s = s[1:]

    tmp = s.split(' ')

    days = 0
    if len(tmp) > 1:
        assert tmp[0][-1] == 'd'
        days = int(tmp[0][:-1])

    hms = tmp[-1].split(':')
    if len(hms) == 2:
        m, s = hms
        h = 0
    elif len(hms) == 3:
        h, m, s = hms
    else:
        raise Exception('Invalid duration string: %s' % s)

    if negative:
        return -days, -int(h), -int(m), -float(s)
    return days, int(h), int(m), float(s)


def utc_str_to_timestamp(s):
    # val = ' '.join(val.split(' ')[:2])
    # tz = - time.timezone / 3600
    # return time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')) + 3600 * tz
    # return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S'))
    return str_to_timestamp(s, 0)


def str_to_timestamp(s, timezone_offset=0):
    """
    :param str s:
    :param int timezone_offset: seconds
    :rtype: int
    """
    try:
        tt = time.strptime(s, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        tt = time.strptime(s, '%Y-%m-%d')

    timestamp = calendar.timegm(tt)
    return timestamp - timezone_offset


def utc_timestamp_to_str(timestamp):
    # return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))
    return timestamp_to_str(timestamp, 0)


def timestamp_to_str(timestamp, timezone_offset=0):
    """
    :param int timestamp:
    :param int timezone_offset:
    :rtype str:
    """
    timestamp += timezone_offset
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))


if __name__ == '__main__':
    # print get_relative_path('/a/b/c', '/a')
    # print get_relative_path('/a', '/a/b/c')
    # print get_relative_path('/a/', '/a/b/c')
    # print get_relative_path('/a/d', '/a/b/c')
    print dhms_to_str(*seconds_to_dhms(129))
    print utc_timestamp_to_str(0)
    print utc_str_to_timestamp('1970-01-01 00:00:00')

