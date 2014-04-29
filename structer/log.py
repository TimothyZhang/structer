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
ERROR Levels:

DEBUG: For developer only.
INFO: Inform user.
WARN: Not sure correct or not. 
ERROR: There's something wrong, but editor can continue working.
FATAL: Serious error that prevents editor from working. Failed assertions are fatal errors.

Example:
    log.error(exception, "this is an error: %s", "bad")  # first argument is an Exception instance
    log.error("this is another error")                   # or just a string 
'''

import traceback, sys

LEVELS = ['DEBUG', "INFO", 'WARN', "ERROR", "FATAL"]
DEBUG = LEVELS.index('DEBUG')
INFO = LEVELS.index('INFO')
WARN = LEVELS.index('WARN')
ERROR = LEVELS.index('ERROR')
FATAL = LEVELS.index("FATAL")

# current log level
_level = 0

# _trackers = []

class Record(object):
    def __init__(self, level, *args, **kwargs):
        self.level = level
        
        self.exception = None
        self.exc_info = None
        
        i = 0
        if isinstance(args[0], Exception):
            self.exception = args[0]
            self.exc_info = sys.exc_info()
            i = 1
        
        self.msg = args[i]
        self.args = args[i+1:]
        self.kwargs = kwargs
                
    def format(self, with_level=True):        
        msg = self.msg % tuple(self.args)
        if with_level:
            msg = '[%s]%s' %(LEVELS[self.level], msg)
        #if self.exception:
        #    msg = '%s: %s' % (msg, self.exception)
        return msg


# class Tracker(object):
#     def __init__(self):        
#         self.errors = []
#         self.warnings = []
#         self.fatals = []
#         self.result = None
#         
#         self._all = []
#         self._map = {WARN: self.warnings,
#                      ERROR: self.errors,
#                      FATAL: self.fatals}        
#         
#         _trackers.append( self )
#     
#     def add(self, record):
#         list_ = self._map.get( record.level )
#         if list_ is not None:
#             list_.append( record )
#             
#         self._all.append( record )            
#         
#     def finish(self):
#         _trackers.remove( self )
#             
#     def has_fatal(self):
#         return len(self.fatals) > 0
#     
#     def has_error_only(self):
#         return len(self.errors) > 0
#     
#     def has_error_or_fatal(self):
#         return len(self.errors) > 0 or len(self.fatals) > 0
#     
#     def has_warning(self):
#         return len(self.warnings) > 0
#     
#     def log_all(self):
#         for r in self._all:
#             _print( r )
# 
# def track(method, *args, **kwargs):
#     tracker = Tracker() 
#    
#     try:
#         tracker.result = method(*args, **kwargs)
#     except Exception, e:
#         import traceback
#         traceback.print_exc()
#         error('internal error', obj=e)            
#     
#     tracker.finish()    
#     return tracker
# 
# def track_errors(method, *args, **kwargs):
#     tracker = track(method, *args, **kwargs)
#     return tracker.has_error_or_fatal()

def set_level(level):
    global _level
    if type(level) is str:
        _level = LEVELS.index(level)
    else:
        _level = level

def _print(record):
    print record.format()

def _log(record):
#     if _trackers:
#         for tracker in _trackers:
#             tracker.add( record ) 
#     else:
    _print( record )
    
    if record.exc_info:
        #sys.stdout.flush()
        traceback.print_exception( *(record.exc_info) )    

def debug(*args, **kwargs):    
    if _level <= DEBUG:
        r = Record(DEBUG, *args, **kwargs)
        _log(r)
        return r
    
def info(*args, **kwargs):    
    if _level <= INFO:
        r = Record(INFO, *args, **kwargs)
        _log(r)
        return r

def warn(*args, **kwargs):    
    if _level <= WARN:
        r = Record(WARN, *args, **kwargs)
        _log(r)
        return r

def error(*args, **kwargs):    
    if _level <= ERROR:                
        r = Record(ERROR, *args, **kwargs)
        _log(r)
        return r

def assert_(condition, msg, *args):
    if not condition:
        return error(msg, *args)
        
def fatal(*args, **kwargs):
    '''The first argument might be an Exception'''
    if _level <= FATAL:
        r = Record(FATAL, *args, **kwargs)
        _log(r)
        return r

if __name__=='__main__':
    def test():
        error('123123')
#     if track_errors(test):
#         print 'error'
