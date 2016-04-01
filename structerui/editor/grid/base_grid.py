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
Clipboard:
    use a custom data object: CLIPBOARD_DATA_FORMAT
    clip data is a json dumped string, json format is [ [AttrType.name, ...], [[col1, col2, ...], ] ]
"""
import json

import wx
import wx.grid as grid

from structer.stype.attr_types import *
from structerui import util
from structerui import hotkey
from cell_editor import * 
from cell_editor.dialog import RefEditorDialog, EditorDialog, FileDialog, FolderDialog

COL_MAX_SIZE = 250
COL_MIN_ACCEPTABLE_SIZE = 100
CLIPBOARD_DATA_FORMAT = "__structer_grid_cells_f9014n203823dk1j2hdlacxcb__"

MY_GRID_DATA_TYPE_ENUM = "MY_GRID_DATA_TYPE_ENUM"
MY_GRID_DATA_TYPE_LIST = "MY_GRID_DATA_TYPE_LIST"
MY_GRID_DATA_TYPE_UNION = "MY_GRID_DATA_TYPE_UNION"
MY_GRID_DATA_TYPE_STRUCT = "MY_GRID_DATA_TYPE_STRUCT"
MY_GRID_DATA_TYPE_LIST_ENUM_UNIQUE = "MY_GRID_DATA_TYPE_LIST_ENUM_UNIQUE"
MY_GRID_DATA_TYPE_REF = 'MY_GRID_DATA_TYPE_REF'
MY_GRID_DATA_TYPE_FILE = 'MY_GRID_DATA_TYPE_FILE'
MY_GRID_DATA_TYPE_FOLDER = 'MY_GRID_DATA_TYPE_FOLDER'
MY_GRID_DATA_TYPE_TIME = 'MY_GRID_DATA_TYPE_TIME'
MY_GRID_DATA_TYPE_DURATION = 'MY_GRID_DATA_TYPE_DURATION'

# Cell Attributes
GRID_CELL_ATTR_DEFAULT = grid.GridCellAttr()

GRID_CELL_ATTR_DEFAULT_READONLY = grid.GridCellAttr()
GRID_CELL_ATTR_DEFAULT_READONLY.SetReadOnly()
        
# error
GRID_CELL_ATTR_ERROR = grid.GridCellAttr()
GRID_CELL_ATTR_ERROR.SetBackgroundColour((0xFF, 0, 0))

GRID_CELL_ATTR_ERROR_READONLY = GRID_CELL_ATTR_ERROR.Clone()
GRID_CELL_ATTR_ERROR_READONLY.SetReadOnly()

# warning
# GRID_CELL_ATTR_WARNING = grid.GridCellAttr()
# GRID_CELL_ATTR_WARNING.SetBackgroundColour( (0xDD, 0xDD, 0x44) )

# readonly
GRID_CELL_ATTR_STATIC_READONLY = grid.GridCellAttr()
GRID_CELL_ATTR_STATIC_READONLY.SetReadOnly(True)
GRID_CELL_ATTR_STATIC_READONLY.SetBackgroundColour(wx.Colour(0xAA, 0xAA, 0xAA))


# noinspection PyMethodOverriding
class TableBase(grid.PyGridTableBase):
    """
    GetValue() returns AttrType.str(val)
    SetValue() accepts val, NOT AttrType.str(val0
    """
    
    def __init__(self, editor_context):
        grid.PyGridTableBase.__init__(self)

        self._ctx = editor_context
        
    @property
    def editor_context(self):
        return self._ctx
    
    def get_attr_type(self, row, col):
        """Get AttrType of a cell. 
        * MUEST override *
        """               
        raise Exception("NotImplemented")
    
    def get_attr_value(self, row, col):
        """Get value of AttrType of a cell
        """
        raise Exception("NotImplemented")

    # noinspection PyMethodMayBeStatic
    def get_cell_typename_by_attrtype(self, attr_type):
        att = type(attr_type)
        if att is ATInt:
            return grid.GRID_VALUE_NUMBER + ":%s,%s" % (attr_type.min, attr_type.max)
        if att is ATFloat:
            return grid.GRID_VALUE_FLOAT
        if att is ATStr:
            return grid.GRID_VALUE_STRING        
        if att is ATRef:
            return MY_GRID_DATA_TYPE_REF
        if att is ATBool:
            return grid.GRID_VALUE_BOOL
        if att is ATEnum:
            # return grid.GRID_VALUE_CHOICE + ":" + ','.join(attr_type.enum.names)
            return MY_GRID_DATA_TYPE_ENUM   
        if att is ATList:
            if type(attr_type.element_type) is ATEnum and attr_type.unique:
                return MY_GRID_DATA_TYPE_LIST_ENUM_UNIQUE
            return MY_GRID_DATA_TYPE_LIST
        if att is ATUnion:
            return MY_GRID_DATA_TYPE_UNION
        if att is ATStruct:
            return MY_GRID_DATA_TYPE_STRUCT
        if att is ATFile:
            return MY_GRID_DATA_TYPE_FILE
        if att is ATFolder:
            return MY_GRID_DATA_TYPE_FOLDER
        if att is ATTime:
            return MY_GRID_DATA_TYPE_TIME
        if att is ATDuration:
            return MY_GRID_DATA_TYPE_DURATION
        
        # if type(attr) is ATInt:
        #    return grid.GRID_VALUE_NUMBER
        # return self.dataTypes[col]
        return grid.GRID_VALUE_STRING

    # noinspection PyMethodMayBeStatic
    def _get_cell_attr(self, name):
        try:
            ca = globals()[('GRID_CELL_ATTR_%s' % name).upper()]
        except AttributeError:
            ca = GRID_CELL_ATTR_DEFAULT
            
        ca.IncRef()
        return ca
    
#     def get_cell_value(self, attr_type, val):    
#         """convert to readable string"""    
#         if type(attr_type) is ATRef:
#             return attr_type.str(val, self._ctx.project)
#         
#         return val

    def GetValue(self, row, col):
        at = self.get_attr_type(row, col) 
        val = self.get_attr_value(row, col)
                
        if at:  # and type(at) is ATRef:
            cell_type = self.get_cell_typename_by_attrtype(at)
            if cell_type not in (grid.GRID_VALUE_NUMBER, grid.GRID_VALUE_FLOAT, grid.GRID_VALUE_BOOL):
                return at.str(val, self._ctx.project)        
        
        return val
    
    def get_value(self, row, col):
        # at = self.get_attr_type(row, col)
        val = self.get_attr_value(row, col)
        return val
    
    def SetValue(self, row, col, val):
        at = self.get_attr_type(row, col)
        old = self.get_attr_value(row, col)
        self.set_value(row, col, val)
        
        if at.compare(old, val) != 0:
            from structerui.editor.undo import MutateAction
            self._ctx.undo_manager.add(MutateAction(row, col, old, val))
    
    def set_value(self, row, col, val):
        """ override me 
            todo: called by? 
        """
        pass
    
    def GetAttr(self, row, col, kind):
        """kind: Any, Cell, Row, Col"""
        at = self.get_attr_type(row, col)
        if not at:
            print 'at is None', row, col, kind
            return self._get_cell_attr("error_readonly")
        
        val = self.get_attr_value(row, col)
        # print 'GetAttr', row, col, kind
        vlog = at.verify(val, self._ctx.project)
        # print 'GetAttr', row, col, tracker.errors
        
        # attr_name = None
        if vlog.has_error():
            attr_name = "error"        
        else:
            attr_name = "default"
        
        if self._ctx.read_only or (val is None and self._ctx.freeze_none):
            editor = self.GetView().GetDefaultEditorForType(self.GetTypeName(row, col))
            if isinstance(editor, GridCellDialogEditor) and editor.dialog_class is EditorDialog:
                pass
            else:
                if val is None and self._ctx.freeze_none:
                    attr_name = "static"
                attr_name += "_readonly"
                    
        return self._get_cell_attr(attr_name)
    
    # def GetAttr(self, row, col, kind):
    #    """kind: Any, Cell, Row, Col"""
    #    attr = [self.even, self.odd][row % 2]
    #    attr.IncRef()
    #    return attr
    
    def IsEmptyCell(self, row, col):
        return False
    
    def CanGetValueAs(self, row, col, type_name):
        return self.GetTypeName(row, col) == type_name

    def CanSetValueAs(self, row, col, type_name):
        return self.GetTypeName(row, col) == type_name
    
        # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.get_cell_typename_by_attrtype(self.get_attr_type(row, col))

    def can_sort_by_col(self, col):
        pass

    def sort_by_col(self, col, ascending):
        pass

    
class GridBase(grid.Grid):
    def __init__(self, parent, table):
        self._tip_window = None
        
        grid.Grid.__init__(self, parent, -1)
        self._ctx = table.editor_context                
        self.SetTable(table)
        
        # read only
        if self._ctx.read_only:
            # self.SetSelectionMode( grid.Grid.wxGridSelectCells )
            # self.SetBackgroundColour( wx.YELLOW )
            self.SetCellHighlightColour(wx.RED)
            # self.SetCellHighlightPenWidth( 3 )
        
        # intercept key events from CellEditors
        self.Bind(wx.EVT_CHAR_HOOK, self.__OnCharHook)
        # self.Bind(wx.EVT_KEY_DOWN, self.__OnKeyDown)
        self.Bind(grid.EVT_GRID_SELECT_CELL, self.__OnCellSelected)                
        self.Bind(grid.EVT_GRID_CELL_CHANGED, self.__OnCellChanged)
        
        # reset tip position if cell size/position changed
        self.Bind(wx.EVT_SET_FOCUS, self.__OnSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.__OnKillFocus)
        # self.Bind(grid.EVT_GRID_LABEL_LEFT_CLICK, self.__OnGirdLabelLeftClicked)
        self.Bind(grid.EVT_GRID_COL_SORT, self.__OnSortCol)
        
        self.Bind(wx.EVT_SIZE, self.__OnPositionTip)
        p = self
        while p.GetParent() and not p.IsTopLevel():
            p = p.GetParent()            
        p.Bind(wx.EVT_SIZE, self.__OnSize)
        p.Bind(wx.EVT_MOVE, self.__OnPositionTip)
        
        self.Bind(grid.EVT_GRID_EDITOR_HIDDEN, self.__OnEditorHidden)
        self.UseNativeColHeader(True)
        
        # str_renderer = grid.GridCellAutoWrapStringRenderer
        str_renderer = grid.GridCellStringRenderer
        
        # todo can be customized by plugin?
        self.RegisterDataType(grid.GRID_VALUE_NUMBER,   grid.GridCellNumberRenderer(), GridCellIntEditor())
        self.RegisterDataType(grid.GRID_VALUE_FLOAT,    grid.GridCellFloatRenderer(),  GridCellFloatEditor())
        self.RegisterDataType(grid.GRID_VALUE_STRING,   str_renderer(), GridCellStrEditor())
        
        self.RegisterDataType(MY_GRID_DATA_TYPE_LIST,   str_renderer(), GridCellDialogEditor())                
        self.RegisterDataType(MY_GRID_DATA_TYPE_UNION,  str_renderer(), GridCellDialogEditor())
        self.RegisterDataType(MY_GRID_DATA_TYPE_STRUCT, str_renderer(), GridCellDialogEditor())
        self.RegisterDataType(MY_GRID_DATA_TYPE_ENUM,   grid.GridCellStringRenderer(), GridCellEnumEditor())
        self.RegisterDataType(MY_GRID_DATA_TYPE_LIST_ENUM_UNIQUE, str_renderer(), GridCellUniqueEnumListEditor())
        self.RegisterDataType(MY_GRID_DATA_TYPE_REF,    grid.GridCellStringRenderer(),
                              GridCellDialogEditor(RefEditorDialog))
        self.RegisterDataType(MY_GRID_DATA_TYPE_FILE,   grid.GridCellStringRenderer(), GridCellDialogEditor(FileDialog))
        self.RegisterDataType(MY_GRID_DATA_TYPE_FOLDER, grid.GridCellStringRenderer(),
                              GridCellDialogEditor(FolderDialog))
        self.RegisterDataType(MY_GRID_DATA_TYPE_TIME, str_renderer(), GridCellTimeEditor())
        self.RegisterDataType(MY_GRID_DATA_TYPE_DURATION, str_renderer(), GridCellDurationEditor())
        
        self.auto_size()
    
    def auto_size(self):
        # auto size by current cell values
        print 'auto size'
        self.AutoSizeColumns(False)
        
        self.SetColMinimalAcceptableWidth(COL_MIN_ACCEPTABLE_SIZE)
        
        col_sizes = []
        for i in xrange(self.GetNumberCols()):            
            w = self.GetColSize(i)
            col_sizes.append(w)
        
        ww, _ = self.GetClientSizeTuple()
        ww -= 4  # 4 pixels space
        
        total = sum(col_sizes) + self.GetRowLabelSize()
                
        if total < ww:  # window too large
            dw = (ww - total) / self.GetNumberCols()
            for i in xrange(self.GetNumberCols()):
                # self.SetColSize(i, col_sizes[i] + dw )
                col_sizes[i] += dw
        elif total > ww:  # window too small
            tmp = tmp2 = 0
            for w in col_sizes:
                if w > COL_MAX_SIZE:
                    tmp += w - COL_MAX_SIZE
                    tmp2 += w
            
            extra = total - ww
            if tmp > extra:     # larger than COL_MAX_SIZE
                for i in xrange(len(col_sizes)):
                    if col_sizes[i] > COL_MAX_SIZE:
                        col_sizes[i] -= extra * col_sizes[i] / tmp2 + 1
            else:
                for i in xrange(len(col_sizes)):
                    if col_sizes[i] > COL_MAX_SIZE:
                        col_sizes[i] = COL_MAX_SIZE
            
        for i in xrange(self.GetNumberCols()):
            self.SetColSize(i, col_sizes[i])        
        
    @property
    def editor_context(self):
        return self._ctx
    
    def get_preferred_size(self):
        # self.AutoSizeColumns()
        self.auto_size()
        
        w = self.GetRowLabelSize()
        for i in xrange(self.GetNumberCols()):
            w += self.GetColSize(i)
            
        h = self.GetColLabelSize()
        for i in xrange(self.GetNumberRows()):
            h += self.GetRowSize(i)        
        
        return w, h
    
    def __OnCellSelected(self, evt):
        """ show/hide tips """
        self._hide_tip_window()        
        self._show_tip(evt.GetRow(), evt.GetCol())
                
        evt.Skip()
        
    def __OnEditorHidden(self, evt):
        self._hide_tip_window()
        self._show_tip(evt.GetRow(), evt.GetCol())
        
        evt.Skip()
        
    def show_tip(self, row=None, col=None, vlog=None):
        if row is None or col is None:
            row = self.GetGridCursorRow()
            col = self.GetGridCursorCol()
        self._show_tip(row, col, vlog)
    
    def _show_tip(self, row, col, vlog=None):
        if row < 0 or col < 0:
            return
        if util.is_mac():
            return
        r, c = row, col
        # print 'show tip:', row, col
        # show tip
        t = self.GetTable()
        at = t.get_attr_type(r, c)
            
        if at:
            if not vlog:
                val = t.get_attr_value(r, c)                            
                vlog = at.verify(val, self._ctx.project)                        
            if vlog.has_error():            
                screen_width, _ = wx.DisplaySize()
                # rect = self.CellToRect(r, c)
                self._tip_window = CellTipWindow(self, vlog, screen_width / 3)
                self.position_tip(r, c)                
                self._tip_window.Show()
    
    def get_cell_rect_on_screen(self, row, col):
        rect = self.BlockToDeviceRect((row, col), (row, col))
        
        tl = rect.GetTopLeft()
        br = rect.GetBottomRight()
                
        tl = self.GetGridWindow().ClientToScreen(tl)
        br = self.GetGridWindow().ClientToScreen(br)
        return wx.Rect(tl.x, tl.y, br.x - tl.x, br.y - tl.y)
    
    def position_tip(self, row=None, col=None):
        if not self._tip_window:
            return
        
        if row is None or col is None:
            row = self.GetGridCursorRow()
            col = self.GetGridCursorCol()
        
        ws = self._tip_window.GetSize()
        screen_width, screen_height = wx.DisplaySize()
        
        rect = self.get_cell_rect_on_screen(row, col)
        cell_pos = rect.GetTopLeft()            
        
        space = 4
        # right
        x = cell_pos.x + rect.width + space
        if x + ws.width > screen_width:
            # left
            x = cell_pos.x - ws.width - space
        
        # top
        # y = cell_pos.y - ws.height - 1
        y = cell_pos.y
        if y + ws.height > screen_height:
            y = cell_pos.y + rect.height - ws.height
            if y < 0:
                y = 0        
        
        self._tip_window.SetPosition(wx.Point(x, y))
    
    def hide_tip(self):
        return self._hide_tip_window()
    
    def _hide_tip_window(self):
        if self._tip_window:
            self._tip_window.Close()
            self._tip_window.Destroy()
            self._tip_window = None
    
    def __OnSetFocus(self, evt):
        if self._tip_window is None:
            self._show_tip(self.GetGridCursorRow(), self.GetGridCursorCol())        
        evt.Skip()
        
    def __OnKillFocus(self, evt):
        self._hide_tip_window()        
        evt.Skip()

    # def __OnGirdLabelLeftClicked(self, evt):
    #     if evt.GetRow() == -1:
    #         col = evt.GetCol()
    #         tbl = self.GetTable()
    #         if tbl.can_sort_by_col(col):
    #             tbl.sort_by_col(col)
    #             self.Refresh()
    #     evt.Skip()

    def __OnSortCol(self, evt):
        col = evt.GetCol()
        sorting_col = self.GetSortingColumn()
        sorting_asc = self.IsSortOrderAscending()
        tbl = self.GetTable()

        if tbl.can_sort_by_col(col):
            # DO NOT sort while editing a cell!
            if self.IsCellEditControlShown():
                evt.Veto()
                return

            if col == sorting_col:
                asc = not sorting_asc
            else:
                asc = True

            tbl.sort_by_col(col, asc)
            # self.SetSortingColumn(col, asc)
            return

        evt.Skip()
    
    def __OnEnterWindow(self, evt):        
        if self._tip_window is None:
            self._show_tip(self.GetGridCursorRow(), self.GetGridCursorCol())
        evt.Skip()   
        
    def __OnLeaveWindow(self, evt):        
        self._hide_tip_window()        
        evt.Skip()
            
    def __OnPositionTip(self, evt):
        self.position_tip()
        evt.Skip()
        
    def __OnSize(self, evt):
        self.auto_size()
        
        self.position_tip()
        evt.Skip()
         
    def __OnCellChanged(self, evt):        
        cursor_row, cursor_col = self.GetGridCursorRow(), self.GetGridCursorCol()
        row, col = evt.GetRow(), evt.GetCol()
        
        if (row, col) == (cursor_row, cursor_col):
            self.hide_tip()
            self.show_tip(row, col)
        
        self.refresh_block((row, col, row, col))
        evt.Skip()

    def goto_ref(self):
        row, col = self.GetGridCursorRow(), self.GetGridCursorCol()
        at = self.GetTable().get_attr_type(row, col)
        if type(at) is ATRef:
            uuid = self.GetTable().get_attr_value(row, col)
            if uuid:
                obj = self.editor_context.project.get_object(uuid, at.clazz_name)
                if obj:
                    self.editor_context.project.explorer.show_editor(obj)

    def get_actions(self):
        """
        :return:
        :rtype: list[GridAction]
        """
        return [GridAction(hotkey.GOTO_REF, self.goto_ref, "Goto", "icons/goto.png"),
                GridAction(hotkey.COPY, self._copy, "Copy", "icons/copy.png"),
                GridAction(hotkey.PASTE, self._paste, "Paste", "icons/paste.png", self.is_editable),
                GridAction(hotkey.UNDO, self.undo, "Undo", "icons/undo.png"),
                GridAction(hotkey.REDO, self.redo, "Redo", "icons/redo.png"),
                GridAction(hotkey.RESET, self.reset_to_default, "Reset", "icons/reset.png", self.is_editable),
                GridAction(hotkey.COPY_TEXT, self._copy_as_plain_text, "Copy as plain text", "icons/copy_text.png"),
                GridAction(hotkey.SELECT_ALL, self._select_all, "Select all", "icons/select_all.png"),
                # GridAction(hotkey.PASTE_TEXT, self._paste_plain_text, "Paste plain text", "icons/paste_text.png"),
                ]

    def undo(self):
        self.editor_context.undo_manager.undo(self)

    def redo(self):
        self.editor_context.undo_manager.redo(self)

    def is_editable(self):
        return not self.is_read_only()

    def is_read_only(self):
        return self._ctx.read_only
    
    def _select_cols(self):
        # selection block 
        block = self._get_selection_block()
        if not block:
            wx.MessageBox("Invalid selection area", "Error")
            return
        
        _, left, _, right = block
        
        self.SelectCol(left, False)
        for c in xrange(left+1, right+1):
            self.SelectCol(c, True)

    # noinspection PyMethodMayBeStatic
    def _set_clipboard(self, attr_types, data):
        data = json.dumps([[at.name for at in attr_types], data])
        
        # save to system clipboard        
        do = wx.CustomDataObject(CLIPBOARD_DATA_FORMAT)
        do.SetData(data)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(do)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")
            
    def _get_clipboard(self):
        # read system clip board      
        success = False
        do = wx.CustomDataObject(CLIPBOARD_DATA_FORMAT)
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            
        if not success:
            # clip board data not match, try to paste strings
            names, data = self._get_text_clipboard()
            if not names:
                wx.MessageBox("invalid clipboard type")
            return names, data
        
        # get data
        data = do.GetData()
        attr_type_names, data = json.loads(data)
        
        if len(data) == 0 or len(data[0]) == 0:
            wx.MessageBox("empty clipboard data")
            return None, None
        
        return attr_type_names, data

    # noinspection PyMethodMayBeStatic
    def _get_text_clipboard(self):
        do = wx.TextDataObject()            
        if wx.TheClipboard.Open():
            wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
        else:
            return None, None

        # get text from clipboard
        text = do.GetText()
        # each line represents a row
        lines = text.split('\n')
        # remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()

        if not lines:
            return None, None

        # split each line with "\t" (columns are separated by \t)
        data = [line.split('\t') for line in lines]

        attr_type_names = ['Str'] * len(data[0])
        
        # # guess types
        # for i in xrange(len(data[0])):
        #     is_int = True
        #     for row in data:
        #         # noinspection PyBroadException
        #         try:
        #             int(row[i])
        #         except:
        #             is_int = False
        #             break
        #
        #     if is_int:
        #         attr_type_names[i] = 'Int'
        #         for row in data:
        #             row[i] = int(row[i])

        return attr_type_names, data

    # noinspection PyMethodMayBeStatic
    def check_paste(self, attr_type, attr_type_name, values):
        if attr_type.name == attr_type_name:
            return True, values

        new_values = []
        for val in values:
            # noinspection PyBroadException
            try:
                new_values.append(attr_type.convert(val))
            except InconvertibleError, e:
                wx.MessageBox("type not match or convertible, expected: %s was: %s" % (attr_type.name, attr_type_name),
                              "Error")
                return False, None
            except Exception, e:
                wx.MessageBox('Error while converting "%s"(%s) to %s: %s' % (val, attr_type_name, attr_type, e),
                              "Error")
                # return
                return False, None

        return True, new_values

    def _select_all(self):
        tbl = self.GetTable()
        for c in xrange(tbl.GetNumberCols()):
            can_select = True
            for r in xrange(tbl.GetNumberRows()):
                if self.IsReadOnly(r, c):
                    can_select = False
                    break

            if can_select:
                self.SelectCol(c, True)

    def _copy_as_plain_text(self):
        block = self._get_selection_block()
        if not block:
            wx.MessageBox("Invalid selection area", "Error")
            return

        attr_types, data = self.make_copy_data(block)
        text_data = [[attr_types[i].str(cell, self._ctx.project) for i, cell in enumerate(row)] for row in data]
        text = '\n'.join(['\t'.join(row) for row in text_data])
        self._set_plain_text_clipboard(text)

    def _paste_plain_text(self):
        pass

    # noinspection PyMethodMayBeStatic
    def _set_plain_text_clipboard(self, text):
        do = wx.TextDataObject()
        do.SetText(text)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(do)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")
    
    def _copy(self):
        # block = self._get_selection_block()
        # if not block:
        wx.MessageBox("Copy not supported!", "Error")

    def make_copy_data(self, block):
        raise NotImplementedError('make_copy_data')
    
    def _paste(self):
        attr_type_names, data = self._get_clipboard()
        if attr_type_names is None:
            return
        
        self._paste_data(attr_type_names, data)
    
    def _paste_data(self, attr_type_names, data):
        wx.MessageBox("Paste not supported!", "Error")
        
    def reset_to_default(self):
        block = self._get_selection_block()
        
        # make sure every cell is editable
        top, left, bottom, right = block
        for r in xrange(top, bottom+1):        
            for c in xrange(left, right+1):                
                if self.IsReadOnly(r, c):
                    wx.MessageBox(u'One or more cells are read only!')
                    return
            
        tbl = self.GetTable()
        # create default data
        data = []
        for r in xrange(top, bottom+1):
            row_data = []
            for c in xrange(left, right+1):
                at = tbl.get_attr_type(r, c)                
                cell_data = at.get_default(self.editor_context.project)
                row_data.append(cell_data)
            data.append(row_data)
                        
        self.batch_mutate(block, data, add_undo=True)
        
    def batch_mutate(self, block, data, add_undo=False):
        top, left, bottom, right = block
        tbl = self.GetTable()
        old = None
        
        if add_undo:
            # old value        
            block = (top, left, bottom, right)
            _, old = self.make_copy_data(block)
        
        # paste data
        for i, r in enumerate(xrange(top, bottom+1)):
            # fill repeatedly
            k = i % len(data)
            for j, c in enumerate(xrange(left, right+1)):
                tbl.set_value(r, c, copy.deepcopy(data[k][j]))
        
        if add_undo:
            _, new = self.make_copy_data(block)
            
            from structerui.editor.undo import BatchMutateAction        
            self._ctx.undo_manager.add(BatchMutateAction(top, left, old, new))
        
        # refresh area
        self.refresh_block((top, left, bottom, right))
    
    def _get_selection_block(self):
        """Returns continuous selection block, or None"""
        max_row = self.GetNumberRows() - 1
        max_col = self.GetNumberCols() - 1
        
        # min outer rect
        top, left, bottom, right = max_row, max_col, 0, 0
        
        tls = self.GetSelectionBlockTopLeft()
        brs = self.GetSelectionBlockBottomRight()
        blocks = [(tls[i][0], tls[i][1], brs[i][0], brs[i][1]) for i in xrange(len(tls))]
        for bt, bl, bb, br in blocks:            
            if bt < top:
                top = bt
            if bl < left:
                left = bl
            if bb > bottom:
                bottom = bb
            if br > right:
                right = br
                
        rows = self.GetSelectedRows()
        for row in rows:
            left, right = 0, max_col
            top = min(top, row)
            bottom = max(bottom, row)
        
        cols = self.GetSelectedCols()
        for col in cols:
            top, bottom = 0, max_row
            left = min(left, col)
            right = max(right, col)
        
        cells = self.GetSelectedCells()
        cells.append((self.GetGridCursorRow(), self.GetGridCursorCol()))
        for cr, cc in cells:
            if cr < top:
                top = cr
            if cr > bottom:
                bottom = cr
            if cc < left:
                left = cc
            if cc > right:
                right = cc
        
        def _check(r_, c_):
            for bt_, bl_, bb_, br_ in blocks:
                if bt_ <= r_ <= bb_ and bl_ <= c_ <= br_:
                    return True
            if r_ in rows or c_ in cols:
                return True
            if (r_, c_) in cells:
                return True
            return False                
        
        for r in xrange(top, bottom+1):
            for c in xrange(left, right+1):
                if not _check(r, c):
                    return None
        
        return top, left, bottom, right
    
    def __OnCharHook(self, evt):
        key = evt.GetKeyCode()
        
        if key == wx.WXK_RETURN or key == wx.WXK_NUMPAD_ENTER:
            self.DisableCellEditControl()
            
            # exactly like Excel
            if evt.ShiftDown():
                self.MoveCursorUp(False)
            else:
                self.MoveCursorDown(False)
            return
        
        if key == wx.WXK_TAB:
            # todo: can get TAB event on a combobox
            self.DisableCellEditControl()
            
            # exactly like Excel
            if evt.ShiftDown():
                self.MoveCursorLeft(False)
            else:
                self.MoveCursorRight(False)
            return
        
        evt.Skip()
        
    def refresh_block(self, block):                
        self.RefreshAttr(self.GetGridCursorRow(), self.GetGridCursorCol())
        
        top, left, bottom, right = block
        tl = self.CellToRect(top, left)        
        br = self.CellToRect(bottom, right)
        rect = wx.Rect(tl.left, tl.top, br.right-tl.left, br.bottom-tl.top)        
        self.GetGridWindow().RefreshRect(rect)    


class CellTipWindow(wx.PopupWindow):
    """Show errors/warnings of cells with a tip window.
        
       Fatal(s)/Errors/Warnings are shown in different font color/styles
    """
    def __init__(self, parent, vlog, width=200):
        wx.PopupWindow.__init__(self, parent)
        
        bg_color = wx.Colour(0xFF, 0xFF, 0x88)
        self.SetBackgroundColour(bg_color)
                
        margin = 2
        text_width = max(100, width - margin * 2)
        x = y = margin
        ctrl_width = 0
        
#         all_ = itertools.chain(vlog.errors, tracker.errors, tracker.warnings)
#         msgs = [(record.level, record.format()) for record in all_]
#             
#         
#         MAX = 10
#         if len(msgs)>MAX:
#             hide = len(msgs) - MAX
#             msgs = msgs[:MAX]
#             msgs.append( (2, '......%s more' % hide) )
#             msgs.append( (2, '%s fatals, %s errors, %s warnings'% \
#                           (len(tracker.fatals), len(tracker.errors), len(tracker.warnings))) )
#             
#         for lvl, text in msgs:                        
#             text_ctrl = wx.StaticText(self, -1, text)
#             text_ctrl.Wrap(text_width)
#             text_ctrl.SetBackgroundColour( bg_color )
#             text_ctrl.SetForegroundColour( wx.BLACK if lvl==log.WARN else wx.RED )
#             text_ctrl.GetFont().SetWeight( wx.FONTWEIGHT_BOLD if lvl==log.FATAL else wx.FONTWEIGHT_NORMAL )
#             text_ctrl.SetPosition( wx.Point(x, y))
#             ctrl_width = max(ctrl_width, text_ctrl.GetSize().width)
#             y += text_ctrl.GetSize().height
        max_ = 10
        msgs = [e.str() for e in vlog.errors]
        if len(msgs) > max_:
            hide = len(msgs) - max_
            msgs = msgs[:max_]
            msgs.append('......%s more' % hide)
            
        for text in msgs:                        
            text_ctrl = wx.StaticText(self, -1, text)
            text_ctrl.Wrap(text_width)
            text_ctrl.SetBackgroundColour(bg_color)
            text_ctrl.SetForegroundColour(wx.BLACK)
            # text_ctrl.GetFont().SetWeight( wx.FONTWEIGHT_NORMAL )
            text_ctrl.SetPosition(wx.Point(x, y))
            ctrl_width = max(ctrl_width, text_ctrl.GetSize().width)
            y += text_ctrl.GetSize().height
            
        # size        
        self.SetSize(wx.Size(ctrl_width + margin*2, y + margin))
        
        # event
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
                   
    def OnKeyDown(self, evt):
        # key = evt.GetKeyCode()
        # print 'tip.onkeydown'
        self.Close()
        self.Destroy()            
        evt.Skip()


class GridAction(object):
    def __init__(self, hot_key_tr, callback, label, icon=None, check_enable=None, is_check_type=False):
        """

        :param str hot_key_tr:
        :param function callback:
        :param str label: label for tool/menu
        :param str icon: path for menu/toolbar icon
        :param function check_enable: EVT_UPDATE_UI
        :return:
        """
        self.hot_key_tr = hot_key_tr
        self.callback = callback
        self.label = label
        self.icon = icon
        self.check_enable = check_enable
        self.is_check_type = is_check_type
