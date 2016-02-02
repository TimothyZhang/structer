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
There are 4 types of nodes in explorer:
1. FsFolder
2. FsFile(object)
3. FsFile(filter)
4. SearchResult

Only 1,3 might appear in ExplorerTree.
Only 1,3,4 might appear in address bar(as list parent).
Only 1,2,3 might appear in ExplorerList
"""


import time
import json
import collections

from structer import const, fs_util
from structer.exceptions import StructerException
from structer.fs_manager import FOLDER_CONFLICTION_STRATEGY_RENAME, FSNode, Folder
from structer.fs_manager import FOLDER_CONFLICTION_STRATEGY_MERGE
from structer.fs_manager import FolderConflictionException
from structerui.util import *

CLIPBOARD_DATA_FORMAT = "__structer_fs_nodes_ajfdi1209dfsdf923jsdf1f4abz__"

# default_filter = """\"\"\"
# Write a python function with name "choose", which accepts three parameters:
#     obj: the Object instance, all objects in current project will be tested.
#         obj.clazz
#         obj['attribute']
#     file: the File instance
#         file.modify_time: time in seconds
#         file.create_time: time in seconds
#         file.tags: a set of tags of the object
#     project: the Project instance
# \"\"\"
# def choose(obj, file, project):
#     # all monsters whose level is 10
#     if obj.clazz.name == 'Monster' and obj['level'] == 10:
#         return True
#
#     # all objects modified in recent 24 hours, any type
#     #import time
#     #if time.time() - file.modify_time < 3600 * 24:
#      #   return True
#
#     # all objects with tag: X'mas
#     #if "X'mas" in file.tags:
#     #    return True
#
#     return False
# """


class SearchResult(FSNode):
    """
    A temporary FSNode to hold search result.
    """

    immutable = True

    def __init__(self, project, sql, scope, name):
        FSNode.__init__(self, None)
        self._sql = sql
        self.name = name if name else 'Search Result in %s' % scope
        self.parent = project.fs_manager.root

    @property
    def sql(self):
        return self._sql

    def _dump(self):
        raise StructerException('could not dump a SearchResult')


