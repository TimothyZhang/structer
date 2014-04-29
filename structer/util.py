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

def normpath(p):     
    p = p.replace('/', os.path.sep)
    p = p.replace('\\', os.path.sep)
    return p    
    
def get_absolute_path(path, relaltive_to):
    '''Gets absolute path of "path", which was relative to "relaltive_to"
    
    Args:
        path: an absolute path, or a path which is relative to "relative_to"
        relaltive_to: 
        
    Retunrs:
        Absolute path    
    '''
    path = normpath(path)
    if os.path.isabs(path):
        return path
    
    p = os.path.join(relaltive_to, path)
    p = os.path.abspath( normpath(p) )
    return p
    
def get_relative_path(path, relaltive_to):
    '''Gets relative path of "path" relatives to "relaltive_to" 
    
    Args:
        path: absolute path, or relative path which is relative to current woking directory
        relaltive_to:
        
    Returns:
        Path relative to "relative_to"
    '''
    
    abs_path = normpath(os.path.abspath(path))
    p = normpath(abs_path)        
    p2 = normpath(relaltive_to)
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
        i+=1
        
    r = ''.join( ['..%s'%sep] * (len(p2)-i) )
    r += sep.join(p[i:])
    return r

if __name__=='__main__':
    print get_relative_path('/a/b/c', '/a')
    print get_relative_path('/a', '/a/b/c')
    print get_relative_path('/a/', '/a/b/c')
    print get_relative_path('/a/d', '/a/b/c')
