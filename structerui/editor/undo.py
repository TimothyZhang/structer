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


import wx
from structer import log


class UndoManager(object):
    def __init__(self):
        self._history = []
        
        # next action to undo
        self._index = -1
        
        # if _lock==True, ignore all new actions
        self._lock = False
    
#     def lock(self):
#         self._lock = True
#         
#     def unlock(self):
#         self._lock = False
#     def is_modified(self):
#         return len(self._history)>0
    
    def add(self, action):
        print 'UndoManager.add:', action, self._lock
        if self._lock:
            return
        
        # clear redo list
        del self._history[self._index+1:]
        
        if self._history:
            last = self._history[-1]
            # open then close         
            if type(action) is CloseDialogAction and type(last) is OpenDialogAction:
                self._history.pop()            
            # close then open
            elif type(action) is OpenDialogAction and type(last) is CloseDialogAction and \
                    action.row == last.row and action.col == last.col:
                self._history.pop()
            elif type(action) is CloseFlattenDialogAction and type(last) is OpenFlattenDialogAction:
                self._history.pop()
            # close then open
            elif type(action) is OpenFlattenDialogAction and type(last) is CloseFlattenDialogAction:
                self._history.pop()
            else:
                self._history.append(action)
        else:            
            self._history.append(action)
            
        self._index = len(self._history)-1
        # print '   history: ', len(self._history), self._index
    
    def _reset(self):
        self._history = []
        self._index = -1
        
    def clear(self):
        self._reset()
        
    def undo(self, grid):
        print 'UndoManager.undo'
        if self._index < 0:
            return
                
        act = self._history[self._index]
        print '   ', act
        self._index -= 1
        
        self._lock = True     
        try:   
            act.undo(grid)
        except Exception, e:
            log.error(e, 'undo failed')
            wx.MessageBox("Undo failed, reset history: %s\n" % e)
            self._reset()
        
        self._lock = False
    
    def redo(self, grid):
        print 'UndoManager.redo'
        if self._index >= len(self._history)-1:
            return
                
        self._index += 1
        act = self._history[self._index]
        print '   ', act
        self._lock = True
        try:
            act.redo(grid)
        except Exception, e:
            log.error(e, 'redo failed')
            wx.MessageBox("Redo failed, reset history: %s\n" % e)
            self._reset()
            
        self._lock = False


class Action(object):    
    def undo(self, grid):
        pass
    
    def redo(self, grid):
        pass


class MutateAction(Action):
    def __init__(self, row, col, old, new):
        self.row = row
        self.col = col
        self.old = old
        self.new = new
    
    def undo(self, grid):
        self._set_value(grid, self.new, self.old)
        
    def _set_value(self, grid, cur, new):
        cur2 = grid.GetTable().get_attr_value(self.row, self.col)
        assert cur == cur2, str((self.row, self.col, cur, cur2, new))
        grid.GetTable().set_value(self.row, self.col, new)
        
        grid.refresh_block((self.row, self.col, self.row, self.col))
        grid.GoToCell(self.row, self.col)
        
    def redo(self, grid):
        self._set_value(grid, self.old, self.new)


class BatchMutateAction(Action):
    def __init__(self, row, col, old, new):
        assert len(old) == len(new)
        assert len(old) > 0
        assert len(old[0]) > 0
        assert len(new[0]) > 0
        
        # self.attr_type_names = attr_type_names
        self.old = old
        self.new = new
        
        self.block = (row, col, row+len(old)-1, col+len(old[0])-1)        
        
    def undo(self, grid):
        grid.batch_mutate(self.block, self.old)
    
    def redo(self, grid):
        grid.batch_mutate(self.block, self.new)


class OpenDialogAction(Action):
    def __init__(self, row, col):
        self.row = row
        self.col = col        
        
    def undo(self, grid):
        p = grid
        while p.GetParent() and not p.IsTopLevel():
            p = p.GetParent()
        
        p.Close()
        # grid.GoToCell( self.row, self.col )
        
    def redo(self, grid):
        grid.GoToCell(self.row, self.col)
        grid.EnableCellEditControl()


class CloseDialogAction(OpenDialogAction):
    def undo(self, grid):
        OpenDialogAction.redo(self, grid)
    
    def redo(self, grid):
        OpenDialogAction.undo(self, grid)


class OpenFlattenDialogAction(Action):
    def __init__(self, block, focus):
        self._block = block
        self._focus = focus

    def undo(self, grid):
        p = grid
        while p.GetParent() and not p.IsTopLevel():
            p = p.GetParent()

        p.Close()

    def redo(self, grid):
        grid.set_selection_block(self._block)
        row, col = self._focus
        grid.SetGridCursor(row, col)
        grid.show_flatten_editor()


class CloseFlattenDialogAction(OpenFlattenDialogAction):
    def undo(self, grid):
        OpenFlattenDialogAction.redo(self, grid)

    def redo(self, grid):
        OpenFlattenDialogAction.undo(self, grid)


class ListInsertAction(Action):
    def __init__(self, pos, attr_type_names, data):
        self.pos = pos
        self.attr_type_names = attr_type_names
        self.data = data        
    
    def undo(self, grid):
        grid.delete(self.pos, len(self.data), False)
    
    def redo(self, grid):        
        grid.insert_data(self.attr_type_names, self.data, self.pos)


class ListDeleteAction(ListInsertAction):
    def undo(self, grid):
        ListInsertAction.redo(self, grid)
        
    def redo(self, grid):
        ListInsertAction.undo(self, grid)
