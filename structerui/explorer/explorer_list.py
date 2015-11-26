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



import copy

import wx

from structer import fs_util
from structer.fs_manager import FSEvent

from structerui import log, hotkey, util

from fs_node_tool import FSNodeTool

class ExplorerList(wx.ListCtrl, wx.DropTarget):
    def __init__(self, parent, explorer):
        self._explorer = explorer
        self._node_tool = FSNodeTool(explorer, self)
        self._name_to_image_id = {}

        self._fs_parent = None      # Folder or Filter
        self._fs_nodes = []
        self._history = []          # navigation history
        self._history_index = -1;
        # 'id', 'name', 'time'
        self._sort_by = 'name'
        self._ascending = True
        
        if util.is_mac():
            style = wx.LC_REPORT | wx.BORDER_NONE | wx.LC_EDIT_LABELS | wx.LC_VIRTUAL
        else: 
            style = wx.LC_ICON | wx.BORDER_NONE | wx.LC_EDIT_LABELS | wx.LC_VIRTUAL

        #| wx.LC_SORT_ASCENDING#| wx.LC_NO_HEADER#| wx.LC_VRULES#| wx.LC_HRULES#| wx.LC_SINGLE_SEL
        wx.ListCtrl.__init__(self, parent, -1, style=style)
        self._init_image_list()        
        self._init_list_columns()
        self._init_list_item_attrs()        
        self._bind_list_events()
        
        self._init_drop_target()
        self.SetDropTarget(self)
        
    
    def _init_list_columns(self):
        self.InsertColumn(0, u"Name")
        self.InsertColumn(1, u"Type")
        self.InsertColumn(2, u"Modified")
        self.SetColumnWidth(0, 200)
        self.SetColumnWidth(1, 100)
        self.SetColumnWidth(2, 200)
        
        
    def _init_list_item_attrs(self):
        self.attr_normal = wx.ListItemAttr()
        
        self.attr_error = wx.ListItemAttr()
        self.attr_error.SetBackgroundColour( wx.Colour(0xFF, 0x88, 0x88, 0xFF) )
        #self.attr_error.SetTextColour( wx.Colour(0xFF, 0x88, 0x88, 0xFF) )
    
    
    def _init_image_list(self):
        image_list, mapping = self.node_tool.create_image_list()
        self.SetImageList(image_list, wx.IMAGE_LIST_SMALL)
        
        if not util.is_mac():
            image_list, mapping = self.node_tool.create_image_list(size=(64,64))
            self.SetImageList(image_list, wx.IMAGE_LIST_NORMAL)
        #self.SetImageList(image_list, wx.IMAGE_LIST_NORMAL)
        self._image_list = image_list
        self._name_to_image_id = mapping  
    
    def _bind_list_events(self):
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self._on_begin_label_edit)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self._on_end_label_edit)
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_item_right_clicked)        
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)   
        
        #self.Bind(wx.EVT_LIST_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
        
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self._on_begin_drag)        
    
    @property
    def project(self):
        return self._explorer.project
    
    @property
    def explorer(self):
        return self._explorer      
    
    @property
    def node_tool(self):
        return self._node_tool
    
    @property
    def fs_parent(self):
        return self._fs_parent
    
    def has_item(self):
        return self.GetItemCount() > 0

    def get_image_id_by_name(self, name):
        i = self._name_to_image_id.get(name, -1)
        if i == -1:
            i = self._name_to_image_id.get('miss.png', -1)
        return i

    def get_image_id_by_node(self, node):
        image_name = self.node_tool.get_icon(node)
        return self.get_image_id_by_name(image_name)    
    
    def update_project(self):
        em = self.project.event_manager
        
        # File System Events
        em.register(FSEvent.get_key_of(FSEvent.CREATE), self._on_fs_create)
        em.register(FSEvent.get_key_of(FSEvent.MODIFY), self._on_fs_modify)
        em.register(FSEvent.get_key_of(FSEvent.MOVE), self._on_fs_move)
        em.register(FSEvent.get_key_of(FSEvent.DELETE), self._on_fs_delete)
        
        self._init_image_list()
    
    def set_parent(self, fs_node, history=0):
        '''Sets the parent node, whose children will be added to current list
        
        Args:
            fs_node: Folder, or a filter
            history: 0:new entry, -1:prev 1:next
        '''
        assert self.node_tool.is_container(fs_node)
        
        self._fs_parent = fs_node        
        self.refresh()

        self.explorer.update_menu_new()
        
        # history
        if history == 0:
            if len(self._history) == 0 or self._history[self._history_index] != fs_node:
                self._history = self._history[:self._history_index + 1]
                self._history.append(fs_node)
                self._history_index += 1
        else:
            self._history_index += history
            assert 0 <= self._history_index < len(self._history)

        # print self._history
        # print self._history_index

    def history_prev(self):
        if self._history_index > 0:
            self.set_parent(self._history[self._history_index - 1], -1)
            return True

    def history_next(self):
        if self._history_index < len(self._history) - 1:
            self.set_parent(self._history[self._history_index + 1], 1)
            return True

    def _node_cmp(self, x, y):
        r = 0
        if self._sort_by == 'name':
            a = self.node_tool.get_name(x).lower()
            b = self.node_tool.get_name(y).lower()
            r = cmp(a, b)
        elif self._sort_by == 'id':
            a = self.node_tool.get_id(x)
            b = self.node_tool.get_id(y)
            r = cmp(a, b)
            if r == 0:
                a = self.node_tool.get_name(x).lower()
                b = self.node_tool.get_name(y).lower()
                r = cmp(a, b)
        elif self._sort_by == 'time':
            r = cmp(x.modify_time, y.modify_time)
        elif self._sort_by == 'type':
            a = self.node_tool.get_type(x)
            b = self.node_tool.get_type(y)
            r = cmp(a, b)

        if not self._ascending:
            r = -r
        return r

    def refresh(self):
        print '>>>refresh'
        if self._fs_parent is None:
            self.SetItemCount(0)
            self.Refresh()
            return        
        
        selected_nodes = self.get_selected_nodes()
        focused_item = self.GetFocusedItem()
        focused_node = self._fs_nodes[focused_item] if focused_item != -1 else None

        #print 'item count:', len(self._fs_nodes) 
        self._fs_nodes = copy.copy( self.node_tool.get_children(self._fs_parent) )

        self._fs_nodes.sort(self._node_cmp)

        self.SetItemCount(len(self._fs_nodes))
        #self.sort()
        self.Refresh()       
        
        self.clear_selection()
        if selected_nodes:
            for n in selected_nodes:
                index = self.get_index_by_node(n)
                if index != -1:
                    self.Select(index, True)
        elif self.GetItemCount() > 0:
            self.single_select(0)
            
        if focused_node and self.GetItemCount() > 0:
            index = self.get_index_by_node(focused_node)
            self.Focus(index)

    def get_selected_nodes(self):
        nodes = []
        
        for i in xrange( self.GetItemCount() ):
            list_item_state = self.GetItemState(i, wx.LIST_STATE_SELECTED)            
            if (list_item_state & wx.LIST_STATE_SELECTED) != 0:
                nodes.append( self._fs_nodes[i] )
        
        return nodes
    
    def get_focused_node(self):
        idx = self.GetFocusedItem()
        if idx == -1:
            return
        return self._fs_nodes[idx]
    
    def get_index_by_node(self, fs_node):
        try:
            i = self._fs_nodes.index(fs_node)                
        except ValueError:
            i = -1
        return i
    
    def single_select(self, index):
        self.Focus(index)        
        
        self.clear_selection()
        self.Select(index, True)
        
    def single_select_node(self, fs_node):
        index = self.get_index_by_node(fs_node)
        if index!=-1:
            self.single_select(index)
        
    def select_all(self):
        for i in xrange( self.GetItemCount() ):
            self.Select(i, True)
    
    def inverse_select(self):
        for i in xrange( self.GetItemCount() ):
            list_item_state = self.GetItemState(i, wx.LIST_STATE_SELECTED)            
            if (list_item_state & wx.LIST_STATE_SELECTED) != 0:
                self.Select(i, False)
            else:
                self.Select(i, True)

    def clear_selection(self):
        for i in xrange(self.GetItemCount()):
            list_item_state = self.GetItemState(i, wx.LIST_STATE_SELECTED)
            if (list_item_state & wx.LIST_STATE_SELECTED) != 0:
                self.Select(i, False)
                
    def sort_by(self, key=None, ascending=None):
        if key is None:
            key = self._sort_by
        if ascending is None:
            ascending = self._ascending

        if self._sort_by != key or self._ascending != ascending:
            self._sort_by = key
            self._ascending = ascending
            self.refresh()
        
    ################################################################################
    # ListCtrl "virtualness"
    ################################################################################    
    def OnGetItemText(self, item, col):
        #print 'OnGetItemText', item, col
        fs_node = self._fs_nodes[item]
        if col==0:
            return self.node_tool.get_name(fs_node)
        elif col==1:
            return self.node_tool.get_type(fs_node)
        elif col==2:
            return self.node_tool.get_modify_time(fs_node)

    def OnGetItemImage(self, item):
        fs_node = self._fs_nodes[item]
        return self.get_image_id_by_node(fs_node)
        
    def OnGetItemAttr(self, item):    
        fs_node = self._fs_nodes[item]
        if fs_util.is_object(fs_node):
            obj = self.project.get_object_by_fsfile(fs_node)
            if obj:     # nodes in Recycle will return None
                if obj.has_error():
                    return self.attr_error
        return self.attr_normal        
    
    ################################################################################
    # ListCtrl Handlers
    ################################################################################
    def _on_begin_label_edit(self, evt):
        index = evt.GetIndex()        
        fs_node = self._fs_nodes[index]
        
        if not self.node_tool.can_rename(fs_node):            
            evt.Veto()
            return
        
        evt.Skip()
        
    def _on_end_label_edit(self, evt):
        new_name = evt.GetLabel()        
        index = evt.GetIndex()
        fs_node = self._fs_nodes[index]

        if not new_name:
            evt.Veto()
            return                
        
        if not self.node_tool.rename(fs_node, new_name):
            evt.Veto()
            return
        
        evt.Skip()
    
    def _on_item_selected(self, evt):
        #print '_on_item_selected'
        evt.Skip()
    
    def _on_item_right_clicked(self, evt):
        print '_on_item_right_clicked'
        nodes = self.get_selected_nodes()
        menu = self.node_tool.get_menu(nodes)
        if menu:
            self.PopupMenu(menu)
            menu.Destroy()            
    
    def _on_right_down(self, evt):        
        self.SetFocus()
        
        x, y = evt.GetX(), evt.GetY()
        item,_ = self.HitTest(wx.Point(x, y))
        
        if not 0<=item<=self.GetItemCount():
            nodes = [self._fs_parent]
            menu = self.node_tool.get_menu(nodes)
            if menu:
                self.PopupMenu(menu)
                menu.Destroy()
            return
            
        evt.Skip()
    
    def _on_char_hook(self, evt):
        keystr = hotkey.build_keystr(evt)
        
        # editing label, skip
        if self.GetEditControl():
            evt.Skip()
            return
        
        if hotkey.check(hotkey.EXPLORER_OPEN, keystr):        
            fs_nodes = self.get_selected_nodes()
            if len(fs_nodes)==1:
                fs_nodes = fs_nodes[0]
            if self.node_tool.can_open(fs_nodes):
                self.node_tool.open(fs_nodes)
                return
        
        if hotkey.check(hotkey.EXPLORER_RENAME, keystr):
            fs_node = self.get_focused_node()            
            if self.node_tool.can_rename(fs_node):
                self.EditLabel(self.GetFocusedItem())
                return

        evt.Skip()
    
    def _on_left_dclick(self, evt):        
        x, y = evt.GetX(), evt.GetY()
        item,_ = self.HitTest(wx.Point(x, y))
        
        if 0<=item<=self.GetItemCount():
            node = self._fs_nodes[ item ]
            if self.node_tool.can_open( node ):
                self.node_tool.open( node )
            return
        
        evt.Skip()
    
    def _on_begin_drag(self, evt):
        nodes = self.get_selected_nodes()                
        self.node_tool.begin_drag(nodes, self)
        
    ################################################################################
    # FSEvent Handlers
    ################################################################################
    def _on_fs_create(self, evt):
        fs_node = evt.fs_node
        
        # Impossible!
        assert fs_node != self._fs_parent            
        
        if fs_node.parent == self._fs_parent:
            self.refresh()
            
