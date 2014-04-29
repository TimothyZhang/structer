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




class xrcProjectDialog(wx.Dialog):
#!XRCED:begin-block:xrcProjectDialog.PreCreate
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
#!XRCED:end-block:xrcProjectDialog.PreCreate

    def __init__(self, parent):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreDialog()
        self.PreCreate(pre)
        get_resources().LoadOnDialog(pre, parent, "ProjectDialog")
        self.PostCreate(pre)

        # Define variables for the controls, bind event handlers
        self.text_ctrl = xrc.XRCCTRL(self, "text_ctrl")
        self.button_browse = xrc.XRCCTRL(self, "button_browse")
        self.list_box = xrc.XRCCTRL(self, "list_box")
        self.checkbox_create = xrc.XRCCTRL(self, "checkbox_create")
        self.button_open = xrc.XRCCTRL(self, "button_open")

        self.Bind(wx.EVT_BUTTON, self.OnButton_button_browse, self.button_browse)
        self.Bind(wx.EVT_LISTBOX, self.OnListbox_list_box, self.list_box)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListbox_dclick_list_box, self.list_box)
        self.Bind(wx.EVT_BUTTON, self.OnButton_button_open, self.button_open)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ui_button_open, self.button_open)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar_hook)

#!XRCED:begin-block:xrcProjectDialog.OnButton_button_browse
    def OnButton_button_browse(self, evt):
        # Replace with event handler code
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._set_path(path)

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
    
    def _set_path(self, path):
        self.text_ctrl.SetValue(path) 
#!XRCED:end-block:xrcProjectDialog.OnButton_button_browse        

#!XRCED:begin-block:xrcProjectDialog.OnListbox_list_box
    def OnListbox_list_box(self, evt):
        # Replace with event handler code
        index = evt.GetSelection()
        if 0<=index<self.list_box.GetCount():
            path = self.list_box.GetString(index)
            self._set_path(path)
#!XRCED:end-block:xrcProjectDialog.OnListbox_list_box        

#!XRCED:begin-block:xrcProjectDialog.OnListbox_dclick_list_box
    def OnListbox_dclick_list_box(self, evt):
        self.OnListbox_list_box(evt)
        
        path = self.text_ctrl.GetValue()
        if self._is_valid(path):
            self.EndModal(wx.ID_OK)
#!XRCED:end-block:xrcProjectDialog.OnListbox_dclick_list_box        

#!XRCED:begin-block:xrcProjectDialog.OnButton_button_open
    def OnButton_button_open(self, evt):
        # Replace with event handler code
        self.EndModal(wx.ID_OK)        
        
    def get_path(self):
        return self.text_ctrl.GetValue()
    
    def should_create(self):
        return self.checkbox_create.IsChecked()
    
    def set_recent_paths(self, paths):
        self.list_box.Clear()
        for path in paths:
            self.list_box.Append(path)
        
        if len(paths):
            self.list_box.SetSelection(0)
            self.text_ctrl.SetValue( paths[0] )
#!XRCED:end-block:xrcProjectDialog.OnButton_button_open        

#!XRCED:begin-block:xrcProjectDialog.OnUpdate_ui_button_open
    def OnUpdate_ui_button_open(self, evt):
        # Replace with event handler code
        path = self.text_ctrl.GetValue()
        evt.Enable( self._is_valid(path) )
    
    def _is_valid(self, path):
        import os
        return not os.path.exists(path) or os.path.isdir(path)
#!XRCED:end-block:xrcProjectDialog.OnUpdate_ui_button_open        

#!XRCED:begin-block:xrcProjectDialog.OnChar_hook
    def OnChar_hook(self, evt):
        # Replace with event handler code
        key = evt.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        
        evt.Skip()
#!XRCED:end-block:xrcProjectDialog.OnChar_hook        




# ------------------------ Resource data ----------------------

