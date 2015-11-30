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


import json

from base import BaseExporter


class Exporter(object):
    def get_name(self):
        u"""
        @return string:
            name of current exporter
        """
        
        return '[%s]' % self.__class__.__name__
    
    def get_exported_wildcard(self):
        u"""
        Gets wildcard string of exported file type.
            eg:  "Zip archive (*.zip)|*.zip"

        @return string:
            wildcard of exported file, or None if export to a folder
        """
        return None

    def export(self, project, writefunc):
        u"""
        Exports a structer project.

        @param project: Project
            the project to be exported
        """
        raise


class DefaultObjectExporter(BaseExporter):
    def export(self):
        project = self.project

        # objects for each class
        for clazz in project.type_manager.get_clazzes():
            clazz_all = {}
            for obj in project.object_manager.get_objects(clazz):
                clazz_all[obj.id] = obj.export()

            data = json.dumps(clazz_all, sort_keys=True)
            self.save('%s.json' % clazz.name, data)
