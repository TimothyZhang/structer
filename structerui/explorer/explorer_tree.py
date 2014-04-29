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

'''
Created on 2013-11-21

@author: Administrator
'''
import time

import wx

from structer.fs_manager import FSEvent
from structer import fs_util

from structerui import log

from fs_node_tool import FSNodeTool

    
class ExplorerTree(wx.TreeCtrl, wx.DropTarget):
    '''The tree ctrl of explorer frame, which shows all folders and filters
    '''    
    def __init__(self, parent, explorer):
        self._explorer = explorer        
        self._node_tool = FSNodeTool(explorer, self)
        # {FileNode: wxTreeItemId}
        self._fs_node_to_tree_item_id = {}
        self._name_to_image_id = {}
        
        # tree ctrl
        style = wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_SINGLE
        # wx.TR_HAS_VARIABLE_ROW_HEIGHT |
        wx.TreeCtrl.__init__(self, parent, -1, style = style)       
        self._bind_tree_events()
        self._init_image_list()
        
        self._init_drop_target()
        self.SetDropTarget(self)
        
        self.update_project()        
        
    def _init_image_list(self):
        image_list, mapping = self.node_tool.create_image_list()
        self.SetImageList(image_list)
        
        # SHOULD keep a reference to image list, otherwise it'll be released immediately
        self._image_list = image_list
        self._name_to_image_id = mapping        
                       
    def _bind_tree_events(self):

        self.Bind(wx.EVT_TREE_ITEM_MENU, self._on_item_menu)         

        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self._on_begin_label_edit)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self._on_end_label_edit)
                
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self._sel_changed)
        # double clicked
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_active)
        # DnD
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag)        
                
    @property
    def project(self):
        return self._explorer.project
    
    @property
    def explorer(self):
        return self._explorer      
    
    @property
    def node_tool(self):
        return self._node_tool
    
    def update_project(self):
        self.DeleteAllItems()
                    
        if not self.project:
            return 
        
        project = self.project
        
        # File System Events
        project.event_manager.register(FSEvent.get_key_of(FSEvent.CREATE), self._on_fs_create)
        project.event_manager.register(FSEvent.get_key_of(FSEvent.MODIFY), self._on_fs_modify)
        project.event_manager.register(FSEvent.get_key_of(FSEvent.DELETE), self._on_fs_delete)
        project.event_manager.register(FSEvent.get_key_of(FSEvent.MOVE), self._on_fs_move)
        
        root_fs_node = project.fs_manager.root
        
        root_tree_item_id = self.AddRoot("ROOT", 
                                         image = self.get_image_id_by_node(root_fs_node), 
                                         data  = wx.TreeItemData(root_fs_node))
        self._fs_node_to_tree_item_id[root_fs_node] = root_tree_item_id 
                
        if self._add_children(root_tree_item_id):
            self.SetItemHasChildren(root_tree_item_id, True)
            self.Expand(root_tree_item_id)
            
        self._init_image_list()
    
    def set_path(self, fs_node):
        '''
        Args:
            fs_node: Folder, or a filter
        '''
        tree_item_id = self._get_tree_item_id_by_fs_node(fs_node)
        assert tree_item_id
                
        self.SelectItem(tree_item_id)            
    
    def _add_children(self, tree_item_id):
        '''Adds all children of a tree item
        
        Returns:
            Number of children.
        '''
        fs_node = self._get_fs_node_by_tree_item_id(tree_item_id)
        if not fs_node:
            return
        
        assert self.node_tool.is_container(fs_node)
        
        n = 0
        if fs_node.is_folder():
            for child_fs_node in self.node_tool.get_children(fs_node):
                if self.node_tool.is_container(child_fs_node):
                    self._add_child(tree_item_id, child_fs_node)                
                    #self._add_children(child_tree_item_id)
                    n += 1
        return n
    
    def _add_child(self, parent_tree_item_id, child_fs_node):
        '''Adds a fs_node to a tree item'''
        try:
            child_tree_item_id = self.AppendItem(parent_tree_item_id, 
                                                 text = self.node_tool.get_name(child_fs_node),
                                                 image = self.get_image_id_by_node(child_fs_node),
                                                 data  = wx.TreeItemData(child_fs_node))
            
            self._fs_node_to_tree_item_id[child_fs_node] = child_tree_item_id        
            
            if self._add_children(child_tree_item_id):
                self.SetItemHasChildren(child_tree_item_id, True)
    
            return child_tree_item_id
        except:
            log.error('failed to add child: %s', child_fs_node.uuid)
            raise
        
    def get_image_id_by_name(self, name):
        i = self._name_to_image_id.get(name, -1)
        if i == -1:
            i = self._name_to_image_id.get('miss.png', -1)
        return i
    
    def get_image_id_by_node(self, node):
        image_name = self.node_tool.get_icon(node)
        return self.get_image_id_by_name(image_name)
    
    def _get_fs_node_by_tree_item_id(self, tree_item_id):
        if tree_item_id and tree_item_id.IsOk():
            tree_item_data = self.GetItemData(tree_item_id)
            return tree_item_data.GetData()
    
    def _get_tree_item_id_by_fs_node(self, fs_node):
        tree_item_id = self._fs_node_to_tree_item_id.get(fs_node)
        if tree_item_id and tree_item_id.IsOk():
            return tree_item_id
    
    def _get_fs_node_by_indices(self, index):
        if not self._project:
            return
        
        if index==():  # tree root, parent of file root
            return None
        
        node = self._project.fs_manager.root
        for i in index[1:]:
            node = node.children[i]
        return node
    
    def get_selected_nodes(self):
        tree_item_id = self.GetSelection()
        if tree_item_id.IsOk():
            return [self._get_fs_node_by_tree_item_id(tree_item_id)]
        return []        

    ################################################################                            
    # Tree Event Handlers 
    ################################################################
    def _on_item_menu(self,evt):        
        fs_node = self._get_fs_node_by_tree_item_id(evt.GetItem())
        
        menu = self.node_tool.get_menu([fs_node])
        if menu:
            # stores the fs_node which pops context menu 
            self._menu_fs_node = fs_node 
            self.PopupMenu(menu)            
            menu.Destroy()
            del self._menu_fs_node
    
    def _on_begin_label_edit(self,evt):
  
        pass
    
    def _on_end_label_edit(self,evt):
        new_name = evt.GetLabel()        
        tree_item_id = evt.GetItem()

        if not new_name:
            evt.Veto()
            return        
        
        fs_node = self._get_fs_node_by_tree_item_id(tree_item_id)
        if not self.node_tool.rename(fs_node, new_name):
            evt.Veto()
            return
        
        evt.Skip()
        
    def _sel_changed(self, evt):
        tree_item_id = evt.GetItem()
        fs_node = self._get_fs_node_by_tree_item_id(tree_item_id)
        
        self.node_tool.open(fs_node)
        #self.explorer.set_path( fs_node )
        
    def _on_active(self,evt):
        tree_item_id = evt.GetItem()
        fs_node = self._get_fs_node_by_tree_item_id(tree_item_id)
        
        self.node_tool.open(fs_node)
        #self.explorer.set_path( fs_node )
        evt.Skip()        
    
    def _on_begin_drag(self,evt):
        #nodes = self.get_selected_nodes()
        tree_item_id = evt.GetItem()
        fs_node = self._get_fs_node_by_tree_item_id(tree_item_id)
        self.node_tool.begin_drag([fs_node], self)
    
    ################################################################                            
    # FSEvent Handlers 
    ################################################################     
    def _on_fs_create(self, evt):        
        fs_node = evt.fs_node
        
        #if fs_node.is_folder():
        if self.node_tool.is_container(fs_node):
            parent_tree_item_id = self._get_tree_item_id_by_fs_node(fs_node.parent)
            self._add_child(parent_tree_item_id, fs_node)
            
            #if self.HasFocus():
                #self.EditLabel( tree_item_id )
    
    def _on_fs_modify(self, evt):
        fs_node = evt.fs_node
        tree_item_id = self._get_tree_item_id_by_fs_node(fs_node)
        
        if not tree_item_id:
            return
        
        # update label
        if fs_node.is_folder():            
            self.SetItemText(tree_item_id, fs_node.name)
        elif fs_util.is_filter(fs_node):
            self.SetItemText(tree_item_id, fs_node.name)        
    
    def _on_fs_move(self, evt):
        fs_node = evt.fs_node
        tree_item_id = self._get_tree_item_id_by_fs_node(fs_node)
        
        if tree_item_id:
            self.Delete(tree_item_id)
        
        if self.node_tool.is_container(fs_node):
            parent_tree_item_id = self._get_tree_item_id_by_fs_node(fs_node.parent)
            if parent_tree_item_id:
                self._add_child(parent_tree_item_id, fs_node) 
    
    def _on_fs_delete(self, evt):
        fs_node = evt.fs_node
        tree_item_id = self._get_tree_item_id_by_fs_node(fs_node)
        
        if not tree_item_id:
            return
        
        self.Delete(tree_item_id)
        
    ################################################################################
    # DropTarget
    ################################################################################
    def _init_drop_target(self):
        wx.DropTarget.__init__(self)
        
        # specify the type of data we will accept
        from fs_node_tool import CLIPBOARD_DATA_FORMAT
        self.data = wx.CustomDataObject(CLIPBOARD_DATA_FORMAT)
        self.SetDataObject(self.data)
        
        self._drop_selected = None
        self._drag_over_time = 0
        
    # some virtual methods that track the progress of the drag
    def OnEnter(self, x, y, d):
        return self.OnDragOver(x, y, d)

    def OnLeave(self):        
        self._restore_drop_target()        
    
    def _restore_drop_target(self):
        if self._drop_selected is not None:
            self.SetItemDropHighlight (self._drop_selected, False)
            self._drop_selected = None            
            self._drag_over_time = 0            
    
    def OnDrop(self, x, y):
        return True

    def OnDragOver(self, x, y, d):        
        tree_item_id, _ = self.HitTest(wx.Point(x, y))
        if tree_item_id.IsOk():
            if self._drop_selected != tree_item_id:
                self._restore_drop_target()
                                
                self._drop_selected = tree_item_id
                self._drag_over_time = time.time()
                self.SetItemDropHighlight (self._drop_selected, True)                
            else:
                dt = time.time() - self._drag_over_time
                if dt > 1.0 and not self.IsExpanded(tree_item_id):  # holds more than 1 second
                    self.Expand(tree_item_id)
                        
            target = self._get_fs_node_by_tree_item_id(tree_item_id)            
            if target and target.is_folder():
                if d == wx.DragCopy:
                    if self.node_tool.can_paste_data(target, 'copy'):
                        return d
                elif d == wx.DragMove:
                    if self.node_tool.can_paste_data(target, 'cut'):
                        return d
        else:
            self._restore_drop_target()          
                    
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
            
            tree_item_id, _ = self.HitTest(wx.Point(x, y))
            target = self._get_fs_node_by_tree_item_id(tree_item_id)
            assert target and target.is_folder()
                            
            if d == wx.DragCopy:
                self.node_tool.do_paste_data(target, uuids, 'copy')
            elif d == wx.DragMove:
                self.node_tool.do_paste_data(target, uuids, 'cut')            
        
        # OnLeave was not called, so we have to do it manually
        self._restore_drop_target()
        
        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d  
