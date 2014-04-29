Structer
========

Structer is a "Structured Data Editor" base on wxPython.

Structer is originally developed for editing game data, while it also can be used for other purposes.


Installation & Run
==================

Prerequisites:

* Python 2.7 (3.0 not supported now)
* wxPython >= 3.0 (>= 2.9 might work but not tested)

Open GUI Editor:
  python structerui.py
  
  Windows user: just double click structerui.py in explorer.
  
Export a project in command line:
  python structer.py -s <project_dir> -d <output_dir>  


Platforms
=========

Structer should run under windows/osx/linux, but only Windows 7 is tested.


Hotkeys
=======

While editing a list, use "Ctrl+." to append a new row and "Ctrl+d" to delete a row.
 
For more hotkeys available please read doc/hotkey.txt.


TODO
====

- add unittest
- support travis/coverage
- add user guide
- customized exporters


Version History
===============

- 0.1.0
    - An usable version without tests and documents.


License
=======

Structer is distributed under the GPL v3.  See LICENSE

Images used by Structer are downloaded from internet. If any of them is prohibited to use, please 
contact me at (zt@live.cn).


Contributing
============

Please feel free to send pull requests to us.
