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
       
        # key referenced values: {uuid: set([uuid, ...])}
        self.__ref = {}
        
        # key referenced by values: {uuid: set([uuid, ...])}
        self.__refby = {}
    
    def get_references(self, referent):
        """Gets all objects referenced by "referent"
        
        Args:
            referent: uuid
            
        Returns:
            set of uuids, which are referenced by "referent".
        """
        return self.__ref.get(referent, set())
    
    def get_referents(self, reference):
        """Gets all objects referenced to "reference"
        
        Args:
            reference: uuid
            
        Returns:
            set of uuids, which referenced to "refernece"
        """
        return self.__refby.get(reference, set())
    
    def update_references(self, referent, refs):
        """Updates references of an object.
        
        Should be called whenever an object changes: create, modify, or delete.        
        Any existing references of referent will be break, and then new references will be inserted.
        
        :param referent: the object changed
        :type referent: Object
        :param refs: referenced by referent
        :type refs: list[structer.stype.attr_types.Ref]
        """
        
        # break old references, if exists
        uuid = referent.uuid
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