class FSNodeTool(object):
    def __init__(self, explorer, ctrl):
        _ = ctrl
        self._explorer = explorer
    
    @property
    def project(self):
        return self._explorer.project 
    
    @property
    def explorer(self):
        return self._explorer
    
    def create_image_list(self, size=(16, 16)):
        """Creates an image list for nodes

        :param size: size of each image
        :type size: tuple[int]
        :return (wxImageList, name_to_image_id), name_to_image_id is a dict whose key is image name, and value is id in
            that image list
        :rtype: (wx.ImageList, dict[str, id])
        """
        image_list = wx.ImageList(size[0], size[1])
        
        # {image name: image id in list}
        name_to_image_id = {}
        
        # folders
        for name in [ICON_FOLDER, ICON_OBJECT, ICON_FILTER]:
            bmp = get_bitmap(name, size, self.project)
            i = image_list.Add(bmp)
            name_to_image_id[name] = i
        
        if self.project:    
            for clazz in self.project.type_manager.get_clazzes():
                bmp = get_clazz_bitmap(clazz, size, self.project)
                i = image_list.Add(bmp)
                name_to_image_id[clazz.icon] = i
        # self.SetImageList(self._image_list)
        return image_list, name_to_image_id   
    
    def _get_object_by_node(self, node):
        om = self.project.object_manager
        obj = om.get_object(node.uuid)
        if not obj:
            obj = om.get_recycled_object(node.uuid)
        return obj
    
    def get_id(self, node):
        if fs_util.is_object(node):
            obj = self._get_object_by_node(node)
            if obj:
                return obj.id

    def get_name(self, node):
        if fs_util.is_object(node):
            obj = self._get_object_by_node(node)
            if obj:
                # return obj.name
                return obj.get_label()

            return 'Unknown'

        return node.name

    def get_type(self, node):
        if isinstance(node, Folder):
            return 'Folder'
        
        if node.file_type == const.FILE_TYPE_FILTER:
            return 'Filter'
        
        obj = self._get_object_by_node(node)
        if obj:
            return obj.clazz.name
        
        return 'Unknown'

    # noinspection PyMethodMayBeStatic
    def get_modify_time(self, node):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(node.modify_time))
    
    def get_icon(self, node):
        if isinstance(node, Folder):
            return ICON_FOLDER
        
        if node.file_type == const.FILE_TYPE_FILTER:
            return ICON_FILTER
        
        obj = self._get_object_by_node(node)
        if obj and obj.clazz.icon:            
            return obj.clazz.icon    
    
    def _on_create_folder(self, nodes):        
        assert self.can_create(nodes)                
        self.do_create_folder(nodes[0])    
        
    def do_create_folder(self, parent):
        try:
            folder = self.project.fs_manager.create_folder(parent, 'New Folder', FOLDER_CONFLICTION_STRATEGY_RENAME)
        except Exception, e:
            log.alert(e, 'Create folder failed.')            
            return   
        
        index = self._show_node_in_list(folder)
        self.explorer.list.EditLabel(index)
        
    def _on_create_filter(self, nodes):
        assert self.can_create(nodes)
        self.do_create_filter(nodes[0])
    
    def do_create_filter(self, parent):
        try:
            node = self.project.fs_manager.create_file(parent, const.FILE_TYPE_FILTER, 'New Filter', '')
        except Exception, e:
            log.alert(e, "Failed to create filter")   
            return
        
        # edit
        self.edit_filter(node)
        
        # rename
        index = self._show_node_in_list(node)
        self.explorer.list.EditLabel(index)
    
    def _on_create_object(self, nodes, clazz):
        # print '_on_create_object'
        assert len(nodes) == 1
        
        self.do_create_object(nodes[0], clazz)
        
    def can_create(self, nodes):
        if not self.is_project_editable():
            return False
        
        if len(nodes) != 1:
            return False
        
        node = nodes[0]
        fsm = self.project.fs_manager
        
        return isinstance(node, Folder) and not fsm.is_recycled(node) and node != fsm.recycle
    
    def can_create_object(self, nodes):
        return self.can_create(nodes)
        
    def do_create_object(self, parent, clazz):
        try:
            obj = self.project.create_object(parent, clazz)            
        except Exception, e:
            log.alert(e, 'Create object failed.')            
            return
        
        fs_node = self.project.fs_manager.get_node_by_uuid(obj.uuid)
        self._show_node_in_list(fs_node)
        
    def _show_node_in_list(self, fs_node):        
        l = self.explorer.list
        
        if l.fs_parent != fs_node.parent:
            # l.set_parent(fs_node.parent)
            self.explorer.set_path(fs_node.parent)
        
        l.SetFocus()
        index = l.get_index_by_node(fs_node)
        l.single_select(index)
        return index

    # noinspection PyMethodMayBeStatic
    def create_clipboard_data(self, uuids, action):
        """
        Args:
            action: 'copy' or 'cut'
        """
        data = {'uuids': uuids, 'action': action}
        data = json.dumps(data)
        
        # save to system clipboard        
        do = wx.CustomDataObject(CLIPBOARD_DATA_FORMAT)
        do.SetData(data)
        return do
    
    def _set_clipboard(self, uuids, action):        
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.create_clipboard_data(uuids, action))
            wx.TheClipboard.Close()
            return True
        
        return False

    # noinspection PyMethodMayBeStatic
    def parse_clipboard_data(self, data):
        data = data.GetData()
        data = json.loads(data)
        return data.get('uuids'), data.get('action')
            
    def _get_clipboard(self):
        # read system clip board      
        success = False
        do = wx.CustomDataObject(CLIPBOARD_DATA_FORMAT)
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            
        if not success:
            return None, None
        
        # get data
        return self.parse_clipboard_data(do)        
        
    def can_rename(self, fs_node):
        if not self.is_container(fs_node):
            return False
        if self.project.fs_manager.is_recycled(fs_node):
            return False
        return True

    def rename(self, fs_node, new_name):
        """Rename a fs_node to new_name
        
        Returns:
            True if sucessed, or False if failed
        """
        if self.can_rename(fs_node):
            try:
                self.project.fs_manager.rename(fs_node.uuid, new_name)
            except Exception, e:
                log.alert(e, 'Rename folder failed.')
                return False  
                            
        return True

    # noinspection PyMethodMayBeStatic
    def _bind_menu(self, menu, call_back, id_, *args):
        def func(evt):
            _ = evt
            call_back(*args)
        menu.Bind(wx.EVT_MENU, func, id=id_)
            
    def get_menu(self, nodes):
        menu = wx.Menu()    
        # fsm = self.project.fs_manager
               
        if self.can_restore(nodes):
            item = menu.Append(wx.NewId(), u'&Restore')
            self._bind_menu(menu, self.do_restore, item.GetId(), nodes)
            return menu
        
        if self._add_menu_search(menu, nodes):
            menu.AppendSeparator()
                
        # batch edit
        if self._add_menu_open(menu, nodes):
            menu.AppendSeparator()
        
        # copy/cut/paste/delete
        if self._add_menu_edits(menu, nodes):
            menu.AppendSeparator()

        # show references/referents
        if self._add_menu_ref(menu, nodes):
            menu.AppendSeparator()

        # tags
        if self._add_menu_tags(menu, nodes):
            menu.AppendSeparator()
        
        if self.can_create(nodes):
            # submenu "create"
            submenu = wx.Menu()
            self.add_create_menu(submenu, nodes, menu)
            menu.AppendSubMenu(submenu, "&New")
                                                                    
        return menu
    
    def add_create_menu(self, menu, nodes, event_menu):
        """todo: the name "menu" and "event_menu" should be more clarified"""
        item = menu.Append(wx.NewId(), u'&Folder')
        self._bind_menu(event_menu, self._on_create_folder, item.GetId(), nodes)

        item = menu.Append(wx.NewId(), u'&Filter')
        self._bind_menu(event_menu, self._on_create_filter, item.GetId(), nodes)
        
        if self.is_project_editable():  # Can not create object if project not editable
            menu.AppendSeparator()
            # Clazzes
            clazzes = self.project.type_manager.get_clazzes()
            clazzes.sort(key=lambda x: x.name)
            for clazz in clazzes:
                item = menu.Append(wx.NewId(), clazz.name)
                self._bind_menu(event_menu, self._on_create_object, item.GetId(), nodes, clazz)
    
    def _add_menu_edits(self, menu, nodes):
        n = 0
        if self.can_copy(nodes):
            item = menu.Append(wx.NewId(), u'&Copy')
            self._bind_menu(menu, self.do_copy, item.GetId(), nodes)
            n += 1
        
        if self.can_cut(nodes):
            item = menu.Append(wx.NewId(), u'&Cut')
            self._bind_menu(menu, self.do_cut, item.GetId(), nodes)
            n += 1
        
        if self.can_paste(nodes):
            item = menu.Append(wx.NewId(), u'&Paste')
            self._bind_menu(menu, self.do_paste, item.GetId(), nodes)
            n += 1

        if self.can_delete(nodes):
            item = menu.Append(wx.NewId(), u'&Delete')
            self._bind_menu(menu, self.do_delete, item.GetId(), nodes)
            n += 1
            
        if self.can_undo(nodes):
            item = menu.Append(wx.NewId(), u'&Undo')
            self._bind_menu(menu, self.do_undo, item.GetId(), nodes)
            n += 1
        if self.can_redo(nodes):
            item = menu.Append(wx.NewId(), u'&Redo')
            self._bind_menu(menu, self.do_redo, item.GetId(), nodes)
            n += 1
            
        return n

    def _add_menu_ref(self, menu, nodes):
        """
        Try to add menu: references and referents
        :type menu: wx.Menu
        :type nodes: list[FsNode]
        :return: number of menu items added
        :rtype: int
        """
        # all nodes must be objects
        if not all(map(fs_util.is_object, nodes)):
            return 0

        item = menu.Append(wx.NewId(), u'References(I referenced...)')
        self._bind_menu(menu, self.show_references, item.GetId(), nodes)

        item = menu.Append(wx.NewId(), u'Referents(I am referenced by...)')
        self._bind_menu(menu, self.show_referents, item.GetId(), nodes)
        return 2
    
    def _add_menu_tags(self, menu, nodes):
        # Get nodes which are objects
        obj_nodes = filter(fs_util.is_object, nodes)
        
        if not obj_nodes:
            return False
        
        tags = list(self.project.tags)
        tagged = sum([list(node.tags) for node in obj_nodes], [])
        
        # If every obj has a tag, do not need to add it
        counts = collections.Counter(tagged)
        for tag, count in counts.iteritems():
            if count >= len(obj_nodes):
                tags.remove(tag)
                
        # add tags
        if tags:
            submenu = wx.Menu()
            for tag in tags:            
                item = submenu.Append(wx.NewId(), tag)
                self._bind_menu(menu, self.do_add_tag, item.GetId(), obj_nodes, tag)
            menu.AppendSubMenu(submenu, u"&Add tag")
        
        # remove tags
        tagged = counts.keys()
        if tagged:
            submenu = wx.Menu()
            for tag in tagged:            
                item = submenu.Append(wx.NewId(), tag)            
                self._bind_menu(menu, self.do_remove_tag, item.GetId(), obj_nodes, tag)
            menu.AppendSubMenu(submenu, u"&Remove tag")            
        return bool(tags or tagged)
        
    def _add_menu_search(self, menu, nodes):
        u"""Returns True if any menu added, otherwise returns False"""
        
        if self.can_search(nodes):            
            item = menu.Append(wx.NewId(), u'&Search')        
            self._bind_menu(menu, self.do_search, item.GetId(), nodes[0])        
            return True
    
    def _add_menu_open(self, menu, nodes):
        u"""Returns True if any menu added, False if no menu added"""
        
        if not self.can_open(nodes):
            return False
        
        # Get nodes which are objects
        obj_nodes = filter(fs_util.is_object, nodes)
        
        if not obj_nodes and len(nodes) == 1:
            if self.is_container(nodes[0]):  # all nodes in this filter or folder
                obj_nodes = filter(fs_util.is_object, self.project.fs_manager.walk(nodes[0], False))
        
        menus = 0
        if obj_nodes:
            # Get Objects
            objects = map(self.project.get_object_by_fsfile, obj_nodes)            
            
            # Clazz or each object
            clazzes = [obj.clazz for obj in objects]
            
            # count of each Clazz.  {Clazz: count}
            counts = collections.Counter(clazzes)
            
            if len(counts) == 1:  # Only 1 clazz
                clazz = clazzes[0]                                    
                
                # Can open single editor
                if len(objects) == 1:
                    label = "&Edit %s" % clazz.name
                    item = menu.Append(wx.NewId(), label)
                    self._bind_menu(menu, self.do_edit, item.GetId(), objects[0])
                
                # Multiple editor is valid even 1 object here
                label = u'&Batch Edit %s(%s)' % (clazz.name, len(objects))
                item = menu.Append(wx.NewId(), label)
                self._bind_menu(menu, self.do_edit, item.GetId(), objects)
            else:  # More than 1 clazz, use a sub menu
                clazz_count = counts.items()
                clazz_count.sort(key=lambda x: x[0].name.lower())
                
                if counts.values().count(1):  # At lease 1 clazz has only 1 object
                    submenu = wx.Menu()
                    for clazz, count in clazz_count:
                        if count == 1:
                            item = submenu.Append(wx.NewId(), u'%s' % clazz.name)
                            objects_ = [obj for obj in objects if obj.clazz == clazz]
                            assert len(objects_) == 1
                            self._bind_menu(menu, self.do_edit, item.GetId(), objects_[0])
                    menu.AppendSubMenu(submenu, u"&Edit")
                
                submenu = wx.Menu()
                for clazz, count in clazz_count:
                    item = submenu.Append(wx.NewId(), u'%s(%s)' % (clazz.name, count))
                    self._bind_menu(menu, self.do_edit, item.GetId(), [obj for obj in objects if obj.clazz == clazz])
                menu.AppendSubMenu(submenu, u"&Batch Edit")
            
            menus = 1
        
        # filter & folder
        if len(nodes) == 1:
            node = nodes[0]
            if self.is_container(node):
                item = menu.Append(wx.NewId(), u'&Open')
                self._bind_menu(menu, self.open, item.GetId(), node)
                menus += 1
                
            if fs_util.is_filter(node):
                item = menu.Append(wx.NewId(), u'&Edit')
                self._bind_menu(menu, self.edit_filter, item.GetId(), node)
                menus += 1                        
        
        return menus > 0
    
    def can_open(self, fs_nodes):
        """
        Args:
            fs_nodes: a FSNode, or a list of FSNodes
        """
        
        # Only 1 node
        # if len(fs_nodes)==1:
        if type(fs_nodes) is not list:
            fs_node = fs_nodes            
            if self.is_container(fs_node):
                return True
            
            return self.is_project_editable()

        if len(fs_nodes) == 0:
            return False
                                
        if not self.is_project_editable():
            return False

        # multiple nodes, can only open if all nodes are objects with the same Clazz
        clazz_name = set()
        for fs_node in fs_nodes:
            if fs_util.is_object(fs_node) and not self.project.fs_manager.is_recycled(fs_node):
                clazz_name.add(fs_util.get_object_clazz_name(fs_node))
            else:
                clazz_name.add(None)
        
        if len(clazz_name) == 1:
            return True                                    
        return False
    
    def open(self, fs_nodes):
        """Open one or more nodes
        
        Args:
            fs_nodes: a FSNode, or a list of FSNodes
        """
        assert self.can_open(fs_nodes)
        
        fsm = self.project.fs_manager
        
        # Only 1 node
        # if len(fs_nodes)==1:
        if type(fs_nodes) is not list:
            fs_node = fs_nodes
            
            # folder or filter
            if self.is_container(fs_node):                
                self.explorer.set_path(fs_node)
                return
            
            # edit the object
            if fs_util.is_object(fs_node):
                # only if it's not recycled
                if not fsm.is_recycled(fs_node):
                    obj = self.project.get_object_by_fsfile(fs_node)
                    self.explorer.show_editor(obj)
                return
                        
            raise Exception('invalid node to open: %s' % fs_node)
        
        # multiple nodes, can only open if all nodes are objects with the same Clazz
        self.explorer.show_editor([self.project.get_object_by_fsfile(fs_node) for fs_node in fs_nodes])
    
    def edit_filter(self, node):
        assert fs_util.is_filter(node)
        
        from filter_editor import FilterEditorDialog
        dlg = FilterEditorDialog(self.explorer)
        dlg.set_value(node.data)
        
        if wx.ID_OK == dlg.ShowModal():
            filter_str = dlg.get_value()            
            try:
                self.project.fs_manager.save_file(node.uuid, filter_str)
            except Exception, e:
                log.alert(e, 'Failed to save filter')
        
        dlg.Destroy()
         
    def is_container(self, node):
        if self.project.fs_manager.is_recycled(node):
            return False
        return isinstance(node, (Folder, SearchResult)) or fs_util.is_filter(node)

    @staticmethod
    def get_chooser_from_filter_str(filter_str):
        # todo: this is not safe!
        choose = None
        exec filter_str
        return choose
    
    def get_children(self, node):
        fsm = self.project.fs_manager

        if isinstance(node, Folder):
            return node.children

        if isinstance(node, SearchResult):
            objects = self.project.object_manager.iter_all_objects(node.sql)
            return [fsm.get_node_by_uuid(obj.uuid) for obj in objects]

        if fs_util.is_filter(node):
            objects = self.project.object_manager.iter_all_objects(node.data)
            return [fsm.get_node_by_uuid(obj.uuid) for obj in objects]

            # # l = {}
            # # g = {time}
            # # noinspection PyBroadException
            # try:
            #     func = self.get_chooser_from_filter_str(filter_str)
            # except:
            #     traceback.print_exc()
            #     log.error('invalid filter str in %s: %s', node.uuid, filter_str)
            #     return []
            #
            # # func = l.get('choose')
            # if func:
            #     objects = self.project.object_manager.iter_all_objects(func)
            #     return [fsm.get_node_by_uuid(obj.uuid) for obj in objects]
            #
            # return []
        
        raise Exception("invalid node to get children: %s" % node)
    
    def is_project_editable(self):
        p = self.project
        return p.is_type_editor or not p.get_editor_project().has_error()
    
    ################################################################
    # Node actions
    ################################################################
    def can_copy(self, nodes):
        if not self.is_project_editable():
            return False
        
        if not nodes:
            return False
        
        for node in nodes:
            if node.immutable:
                return False
            
        return True
    
    def do_copy(self, nodes):
        assert self.can_copy(nodes)
        
        uuids = [node.uuid for node in nodes]
        if not self._set_clipboard(uuids, 'copy'):
            log.alert(u'Failed to copy.')
            
    def can_cut(self, nodes):
        if not self.is_project_editable():
            return False
        
        return self.can_copy(nodes)        
    
    def do_cut(self, nodes):
        assert self.can_cut(nodes)
        
        uuids = [node.uuid for node in nodes]
        if not self._set_clipboard(uuids, 'cut'):        
            log.alert(u"Failed to cut.")
    
    def can_paste(self, nodes):
        if len(nodes) != 1:
            return False
        
        uuids, action = self._get_clipboard()
        if not uuids:
            return False
        
        return self.can_paste_data(nodes[0], action)

    def can_paste_data(self, target, action):
        if not self.is_project_editable():
            return False
              
        fsm = self.project.fs_manager        
        if not isinstance(target, Folder) or fsm.is_recycled(target):
            return False        
        
        if target == fsm.recycle and action != 'cut':
            return False 
        
        return True
    
    def do_paste(self, nodes):
        assert self.can_paste(nodes)
                    
        uuids, action = self._get_clipboard()        
        self.do_paste_data(nodes[0], uuids, action)
    
    def do_paste_data(self, target, uuids, action):
        fsm = self.project.fs_manager
        fs_nodes = [fsm.get_node_by_uuid(uuid) for uuid in uuids]
        
        if target in fs_nodes:
            # log.debug('paste cancelled because target is in source data')
            log.alert('paste failed because target is in source data')
            return
        
        if action == 'copy':
            self._repeat_strategy('copy', fs_nodes, fsm.copy, target)            
        elif action == 'cut':
            # moving to Recycle, is equal to delete
            if target == fsm.recycle:
                self.do_delete(fs_nodes)
                return 
            
            self._repeat_strategy('move', fs_nodes, fsm.move, target)                
        else:
            log.alert('invalid clipboard action: %s', action)

    # noinspection PyMethodMayBeStatic
    def _repeat_strategy(self, action_name, nodes, func, *args):
        # todo: remember user's decision with a checkbox "apply to all"
        for node in nodes:
            try:
                try:
                    func(node, *args)
                except FolderConflictionException:
                    ret = wx.MessageBox(u"Folder with the same name already exists! Do you want to merge them?",
                                        style=wx.YES_NO | wx.ICON_WARNING)
                    if ret == wx.YES:
                        func(node, *args, strategy=FOLDER_CONFLICTION_STRATEGY_MERGE)
            except Exception, e:
                log.alert(e, 'Failed to %s: %s', action_name, node)
    
    def begin_drag(self, nodes, window):
        if not (self.can_copy(nodes) or self.can_cut(nodes)):
            return
        
        uuids = [node.uuid for node in nodes]
        data = self.create_clipboard_data(uuids, '')
                
        drop_src = wx.DropSource(window)
        drop_src.SetData(data)        
        result = drop_src.DoDragDrop(wx.Drag_AllowMove)

        if result == wx.DragMove:
            pass    
    
    def can_delete(self, nodes):
        if not self.is_project_editable():
            return False
        
        if not nodes:
            return False
        
        for node in nodes:
            if node.immutable:
                return False
        
        return True
    
    def do_delete(self, nodes):
        assert self.can_delete(nodes)
        
        # is this a destroy action?
        fsm = self.project.fs_manager
        if fsm.is_recycled(nodes[0]):
            if not all([fsm.is_recycled(node) for node in nodes]):
                log.alert('internal error in fs_node_tool._on_delete')
                return
            
            ret = wx.MessageBox("Permanetly delete %s?" % self.get_readable_node_names(nodes),
                                style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            # print ret, wx.YES, wx.NO, wx.ID_YES, wx.ID_NO
            if ret == wx.NO:
                return
            
            delete = fsm.destroy
        else:
            ret = wx.MessageBox("Move %s to recycle bin?" % self.get_readable_node_names(nodes),
                                caption='Warning',
                                style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if ret == wx.NO:
                return

            # if the objects to be deleted are referenced by other objects, give a warning
            if not self.check_reference_before_delete(nodes):
                ret = wx.MessageBox("Some of the nodes are referenced, are you sure to delete?",
                                    caption='Warning',
                                    style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if ret == wx.NO:
                    return

            delete = fsm.delete
                
        for node in nodes:
            try:
                delete(node.uuid)
            except Exception, e:
                log.alert(e, 'Failed to delete: %s', node)

    def check_reference_before_delete(self, nodes):
        """
        Checks if any of the objects, which reside in nodes, is referenced by any node that does not reside in nodes.

        :type nodes: list[FSNode]
        :return: True if it's safe to delete
        :rtype: bool
        """
        objects = self.get_objects_within_nodes(nodes)
        uuids = set([obj.uuid for obj in objects])
        referents = set(sum([list(self.project.ref_manager.get_referents(obj.uuid)) for obj in objects], []))
        if referents.difference(uuids):
            return False
        return True

    def get_objects_within_nodes(self, nodes):
        """
        Returns all the objects, which is one of the nodes, or is the descendant of one of the nodes.

        :type nodes: list[FSNode]
        :rtype: list[Object]
        """
        objects = []
        for node in nodes:
            if fs_util.is_object(node):
                objects.append(self._get_object_by_node(node))
            elif isinstance(node, Folder):
                for child in self.project.fs_manager.walk(node, False):
                    if fs_util.is_object(child):
                        objects.append(self._get_object_by_node(child))
        return objects

    def get_readable_node_names(self, nodes):        
        names = ', '.join('"%s"' % self.get_name(node) for node in nodes[:3])
        if len(nodes) > 3:
            names += '...(%s files)' % len(nodes)
        return names

    # noinspection PyMethodMayBeStatic
    def can_undo(self, nodes):
        _ = nodes
        return False
    
    def do_undo(self, nodes):
        pass

    # noinspection PyMethodMayBeStatic
    def can_redo(self, nodes):
        _ = nodes
        return False
    
    def do_redo(self, nodes):
        pass
    
    def can_restore(self, nodes):
        if not self.is_project_editable():
            return False
                
        if not nodes:
            return False
        
        for node in nodes:
            if not self.project.fs_manager.is_recycled(node):
                return False
        
        return True
                    
    def do_restore(self, nodes):
        assert self.can_restore(nodes)        
        self._repeat_strategy('restore', nodes, self.project.fs_manager.undelete)
        
    def can_search(self, nodes):
        return len(nodes) == 1 and self.is_container(nodes[0])
    
    def do_search(self, node):        
        def iter_maker():
            for node_ in self.project.fs_manager.walk(node, False):
                if fs_util.is_object(node_):
                    yield self.project.get_object_by_fsfile(node_)            
        
        # self.project.object_manager.filter_objects(iter)
        def on_selected(obj):
            print 'search result:', obj, id, obj.name
            # self.explorer.show_editor(obj)
            node_ = self.project.fs_manager.get_node_by_uuid(obj.uuid)
            self.explorer.set_path(node_)            
        
        from structerui.editor.grid.cell_editor.dialog import RefDialog
        dlg = RefDialog(None, self.project, iter_maker, on_selected)
        dlg.Show()       

    def do_edit(self, objects):
        self.project.explorer.show_editor(objects)
    
    def do_add_tag(self, nodes, tag):
        for node in nodes:
            node.tags.add(tag)
            try:
                self.project.fs_manager.save_file(node.uuid)
            except Exception, e:
                log.alert(e, 'Failed to add tag "%s" to: %s', tag, node)

    def do_remove_tag(self, nodes, tag):
        for node in nodes:
            node.tags.discard(tag)
            try:
                self.project.fs_manager.save_file(node.uuid)
            except Exception, e:
                log.alert(e, 'Failed to remove tag "%s" from: %s', tag, node)

    def show_references(self, nodes):
        sql = ' or '.join(["refby('%s')" % node.uuid for node in nodes])
        msg = 'Referenced by "%s"' % self.get_name_of_object_nodes(nodes)
        node = SearchResult(self.project, sql, None, msg)
        self.explorer.set_path(node)

    def show_referents(self, nodes):
        sql = ' or '.join(["ref('%s')" % node.uuid for node in nodes])
        msg = 'References to "%s"' % self.get_name_of_object_nodes(nodes)
        node = SearchResult(self.project, sql, None, msg)
        self.explorer.set_path(node)

    def get_name_of_object_nodes(self, nodes):
        if not nodes:
            return ''

        obj = self._get_object_by_node(nodes[0])
        if len(nodes) == 1:
            return obj.name

        return '%s...' % obj.name

    def get_node_path(self, node):
        names = []
        while node:
            names.append(self.get_name(node))
            node = node.parent

        path = '/'.join(reversed(names))
        return path or '/'