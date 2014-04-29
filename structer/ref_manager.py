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
        '''Gets all objects referenced by "referent"
        
        Args:
            referent: uuid
            
        Returns:
            set of uuids, which are referenced by "referent".
        '''
        return self.__ref.get(referent, set())
    
    def get_referents(self, reference):
        '''Gets all objects referenced to "reference"
        
        Args:
            referent: uuid
            
        Returns:
            set of uuids, which referenced to "refernece"
        '''
        return self.__refby.get(reference, set())
    
    def update_references(self, referent, refs):
        '''Updates references of an object.
        
        Should be called whenever an object changes: create, modify, or delete.        
        Any existing references of referent will be breaked, and then new referneces will be inserted.
        
        Args:
            referent: uuid of the object to be updated
            refs:     list of uuids of the objects referenced by referent
        
        Returns:
            None
        '''
        
        # remove old references, if exists
        if referent in self.__ref:
            for ref in self.__ref[referent]:
                self.__refby[ref].remove(referent)
            del self.__ref[referent]        
        
        # add new references, if any
        if refs:
            for ref in refs:
                if ref in self.__refby:
                    self.__refby[ref].add( referent )
                else:
                    self.__refby[ref] = set([ referent ])
            self.__ref[referent] = refs
    
        
