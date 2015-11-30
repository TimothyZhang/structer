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


import optparse
from structer.project import Project


def export(project_path, dst_path):
    p = Project(project_path, False)
    p.load()
    
    if p.has_error():
        raise Exception('All errors must be fixed before exporting.')
    
    from structer.exporter import DefaultObjectExporter
    exp = DefaultObjectExporter()
    
    from zipfile import ZipFile
    zf = None
    try:
        zf = ZipFile(dst_path, 'w')
        exp.export(p, zf.writestr)
    finally:
        if zf:
            zf.close()


def make_option_parser():
    usage = """%prog -s project_path -d output_path export"""
    
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-s', '--source', dest="source", help="source(project) folder")
    parser.add_option('-d', '--dest', dest="dest", help="dest(output) folder")
    return parser


def main():
    parser = make_option_parser()        
    (options, args) = parser.parse_args()
    
    if len(args) == 1:
        cmd = args[0]    
        if cmd == 'export':                     
            export(options.source, options.dest)
            return
        
    parser.print_usage()


if __name__ == '__main__':
    main()