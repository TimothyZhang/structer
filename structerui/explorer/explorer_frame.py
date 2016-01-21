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

import wx
import wx.lib.agw.aui as aui 
import wx.lib.scrolledpanel as scrolled

from structerui import log, hotkey
from structerui.util import get_bitmap, get_icon, get_clazz_bitmap, get_app_data_path 
from structerui.util import ICON_FOLDER, ICON_FILTER, FRAME_ICON_SIZE

from frame_xrc import xrcExplorerFrame
from list_toolbar_xrc import xrcListToolbar
from explorer_tree import ExplorerTree
from explorer_list import ExplorerList

       
class ExplorerFrame(xrcExplorerFrame):
    """A frame to explorer all objects of a project, both data project and type project.

    At most 2 instances of ExplorerFrame might exists, while only one is enabled  at the same time.  
    """
    
    def __init__(self, parent, project = None):   
        self._project = None            
        # [EditorFrame, ...]
        self._editor_frames = []   
        
        # {EditorFrame: wxid}  
        self._editor_to_menuid = {}
        
        # [fs_nodes, ...]
        self._path_history_pos = 0      
        self._path_history = []    
        
        # tool ids
        self._create_obj_tool_ids = [] 
             
        super(ExplorerFrame, self).__init__(parent)

        # icon
        icon = wx.EmptyIcon()
        icon_name = 'icons/setting.png' if (project and project.is_type_editor) else 'icons/table.png'
        icon.CopyFromBitmap( get_bitmap(icon_name,(64,64), project) )
        self.SetIcon( icon )
        
        # Replace tool icons
        tbsize = self.tool_bar.GetToolBitmapSize()
        size = (tbsize.width, tbsize.height)
        self.tool_bar.SetToolNormalBitmap(self.tool_open.GetId(), get_bitmap('icons/open.png', size, project))
        self.tool_bar.SetToolNormalBitmap(self.tool_setting.GetId(), get_bitmap('icons/setting.png', size, project))
        self.tool_bar.SetToolNormalBitmap(self.tool_repair.GetId(), get_bitmap('icons/repair.png', size, project))
        self.tool_bar.SetToolNormalBitmap(self.tool_export.GetId(), get_bitmap('icons/export.png', size, project))
        
        self.tool_bar.SetToolNormalBitmap(self.tool_create_folder.GetId(), get_bitmap(ICON_FOLDER, size, project))
        self.tool_bar.SetToolNormalBitmap(self.tool_create_filter.GetId(), get_bitmap(ICON_FILTER, size, project))
                
        # XRCed can't assign variable for wxMenu correctly        
        self.menu_windows = self.menu_close_all.GetMenu()
        self.menu_new = self.menu_new_dummy.GetMenu()
        self.menu_new.Remove(self.menu_new.FindItemByPosition(0).GetId())
        
        self.menu_plugins = self.menu_plugin_dummy.GetMenu()
        self.menu_plugins.Remove(self.menu_plugins.FindItemByPosition(0).GetId())
        
        self.SetMinSize((640, 480))        
        self._create_tree()
        self._create_list()
        #self._create_status_view()
        #self._create_log_view()
        self._layout()
        
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
          
        if project:
            self.update_project(project)

    # def ProcessEvent(self, event):
    #     a = xrcExplorerFrame.ProcessEvent(self, event)
    #     b = event.GetSkipped()
    #     print 'ProcessEvent:', event, a, b
    #     return a

    @property
    def list(self):
        return self._list

    def _create_tree(self):
        self._tree_panel = scrolled.ScrolledPanel(self.main_panel, -1,
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="TreePanel" )
        
        self._tree = ExplorerTree(self._tree_panel, self)  
              
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._tree, 1, wx.EXPAND)
        self._tree_panel.SetSizer(sizer)
        
        self._tree_panel.SetAutoLayout(1)
        self._tree_panel.SetupScrolling()
        self._tree_panel.SetInitialSize()        
    
    def _create_list(self):        
        self._list_panel = scrolled.ScrolledPanel(self.main_panel, -1,                                                   
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="ListPanel" )
        
        self._list = ExplorerList(self._list_panel, self)

        tb = xrcListToolbar(self._list_panel)
        tb.list = self._list
        tbsize = tb.GetToolBitmapSize()
        tb.SetToolNormalBitmap(tb.sort_by_type.GetId(), get_bitmap('icons/class.png', tbsize, self.project))
        tb.SetToolNormalBitmap(tb.sort_by_time.GetId(), get_bitmap('icons/time.png', tbsize, self.project))
        tb.SetToolNormalBitmap(tb.sort_by_name.GetId(), get_bitmap('icons/name.png', tbsize, self.project))
        tb.SetToolNormalBitmap(tb.list_icon.GetId(), get_bitmap('icons/icon_view.png', tbsize, self.project))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND)
        sizer.Add(self._list, 1, wx.EXPAND)
        self._list_panel.SetSizer(sizer)
        
        self._list_panel.SetAutoLayout(1)
        self._list_panel.SetupScrolling()
        self._list_panel.SetInitialSize()
        
    def _create_status_view(self):
        pass
    
    def _create_log_view(self):
        self._log = wx.TextCtrl(self.main_panel, -1,
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)        
        wx.Log_SetActiveTarget(wx.LogTextCtrl(self._log))        
        pass
    
    def _layout(self):
        self._aui_manager = aui.AuiManager()
        self._aui_manager.SetManagedWindow(self.main_panel)
                
        # Use the aui manager to set up everything
        ALLOW_AUI_FLOATING = False
        