#             # try to focus, or edit the label
#             i = self.get_index_by_node(fs_node)
#             if i!=-1:
#                 if self.HasFocus():
#                     self.single_select(i)                
#                     if fs_node.is_folder():                            
#                         self.EditLabel(i)
    
    def _on_fs_modify(self, evt):
        fs_node = evt.fs_node
        
        if fs_node == self._fs_parent:            
            return
        
        i = self.get_index_by_node(fs_node)
        if i!=-1:
            self.refresh()
            # self.RefreshItem(i)
            
    def _on_fs_move(self, evt):       
        fs_node = evt.fs_node
        #original_parent = evt.original_parent
        
        # moved out
        if fs_node in self._fs_nodes:
            self.refresh()
            return
        
        # moved in
        if fs_node.parent == self._fs_parent:
            self.refresh()
            return        
        
    def _on_fs_delete(self, evt):
        #print 'list._on_fs_delete'
        fs_node = evt.fs_node
        
        if fs_node == self._fs_parent:
            self._fs_parent = None
            self.refresh()
            return
        
        # child deleted
        if fs_node in self._fs_nodes:
            self.refresh()
            return
            
            #todo: try to select the same item
          
    ################################################################################
    # DropTarget
    ################################################################################
    def _init_drop_target(self):
        wx.DropTarget.__init__(self)
        
        # specify the type of data we will accept
        from fs_node_tool import CLIPBOARD_DATA_FORMAT
        self.data = wx.CustomDataObject(CLIPBOARD_DATA_FORMAT)
        self.SetDataObject(self.data)
        
        self._drop_selected = -1
        
    # some virtual methods that track the progress of the drag
    def OnEnter(self, x, y, d):
        return self.OnDragOver(x, y, d)

    def OnLeave(self):
        if self._drop_selected != -1:
            self.Select(self._drop_selected, False)

    def OnDrop(self, x, y):
