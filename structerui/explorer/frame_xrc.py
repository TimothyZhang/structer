# This file was automatically generated by pywxrc.
# -*- coding: UTF-8 -*-

import wx
import wx.xrc as xrc

__res = None

def get_resources():
    """ This function provides access to the XML resources in this module."""
    global __res
    if __res == None:
        __init_resources()
    return __res




class xrcExplorerFrame(wx.Frame):
#!XRCED:begin-block:xrcExplorerFrame.PreCreate
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
#!XRCED:end-block:xrcExplorerFrame.PreCreate

    def __init__(self, parent):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreFrame()
        self.PreCreate(pre)
        get_resources().LoadOnFrame(pre, parent, "ExplorerFrame")
        self.PostCreate(pre)

        # Define variables for the controls, bind event handlers
        self.menu_new_dummy = self.GetMenuBar().FindItemById(xrc.XRCID("menu_new_dummy"))
        self.menu_search = self.GetMenuBar().FindItemById(xrc.XRCID("menu_search"))
        self.menu_plugin_dummy = self.GetMenuBar().FindItemById(xrc.XRCID("menu_plugin_dummy"))
        self.menu_close_all = self.GetMenuBar().FindItemById(xrc.XRCID("menu_close_all"))
        self.tool_bar = xrc.XRCCTRL(self, "tool_bar")
        self.tool_open = self.GetToolBar().FindById(xrc.XRCID("tool_open"))
        self.tool_setting = self.GetToolBar().FindById(xrc.XRCID("tool_setting"))
        self.tool_export = self.GetToolBar().FindById(xrc.XRCID("tool_export"))
        self.tool_up = self.GetToolBar().FindById(xrc.XRCID("tool_up"))
        self.tool_back = self.GetToolBar().FindById(xrc.XRCID("tool_back"))
        self.tool_forward = self.GetToolBar().FindById(xrc.XRCID("tool_forward"))
        self.address_box = xrc.XRCCTRL(self, "address_box")
        self.status_bar = xrc.XRCCTRL(self, "status_bar")
        self.main_panel = xrc.XRCCTRL(self, "main_panel")

        self.Bind(wx.EVT_MENU, self.OnMenu_menu_open, id=xrc.XRCID('menu_open'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_open, id=xrc.XRCID('menu_open'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_setting, id=xrc.XRCID('menu_setting'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_setting, id=xrc.XRCID('menu_setting'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_repair, id=xrc.XRCID('menu_repair'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_repair, id=xrc.XRCID('menu_repair'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_export, id=xrc.XRCID('menu_export'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_export, id=xrc.XRCID('menu_export'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_exit, id=xrc.XRCID('menu_exit'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_undo, id=xrc.XRCID('menu_undo'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_undo, id=xrc.XRCID('menu_undo'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_redo, id=xrc.XRCID('menu_redo'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_redo, id=xrc.XRCID('menu_redo'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_copy, id=xrc.XRCID('menu_copy'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_copy, id=xrc.XRCID('menu_copy'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_cut, id=xrc.XRCID('menu_cut'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_cut, id=xrc.XRCID('menu_cut'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_paste, id=xrc.XRCID('menu_paste'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_paste, id=xrc.XRCID('menu_paste'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_delete, id=xrc.XRCID('menu_delete'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_delete, id=xrc.XRCID('menu_delete'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_select_all, id=xrc.XRCID('menu_select_all'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_inverse_select, id=xrc.XRCID('menu_inverse_select'))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_new, id=xrc.XRCID('menu_new'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_search, self.menu_search)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_search, self.menu_search)
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_close_all, self.menu_close_all)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_menu_close_all, self.menu_close_all)
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_help_content, id=xrc.XRCID('menu_help_content'))
        self.Bind(wx.EVT_MENU, self.OnMenu_menu_about, id=xrc.XRCID('menu_about'))
        self.Bind(wx.EVT_TOOL, self.OnTool_tool_open, self.tool_open)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_tool_open, self.tool_open)
        self.Bind(wx.EVT_TOOL, self.OnTool_tool_setting, self.tool_setting)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_tool_setting, self.tool_setting)
        self.Bind(wx.EVT_TOOL, self.OnTool_tool_export, self.tool_export)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_tool_export, self.tool_export)
        self.Bind(wx.EVT_TOOL, self.OnTool_tool_up, self.tool_up)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_tool_up, self.tool_up)
        self.Bind(wx.EVT_TOOL, self.OnTool_tool_back, self.tool_back)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_tool_back, self.tool_back)
        self.Bind(wx.EVT_TOOL, self.OnTool_tool_forward, self.tool_forward)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_tool_forward, self.tool_forward)
        self.Bind(wx.EVT_COMBOBOX, self.OnCombobox_address_box, self.address_box)
        self.Bind(wx.EVT_TEXT, self.OnText_address_box, self.address_box)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnText_enter_address_box, self.address_box)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_address_box, self.address_box)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_open
    def OnMenu_menu_open(self, evt):
        try:
            self._open()
        except Exception, e:
            from structerui import log
            log.alert(e, 'Failed to open/create project.')
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_open        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_open
    def OnUpdate_ui_menu_open(self, evt):
        # Replace with event handler code
        evt.Enable( not self.is_type_editor )        
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_open        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_setting
    def OnMenu_menu_setting(self, evt):
        # Replace with event handler code
        self._setting()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_setting        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_setting
    def OnUpdate_ui_menu_setting(self, evt):
        # Replace with event handler code
        evt.Enable( bool(self.project and not self.is_type_editor) )
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_setting        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_repair
    def OnMenu_menu_repair(self, evt):
        # Replace with event handler code
        self._repair()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_repair        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_repair
    def OnUpdate_ui_menu_repair(self, evt):
        # Replace with event handler code
        evt.Enable(bool(self.project))
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_repair        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_export
    def OnMenu_menu_export(self, evt):
        # Replace with event handler code
        self._export()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_export        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_export
    def OnUpdate_ui_menu_export(self, evt):
        # Replace with event handler code
        #self.project.get_type_editor().has_error() and
        evt.Enable( self._can_export() )
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_export        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_exit
    def OnMenu_menu_exit(self, evt):
        # Replace with event handler code        
        self.Close()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_exit        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_undo
    def OnMenu_menu_undo(self, evt):
        # Replace with event handler code
        # self.on_menu(evt, 'undo')
        pass
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_undo        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_undo
    def OnUpdate_ui_menu_undo(self, evt):
        # Replace with event handler code
        # self.on_update_ui(evt, 'undo')
        pass
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_undo        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_redo
    def OnMenu_menu_redo(self, evt):
        # Replace with event handler code
        # print "OnMenu_menu_redo()"
        pass
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_redo        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_redo
    def OnUpdate_ui_menu_redo(self, evt):
        # Replace with event handler code
        # self.on_update_ui(evt, 'redo')
        pass
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_redo        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_copy
    def OnMenu_menu_copy(self, evt):
        # Replace with event handler code
        self.on_menu(evt, 'copy')
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_copy        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_copy
    def OnUpdate_ui_menu_copy(self, evt):
        # Replace with event handler code
        self.on_update_ui(evt, 'copy')
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_copy        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_cut
    def OnMenu_menu_cut(self, evt):
        # Replace with event handler code
        self.on_menu(evt, 'cut')
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_cut        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_cut
    def OnUpdate_ui_menu_cut(self, evt):
        # Replace with event handler code
        self.on_update_ui(evt, 'cut')
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_cut        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_paste
    def OnMenu_menu_paste(self, evt):
        # Replace with event handler code
        # self.on_menu(evt, 'paste')
        self.list.node_tool.do_paste([self.list.fs_parent])
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_paste        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_paste
    def OnUpdate_ui_menu_paste(self, evt):
        # Replace with event handler code
        can_paste = self.list.node_tool.can_paste([self.list.fs_parent])
        # self.on_update_ui(evt, 'paste')
        evt.Enable(can_paste)
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_paste        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_delete
    def OnMenu_menu_delete(self, evt):
        # Replace with event handler code
        self.on_menu(evt, 'delete')
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_delete        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_delete
    def OnUpdate_ui_menu_delete(self, evt):
        # Replace with event handler code
        self.on_update_ui(evt, 'delete')
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_delete        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_select_all
    def OnMenu_menu_select_all(self, evt):
        # Replace with event handler code
        self._list.select_all()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_select_all        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_inverse_select
    def OnMenu_menu_inverse_select(self, evt):
        # Replace with event handler code
        self._list.inverse_select()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_inverse_select        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_new
    def OnUpdate_ui_menu_new(self, evt):
        # Replace with event handler code
        can = bool(self.project and self._list and self._list.node_tool.can_create([self._list.fs_parent]))
        evt.Enable(can)
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_new        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_search
    def OnMenu_menu_search(self, evt):
        # Replace with event handler code
        self._search()        
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_search        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_search
    def OnUpdate_ui_menu_search(self, evt):
        # Replace with event handler code
        evt.Enable(bool(self.project))
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_search        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_close_all
    def OnMenu_menu_close_all(self, evt):
        # Replace with event handler code
        self.close_all_editors()
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_close_all        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_menu_close_all
    def OnUpdate_ui_menu_close_all(self, evt):
        # Replace with event handler code
        evt.Enable( len(self._editor_frames) )
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_menu_close_all        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_help_content
    def OnMenu_menu_help_content(self, evt):
        # Replace with event handler code
        print "OnMenu_menu_help_content()"
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_help_content        

#!XRCED:begin-block:xrcExplorerFrame.OnMenu_menu_about
    def OnMenu_menu_about(self, evt):
        from wx.lib.wordwrap import wordwrap
        
        info = wx.AboutDialogInfo()
        info.Name = "Structer"
        info.Version = "0.1.0"
        info.Copyright = "Copyright 2014 Timothy Zhang(zt@live.cn)."
        info.Description = wordwrap(
            'Structer is a "Structured Data Editor" base on wxPython.\n' +
            'Structer is originally developed for editing game data, while it also can be used for other purposes.',
            450, wx.ClientDC(self))
        
        info.WebSite = ("https://github.com/TimothyZhang/structer", "Github Repository")
        info.Developers = [ "Timothy Zhang(zt@live.cn)",
                            "Yutao Yang(zhatudou@gmail.com)"]
        
        licenseText = 'Structer is distributed under the GPL v3.  See LICENSE'
        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
#!XRCED:end-block:xrcExplorerFrame.OnMenu_menu_about        

#!XRCED:begin-block:xrcExplorerFrame.OnTool_tool_open
    def OnTool_tool_open(self, evt):
        # Replace with event handler code
        self._open()
#!XRCED:end-block:xrcExplorerFrame.OnTool_tool_open        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_tool_open
    def OnUpdate_ui_tool_open(self, evt):
        # Replace with event handler code
        evt.Enable( not self.is_type_editor )
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_tool_open        

#!XRCED:begin-block:xrcExplorerFrame.OnTool_tool_setting
    def OnTool_tool_setting(self, evt):
        # Replace with event handler code
        self._setting()
#!XRCED:end-block:xrcExplorerFrame.OnTool_tool_setting        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_tool_setting
    def OnUpdate_ui_tool_setting(self, evt):
        # Replace with event handler code
        evt.Enable( bool(self.project and not self.is_type_editor) )
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_tool_setting        

#!XRCED:begin-block:xrcExplorerFrame.OnTool_tool_export
    def OnTool_tool_export(self, evt):
        # Replace with event handler code
        self._export()
#!XRCED:end-block:xrcExplorerFrame.OnTool_tool_export        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_tool_export
    def OnUpdate_ui_tool_export(self, evt):
        # Replace with event handler code
        #todo: currently has_error is slow!!
        evt.Enable( self._can_export() )
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_tool_export        

#!XRCED:begin-block:xrcExplorerFrame.OnTool_tool_up
    def OnTool_tool_up(self, evt):
        # Replace with event handler code
        self.go_up()
#!XRCED:end-block:xrcExplorerFrame.OnTool_tool_up        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_tool_up
    def OnUpdate_ui_tool_up(self, evt):
        # Replace with event handler code
        evt.Enable(self.can_go_up())
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_tool_up        

#!XRCED:begin-block:xrcExplorerFrame.OnTool_tool_back
    def OnTool_tool_back(self, evt):
        self.list.history_prev()
#!XRCED:end-block:xrcExplorerFrame.OnTool_tool_back        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_tool_back
    def OnUpdate_ui_tool_back(self, evt):
        evt.Enable(self.can_go_back())
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_tool_back        

#!XRCED:begin-block:xrcExplorerFrame.OnTool_tool_forward
    def OnTool_tool_forward(self, evt):
        self.list.history_next()
#!XRCED:end-block:xrcExplorerFrame.OnTool_tool_forward        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_tool_forward
    def OnUpdate_ui_tool_forward(self, evt):
        evt.Enable(self.can_go_forward())
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_tool_forward        

#!XRCED:begin-block:xrcExplorerFrame.OnCombobox_address_box
    def OnCombobox_address_box(self, evt):
        # Replace with event handler code
        print "OnCombobox_address_box()"
#!XRCED:end-block:xrcExplorerFrame.OnCombobox_address_box        

#!XRCED:begin-block:xrcExplorerFrame.OnText_address_box
    def OnText_address_box(self, evt):
        # Replace with event handler code
        # print "OnText_address_box()"
        pass
#!XRCED:end-block:xrcExplorerFrame.OnText_address_box        

#!XRCED:begin-block:xrcExplorerFrame.OnText_enter_address_box
    def OnText_enter_address_box(self, evt):
        # Replace with event handler code
        print "OnText_enter_address_box()"
#!XRCED:end-block:xrcExplorerFrame.OnText_enter_address_box        

#!XRCED:begin-block:xrcExplorerFrame.OnUpdate_ui_address_box
    def OnUpdate_ui_address_box(self, evt):
        # Replace with event handler code
        # print "OnUpdate_ui_address_box()"
        pass
#!XRCED:end-block:xrcExplorerFrame.OnUpdate_ui_address_box        

#!XRCED:begin-block:xrcExplorerFrame.OnClose
    def OnClose(self, evt):
        if self.project:        
            if not self.close_all_editors():
                # some editors not closed!
                return
        
            if self.project.is_type_editor:
                self.GetParent().Enable()            
                self.GetParent().Raise()
                self.GetParent().reload_project()
        
        #self._aui_manager.Destroy()
        evt.Skip()
#!XRCED:end-block:xrcExplorerFrame.OnClose        




# ------------------------ Resource data ----------------------

def __init_resources():
    global __res
    __res = xrc.EmptyXmlResource()

    wx.FileSystem.AddHandler(wx.MemoryFSHandler())

    frame_xrc = '''\
<?xml version="1.0" ?><resource class="wxMenuItem">
  <object class="wxFrame" name="ExplorerFrame">
    <object class="wxMenuBar" name="menu_object">
      <object class="wxMenu" name="menu_file">
        <object class="wxMenuItem" name="menu_open">
          <label>&amp;Open/Create...\tCtrl+O</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_setting">
          <label>Setting...\tCtrl+P</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_repair">
          <label>&amp;Repair\tF4</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_export">
          <label>&amp;Export\tF8</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="separator"/>
        <object class="wxMenuItem" name="menu_exit">
          <label>E&amp;xit\tCtrl+Q</label>
          <XRCED>
            <events>EVT_MENU</events>
          </XRCED>
        </object>
        <label>&amp;Project</label>
      </object>
      <object class="wxMenu" name="menu_edit">
        <object class="wxMenuItem" name="menu_undo">
          <label>&amp;Undo\tCtrl+Z</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_redo">
          <label>&amp;Redo\tCtrl+Y</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="separator"/>
        <object class="wxMenuItem" name="menu_copy">
          <label>&amp;Copy\tCtrl+C</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_cut">
          <label>Cut\tCtrl+X</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_paste">
          <label>&amp;Paste\tCtrl+V</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_delete">
          <label>Delete\tDelete</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="separator"/>
        <object class="wxMenuItem" name="menu_select_all">
          <label>Select &amp;All\tCtrl+A</label>
          <XRCED>
            <events>EVT_MENU</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_inverse_select">
          <label>&amp;Inverse Select\tCtrl+Shift+I</label>
          <XRCED>
            <events>EVT_MENU</events>
          </XRCED>
        </object>
        <label>&amp;Edit</label>
      </object>
      <object class="wxMenu" name="menu_object">
        <label>&amp;Object</label>
        <object class="wxMenu" name="menu_new">
          <object class="wxMenuItem" name="menu_new_dummy">
            <label>Dummy</label>
            <XRCED>
              <assign_var>1</assign_var>
            </XRCED>
          </object>
          <label>&amp;New\tCtrl+N</label>
          <help>create new object...</help>
          <XRCED>
            <events>EVT_UPDATE_UI</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_search">
          <label>&amp;Search\tCtrl-F</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
            <assign_var>1</assign_var>
          </XRCED>
        </object>
      </object>
      <object class="wxMenu" name="menu_plugins">
        <object class="wxMenuItem" name="menu_plugin_dummy">
          <label>Dummy</label>
          <XRCED>
            <assign_var>1</assign_var>
          </XRCED>
        </object>
        <label>&amp;Plugins</label>
      </object>
      <object class="wxMenu" name="menu_windows">
        <object class="wxMenuItem" name="menu_close_all">
          <label>Close All</label>
          <XRCED>
            <events>EVT_MENU|EVT_UPDATE_UI</events>
            <assign_var>1</assign_var>
          </XRCED>
        </object>
        <object class="separator"/>
        <label>&amp;Windows</label>
      </object>
      <object class="wxMenu" name="menu_help">
        <object class="wxMenuItem" name="menu_help_content">
          <label>Contents...</label>
          <XRCED>
            <events>EVT_MENU</events>
          </XRCED>
        </object>
        <object class="wxMenuItem" name="menu_about">
          <label>About...</label>
          <XRCED>
            <events>EVT_MENU</events>
          </XRCED>
        </object>
        <label>&amp;Help</label>
      </object>
    </object>
    <object class="wxToolBar" name="tool_bar">
      <object class="tool" name="tool_open">
        <bitmap stock_id="wxART_FILE_OPEN"/>
        <tooltip>open project...</tooltip>
        <XRCED>
          <events>EVT_TOOL|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      <object class="tool" name="tool_setting">
        <bitmap stock_id="wxART_HELP_SETTINGS"/>
        <tooltip>open setting project...</tooltip>
        <XRCED>
          <events>EVT_TOOL|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      <object class="tool" name="tool_export">
        <bitmap stock_id="wxART_MISSING_IMAGE"/>
        <tooltip>export project...</tooltip>
        <XRCED>
          <events>EVT_TOOL|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      <object class="separator"/>
      <object class="tool" name="tool_up">
        <bitmap stock_id="wxART_GO_UP"/>
        <tooltip>Go Up</tooltip>
        <XRCED>
          <events>EVT_TOOL|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      <object class="tool" name="tool_back">
        <bitmap stock_id="wxART_GO_BACK"/>
        <tooltip>Go Back</tooltip>
        <XRCED>
          <events>EVT_TOOL|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      <object class="tool" name="tool_forward">
        <bitmap stock_id="wxART_GO_FORWARD"/>
        <tooltip>Go Forward</tooltip>
        <XRCED>
          <events>EVT_TOOL|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      <object class="separator" name="status_bar"/>
      <object class="wxComboBox" name="address_box">
        <size>300</size>
        <content>
          <item>/</item>
        </content>
        <font>
          <size>15</size>
          <style>normal</style>
          <weight>normal</weight>
          <underlined>0</underlined>
          <family>swiss</family>
          <face>Microsoft YaHei UI</face>
          <encoding>WINDOWS-936</encoding>
        </font>
        <enabled>0</enabled>
        <XRCED>
          <events>EVT_COMBOBOX|EVT_TEXT|EVT_TEXT_ENTER|EVT_UPDATE_UI</events>
          <assign_var>1</assign_var>
        </XRCED>
      </object>
      
      
      
      
      <bitmapsize>32,32</bitmapsize>
      <style>wxTB_FLAT</style>
      <XRCED>
        <assign_var>1</assign_var>
      </XRCED>
    </object>
    <object class="wxStatusBar" name="status_bar">
      <XRCED>
        <assign_var>1</assign_var>
      </XRCED>
    </object>
    <size>1024,768</size>
    <title>Structer</title>
    <centered>1</centered>
    <style>wxDEFAULT_FRAME_STYLE</style>
    <XRCED>
      <events>EVT_CLOSE</events>
    </XRCED>
    <object class="wxBoxSizer">
      <orient>wxVERTICAL</orient>
      <object class="sizeritem">
        <object class="wxPanel" name="main_panel">
          <size>1024,600</size>
          <XRCED>
            <assign_var>1</assign_var>
          </XRCED>
        </object>
        <option>1</option>
        <flag>wxEXPAND</flag>
      </object>
    </object>
  </object>
</resource>'''

    wx.MemoryFSHandler.AddFile('XRC/frame/frame_xrc', frame_xrc)
    __res.Load('memory:XRC/frame/frame_xrc')