#         self.SetToolBar(None)        
#         self._aui_manager.AddPane(self.tool_bar, aui.AuiPaneInfo().
#                       Name("Toolbar").Caption("Toolbar").
#                       ToolbarPane().Top().Floatable(ALLOW_AUI_FLOATING).
#                       LeftDockable(False).RightDockable(False))        

        self._aui_manager.AddPane(self._tree_panel,
                         aui.AuiPaneInfo().
                         Left().Layer(2).BestSize((240, -1)).
                         MinSize((160, -1)).
                         Floatable(ALLOW_AUI_FLOATING).FloatingSize((240, 700)).
                         Caption(u"Object Explorer").
                         CloseButton(False).
                         Name("ResourceTree"))
        self._aui_manager.AddPane(self._list_panel, aui.AuiPaneInfo().CenterPane().Name("FileList"))
#         self._aui_manager.AddPane(self._log,
#                          aui.AuiPaneInfo().
#                          Bottom().BestSize((-1, 60)).
#                          MinSize((-1, 60)).Name("Log").Caption("Log") )
        #self._aui_cfgs[DEFAULT_PERSPECTIVE] = self._aui_manager.SavePerspective()
        self._aui_manager.Update()
        #self._aui_manager.SetFlags(self._aui_manager.GetFlags() ^ aui.AUI_MGR_TRANSPARENT_DRAG)
        pass
    
    def _on_char_hook(self, evt):
        keystr = hotkey.build_keystr(evt)
        
        if hotkey.check(hotkey.EXPLORER_UP_LEVEL, keystr):
            fs_node = self._list.fs_parent
            if fs_node.parent:                
                self.set_path(fs_node.parent)
                self._list.single_select_node(fs_node)
                return
        
        if hotkey.check(hotkey.EXPLORER_HISTORY_PREV, keystr):
            print 'prev'
            if self.list.history_prev():
                return

        if hotkey.check(hotkey.EXPLORER_HISTORY_NEXT, keystr):
            print 'next'
            if self.list.history_next():
                return

        evt.Skip()

    @property
    def project(self):
        return self._project
    
    @property
    def list(self):
        return self._list
    
    @property
    def tree(self):
        return self._tree
    
    @property
    def is_type_editor(self):
        return bool( self._project and self._project.is_type_editor )
    
    def update_project(self, project): 
        # Less elegant but more convenience than ExplorerFrame.get_frame(project)        
        project.explorer = self
        
        self._project = project
        self.SetTitle("%s - [%s]" % (project.name, project.path))
                    
        if not project.is_type_editor and project.get_editor_project().has_error():
            wx.MessageBox("Invalid types, please fix!")
            self.set_status_msg('Can not edit because types are invalid. Open Settings to fix!')            
        
        self._tree.update_project()
        self._list.update_project()
        
        # Create buttons for Creating clazzes
        for tid in self._create_obj_tool_ids:
            self.tool_bar.DeleteTool(tid)
            
        tbsize = self.tool_bar.GetToolBitmapSize()
        size = (tbsize.width, tbsize.height)
        clazzes = project.type_manager.get_clazzes()
        clazzes.sort(key=lambda x: x.name)
        for clazz in clazzes:
            tool = self.tool_bar.AddTool(wx.NewId(), get_clazz_bitmap(clazz, size, project), shortHelpString=clazz.name)
            self._bind_tool_create(clazz, tool.GetId())
            self._create_obj_tool_ids.append( tool.GetId() )
        self.tool_bar.Realize()            
                
        self.set_path(project.fs_manager.root)
        
        # Update frame icon
        icon = get_icon('table.png', FRAME_ICON_SIZE, project)
        if icon:
            self.SetIcon( icon )
            
        self.init_plugins()
    
    def init_plugins(self):
        # Remove current plugins
        while 1:
            try:
                item = self.menu_plugins.FindItemByPosition(0)                
                self.menu_plugins.Remove(item.GetId())
            except:
                break
            
        from structerui.plugin_manager import PluginManager
        pm = PluginManager()      
        pm.load_plugins()      
        
        # add all        
        for plugin in pm.iter_plugins():            
            mi = wx.MenuItem(self.menu_plugins, wx.NewId(), plugin.label)
            def get_callback(plugin_):
                def callback(evt):
                    plugin_.execute(self.project)
                return callback
            self.menu_plugins.Bind(wx.EVT_MENU, get_callback(plugin), mi)
            self.menu_plugins.AppendItem( mi )
        

    def update_menu_new(self):
        while self.menu_new.GetMenuItemCount():
            self.menu_new.Remove(self.menu_new.FindItemByPosition(0).GetId())

        self._list.node_tool.add_create_menu(self.menu_new, [self._list.fs_parent], self.menu_new)

    def _bind_tool_create(self, clazz, id_):    
        def func(evt):
            self._list.node_tool.do_create_object(self._list.fs_parent, clazz)
        self.tool_bar.Bind(wx.EVT_TOOL, func, id = id_)
        self.tool_bar.Bind(wx.EVT_UPDATE_UI, self._on_updateui_evt_create, id = id_)
    
    def _on_updateui_evt_create(self, evt):        
        #self.on_update_ui(evt, "create")            
        evt.Enable(bool(self.project and self._list.fs_parent and self._list.node_tool.can_create_object([self._list.fs_parent])))
    
    def set_status_msg(self, msg):
        self.status_bar.SetStatusText(msg)
    
    def set_path(self, fs_node):
        '''Set current path to show
        
        Args:
            fs_node: Folder, or a filter
        '''
        if self.list.node_tool.is_container(fs_node):
            fs_folder = fs_node
            fs_file = None
        else:
            fs_folder = fs_node.parent
            fs_file = fs_node
        
        self._tree.set_path(fs_folder)
        self._list.set_parent(fs_folder)
        
        if file:
            self._list.single_select_node(fs_file)
            self._list.SetFocus()
    
    def show_editor(self, objects):
        '''create and show a new editor
        
        Args:
            objects: an Object, or a list of Objects.
                If it's an object, a Struct editor will be used
                If it's a list of object, even with only 1 object, a StructList editor will be used 
        '''
        org = objects
        if type(objects) is not list:
            objects = [org]
            
        # order by id, by default
        if objects and objects[0].struct.has_attr('id'):
            objects.sort(key=lambda x:x.id)

        while 1:
            # Is there any editor frames already editing (some of) objects
            editors = self._find_editors(objects, True)            
            read_only = False  
            
            # some of the objects are alread open
            if editors:
                # if only 1 objects is requested, just show that editor
                if len(objects)==1:
                    editors[0].Raise()
                    return
                
                # prompt use to choose: close, read only or cancel
                import wx.lib.agw.genericmessagedialog as GMD
                dlg = GMD.GenericMessageDialog(self, "%s objects(s) are already opened, you may close those editors, or open as read only mode."%len(editors),
                                           "Oh~",
                                           wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
                dlg.SetYesNoCancelLabels('Close', '&Read Only', '&Cancel')            
                ret = dlg.ShowModal()            
                if ret == wx.ID_YES:
                    for editor in editors:
                        editor.close()
                    continue
                elif ret == wx.ID_NO:
                    read_only = True
                else:
                    return          
            break      
            
        from structerui.editor.context import FrameEditorContext
        from structerui.editor.frame import EditorFrame
        
        ctx = FrameEditorContext(self.project, org, read_only)
        f = EditorFrame(self, ctx)        
        
        self.add_editor( f )
        
            
        f.Show()
        f.Raise()
        
    def _find_editors(self, objects, editable_only):
        '''
        Args:
            objects: list of Objects
            editable_only: Bool. only return editors which are editable
            
        Returns:
            list of EditorFrames
        '''
        
        # Is there any editor frames already editing (some of) objects
        editors = []
        for obj in objects:
            editor = self._get_editor_by_object(obj)
            if editor and (not editable_only or not editor.editor_context.read_only):
                editors.append(editor)
        
        return editors
    
    def add_editor(self, editor):
        self._editor_frames.append( editor )
        
        def on_menu(evt):
            editor.Raise()
        
        self._editor_to_menuid[editor] = id_ = wx.NewId()                    
        mi = wx.MenuItem(self.menu_windows, id_, editor.GetTitle())        
        self.menu_windows.Bind(wx.EVT_MENU, on_menu, mi)
        self.menu_windows.AppendItem( mi )
        
    def remove_editor(self, editor):
        self._editor_frames.remove(editor)        
        
        id_ = self._editor_to_menuid.pop(editor)
        self.menu_windows.Delete(id_)        
        
    def _get_editor_by_object(self, object):
        '''Gets the EditorFrame which is editor object, if it exists
        
        Args:
            object: instance of Object
        '''
        
        for ef in self._editor_frames:
            if ef.editor_context.contains_object(object) and not ef.editor_context.read_only:
                return ef
    
    def _open(self):        
        ''' open or create a project '''
        # read recent projects
        app_data_path = get_app_data_path()
        recent_file = os.path.join(app_data_path, 'recent_projects')
        try:
            recent_projects = open(recent_file).read().split('\n')
        except:
            recent_projects = []
                
        SAMPLE_DIR = 'samples'
        sample_projects = [os.path.join(SAMPLE_DIR, f) for f in os.listdir(SAMPLE_DIR)]

        # prompt 
        from project_dialog_xrc import xrcProjectDialog
        dlg = xrcProjectDialog(self)
        dlg.set_recent_paths(recent_projects + sample_projects)
        if wx.ID_OK == dlg.ShowModal():            
            path = dlg.get_path()    
            
            # prompt and create if not exists
            if not os.path.exists(path):
                dlg = wx.MessageDialog(self, 'Folder not exists, create now?',
                               'Warning',                               
                               wx.YES_NO | wx.ICON_QUESTION)
                                
                if dlg.ShowModal() == wx.ID_NO:
                    return
                
                try:
                    os.makedirs(path)
                except Exception, e:
                    log.error(e, "create project folder failed")
                    wx.MessageBox("Failed to create folder: %s" % path)
                    return
                                                   
            self._load_project(path)
#             try:
#                 project = Project(path, False)
#                 project.load()
#                 self.update_project(project)
#             except Exception, e:        
#                 log.error(e, "Failed to open/create project")
#                 wx.MessageBox("Failed to open/create project: %s" % e)
#             else:
            
            # save recent files
            try:   
                recent_projects.remove(path)
            except: pass            
            recent_projects.insert(0, path)
            open(recent_file, 'w').write('\n'.join(recent_projects))
                
        dlg.Destroy()
        
    def _setting(self): 
        ''' open a new ExplorerFrame to edit types and settings '''       
        if not self.close_all_editors():
            return
                
        self.Disable()
        
        p = self.project.get_editor_project()
        frame = ExplorerFrame(self, p)        
        frame.SetTitle( "%s - Setting" % self.GetTitle())
        #frame.SetModal(True)
        frame.Show() 
    
    def _can_export(self):
        return bool(self.project and not self.project.is_type_editor)
        
    def _export(self):
        if self.project.has_error(True):
            log.alert("All errors must be fixed before exporting.")
            return
        
        from structer.exporter import DefaultExporter
        exp = DefaultExporter()
        
        wildcard = exp.get_exported_wildcard()
        if wildcard is None:
            # need a folder
            raise NotImplemented
        
            #path = ...
        else:
            dlg = wx.FileDialog(self, message="Choose export location",                               
                                #defaultDir=self.project.path, 
                                #defaultFile="",
                                wildcard=wildcard ,
                                style=wx.SAVE|wx.FD_OVERWRITE_PROMPT
                               )
            if wx.ID_CANCEL == dlg.ShowModal():
                dlg.Destroy()
                return False
                            
            path = dlg.GetPath()
            dlg.Destroy()
            
        try:
            from zipfile import ZipFile
            zf = ZipFile(path, 'w')
            exp.export(self.project, zf.writestr)
        except Exception, e:
            log.alert(e, "Failed to export")
            return False
        finally:
            if zf:
                zf.close()
        
        wx.MessageBox("export success!")
        return True
    
    def reload_project(self):
        ''' completely reload project '''
        if not self.close_all_editors():
            return
        
        self._load_project(self.project.path)
        
    def _load_project(self, path):
        from structer.project import Project
        project = Project(path, False)
        
        project.load()
        self.update_project(project)
        
    def close_all_editors(self):
        frames = self._editor_frames[:]
        for ef in frames:            
            ef.close()
            
        if self._editor_frames:
            wx.MessageBox("Some editors not closed!")
            return False
    
        return True
    
    def get_focused_ctrl(self):
        if self._tree.HasFocus():
            return self._tree
        if self._list.HasFocus():
            return self._list
    
    def get_node_tool(self):
        ctrl = self.get_focused_ctrl()
        if ctrl:
            return ctrl.node_tool
    
    def on_menu(self, evt, action_name):
        nt = self.get_node_tool()
        ctrl = self.get_focused_ctrl()
        
        if ctrl and nt:
            try:
                mth = getattr(nt, 'do_%s' % action_name)                    
                mth( ctrl.get_selected_nodes() )            
            except Exception, e:
                log.alert(e, 'Failed to %s', action_name)
    
    def on_update_ui(self, evt, action_name):
        enable = False
        
        nt = self.get_node_tool()
        ctrl = self.get_focused_ctrl()
        
        if ctrl and nt:
            try:
                mth = getattr(nt, 'can_%s' % action_name)                    
                enable = mth( ctrl.get_selected_nodes() )
            except AttributeError:
                pass
            except Exception, e:
                #todo: if need print, print only time
                pass
        evt.Enable( enable )
        
    def _repair(self):
        # Replace with event handler code
        if not self.close_all_editors():
            return
        
        from repair_dialog_xrc import xrcRepairDialog, get_resources
        import wx.py
        dlg = xrcRepairDialog(self)        
        shell = wx.py.shell.Shell(dlg.repair_panel, -1, introText='Try to start with\n>>> project.object_manager.iter_all_objects()\n')
        get_resources().AttachUnknownControl("shell_ctrl", shell)
        shell.interp.locals['project'] = self.project
        
        dlg.ShowModal()
        dlg.Destroy()
    
    def _search(self):
        nodes = self.tree.get_selected_nodes()
        if nodes:
            self.tree.node_tool.do_search(nodes[0])        