def __init_resources():
    global __res
    __res = xrc.EmptyXmlResource()

    wx.FileSystem.AddHandler(wx.MemoryFSHandler())

    project_dialog_xrc = '''\
<?xml version="1.0" ?><resource class="wxListBox">
  <object class="wxDialog" name="ProjectDialog">
    <object class="wxBoxSizer">
      <orient>wxHORIZONTAL</orient>
      <object class="spacer">
        <size>5,5</size>
      </object>
      <object class="sizeritem">
        <object class="wxBoxSizer">
          <object class="spacer">
            <size>5,15</size>
          </object>
          <object class="sizeritem">
            <object class="wxBoxSizer">
              <object class="sizeritem">
                <object class="wxStaticText">
                  <label>Path:</label>
                </object>
                <flag>wxALIGN_LEFT|wxALIGN_CENTRE_VERTICAL</flag>
              </object>
              <object class="spacer">
                <size>5,5</size>
              </object>
              <object class="sizeritem">
                <object class="wxTextCtrl" name="text_ctrl">
                  <XRCED>
                    <assign_var>1</assign_var>
                  </XRCED>
                </object>
                <option>1</option>
                <flag>wxEXPAND|wxALIGN_CENTRE_VERTICAL</flag>
                <minsize>400,20</minsize>
              </object>
              <object class="spacer"/>
              <object class="sizeritem">
                <object class="wxButton" name="button_browse">
                  <label>&amp;Browse</label>
                  <XRCED>
                    <events>EVT_BUTTON</events>
                    <assign_var>1</assign_var>
                  </XRCED>
                </object>
                <flag>wxALIGN_RIGHT|wxALIGN_CENTRE_VERTICAL</flag>
              </object>
              <orient>wxHORIZONTAL</orient>
            </object>
            <flag>wxEXPAND</flag>
          </object>
          <object class="spacer">
            <size>5,5</size>
          </object>
          <object class="sizeritem">
            <object class="wxStaticText">
              <label>Recent projects:</label>
            </object>
          </object>
          <object class="spacer">
            <size>5,5</size>
          </object>
          <object class="sizeritem">
            <object class="wxListBox" name="list_box">
              <size>400,200</size>
              <content>
                <item/>
              </content>
              <focused>1</focused>
              <XRCED>
                <events>EVT_LISTBOX|EVT_LISTBOX_DCLICK</events>
                <assign_var>1</assign_var>
              </XRCED>
            </object>
            <option>1</option>
            <flag>wxEXPAND|wxALIGN_CENTRE_HORIZONTAL</flag>
            <minsize>400,200</minsize>
          </object>
          <object class="spacer">
            <size>5,5</size>
          </object>
          <object class="sizeritem">
            <object class="wxBoxSizer">
              <object class="sizeritem">
                <object class="wxCheckBox" name="checkbox_create">
                  <label>create project if not exists</label>
                  <checked>1</checked>
                  <enabled>0</enabled>
                  <XRCED>
                    <assign_var>1</assign_var>
                  </XRCED>
                </object>
                <option>1</option>
                <flag>wxEXPAND|wxALIGN_CENTRE_HORIZONTAL</flag>
              </object>
              <orient>wxHORIZONTAL</orient>
            </object>
            <flag>wxEXPAND</flag>
          </object>
          <object class="spacer">
            <size>5,5</size>
          </object>
          <object class="sizeritem">
            <object class="wxBoxSizer">
              <orient>wxVERTICAL</orient>
              <object class="sizeritem">
                <object class="wxButton" name="button_open">
                  <label>&amp;Open</label>
                  <default>1</default>
                  <XRCED>
                    <events>EVT_BUTTON|EVT_UPDATE_UI</events>
                    <assign_var>1</assign_var>
                  </XRCED>
                </object>
                <flag>wxALIGN_RIGHT|wxALIGN_CENTRE_VERTICAL</flag>
              </object>
            </object>
            <flag>wxEXPAND</flag>
          </object>
          <object class="spacer">
            <size>5,5</size>
          </object>
          <orient>wxVERTICAL</orient>
        </object>
        <option>1</option>
        <flag>wxEXPAND</flag>
      </object>
      <object class="spacer">
        <size>5,5</size>
      </object>
    </object>
    <size>640,480</size>
    <title>Open or create project</title>
    <centered>1</centered>
    <style>wxDEFAULT_DIALOG_STYLE|wxRESIZE_BORDER|wxCLOSE_BOX</style>
    <XRCED>
      <events>EVT_CHAR_HOOK</events>
    </XRCED>
  </object>
</resource>'''

    wx.MemoryFSHandler.AddFile('XRC/project_dialog/project_dialog_xrc', project_dialog_xrc)
    __res.Load('memory:XRC/project_dialog/project_dialog_xrc')

