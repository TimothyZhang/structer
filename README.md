Structer
========

Structer is a "Structured Data Editor" base on wxPython.

Structer is originally developed for editing game data, while it also can be used for other purposes.


Install & Run
=============

* Prerequisites:
  * Python 2.7 (3.0 not supported now)
  * wxPython >= 3.0 (>= 2.9 might work but not tested)

* Open GUI Editor:

  `python structerui.py`
  
  Windows user: just double click `structerui.py` in explorer.
  
* Export a project in command line:

  `python structer.py -s <project_dir> -d <output_dir>`


Platforms
=========

Structer should run under windows/osx/linux, but only Windows 7/10 is tested.


Hot keys
========

While editing a list, use "Ctrl+." to append a new row and "Ctrl+d" to delete a row.
 
For more hot keys available please read doc/hotkey.txt.


TODO
====

- add tutorial and user guide
- tag support
- each object can be marked as export/don't export(or with label)
- confirm when trying to delete a reference object
- curve editing?
- support travis/coverage?
- add unittest
- customized exporters
- plugin


License
=======

Structer is distributed under the GPL v3.  See LICENSE for more details.

Images used by Structer are downloaded from internet. If any of them is prohibited to use, please 
contact me at (zt at live dot cn).


Contributing
============

Please feel free to send pull requests.