#         index, _ = self.HitTest(wx.Point(x, y))
#         if 0<= index < self.GetItemCount():
#             fs_node = self._fs_nodes[index]
#             if not fs_node.is_folder():
#                 return False
#             
#             #self.node_tool.can_paste_data(fs_node,)
#                 
        return True

    def OnDragOver(self, x, y, d):
        index, _ = self.HitTest(wx.Point(x, y))
        
        if index != self._drop_selected:
            self.Select(self._drop_selected, False)
            
        if 0<= index < self.GetItemCount():            
            list_item_state = self.GetItemState(index, wx.LIST_STATE_SELECTED)            
            if (list_item_state & wx.LIST_STATE_SELECTED) == 0:
                self._drop_selected = index
                self.Select(index, True)
                
            target = self._fs_nodes[index]            
            if not target.is_folder():
                return wx.DragNone
        else:
            target = self.fs_parent                        
            
        if d == wx.DragCopy:
            if self.node_tool.can_paste_data(target, 'copy'):
                return d
        elif d == wx.DragMove:
            if self.node_tool.can_paste_data(target, 'cut'):
                return d            
        return wx.DragNone

    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
        print "OnData: %d, %d, %d\n" % (x, y, d)

        # copy the data from the drag source to our data object
        if self.GetData():
            # convert it back to a list of lines and give it to the viewer            
            uuids, _ = self.node_tool.parse_clipboard_data(self.data)
            #nodes = [self.project.fs_manager.get_node_by_uuid(uuid) for uuid in uuids]
            
            index, _ = self.HitTest(wx.Point(x, y))
            if 0 <= index < self.GetItemCount():
                target = self._fs_nodes[index]
                assert target.is_folder()
            else:
                target = self.fs_parent 
                            
            if d == wx.DragCopy:
                self.node_tool.do_paste_data(target, uuids, 'copy')
            elif d == wx.DragMove:
                self.node_tool.do_paste_data(target, uuids, 'cut')            
                        
        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d  
