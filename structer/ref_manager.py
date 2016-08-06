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


class RefManager(object):
    """Manages referencs between objects.
    
    Managed by ObjectManager
    """
    
    def __init__(self):
       
        # {referer_uuid: set([referent_uuid, ...])}
        self.__ref = {}
        """:type: dict[str, set[str]]"""
        
        # {referent_uuid: set([referer_uuid, ...])}
        self.__refby = {}
        """:type: dict[str, set[str]]"""
    
    def get_referents(self, referer):
        """Gets all objects referenced by "referer"
        
        Args:
            referer: uuid
            
        Returns:
            set of uuids, which are referenced by "referer".
        """
        return self.__ref.get(referer, set())
    
    def get_referers(self, referent):
        """Gets all objects referenced to "referent"
        
        Args:
            referent: uuid
            
        Returns:
            set of uuids, which referenced to "referent"
        """
        return self.__refby.get(referent, set())
    
    def update_references(self, referer, refs):
        """Updates references of an object.
        
        Should be called whenever an object changes: create, modify, or delete.        
        Any existing references of referer will be break, and then new references will be inserted.
        
        :param Object referer: the object changed
        :param list[structer.stype.attr_types.Ref] refs: referenced by referer
        """
        
        # break old references, if exists
        uuid = referer.uuid
        if uuid in self.__ref:
            for ref_uuid in self.__ref[uuid]:
                self.__refby[ref_uuid].remove(uuid)
            del self.__ref[uuid]
        
        # add new references, if any
        if refs:
            ref_uuids = {ref.uuid for ref in refs}
            for ref_uuid in ref_uuids:
                if ref_uuid in self.__refby:
                    self.__refby[ref_uuid].add(uuid)
                else:
                    self.__refby[ref_uuid] = {uuid}
            self.__ref[uuid] = ref_uuids
