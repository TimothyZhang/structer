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



import os, json, uuid, time

from structer import log
from structer.event_manager import Event

# folder name of Recycle
RECYCLE = 'Recycle'

# Abort the action
FOLDER_CONFLICTION_STRATEGY_ABORT   = 0
# Choose an available name automatically
FOLDER_CONFLICTION_STRATEGY_RENAME  = 1
# Continue with duplicated name, that we will get 2 folders with the same name!
# This is ONLY used while moving to Recycle
FOLDER_CONFLICTION_STRATEGY_IGNORE  = 2
# Merge two directories
FOLDER_CONFLICTION_STRATEGY_MERGE   = 3
# Replace old folder
FOLDER_CONFLICTION_STRATEGY_REPLACE = 4

class FolderConflictionException(Exception):
    pass

class FileSystemManager(object):  
    """Simulates a virtual file system.

    (The main reason not using native file system is, subversion puts a ".svn" folder in each native folder, and it's
    complicated to manage that correctly if we want to move/rename folders. Althoulgh Latest subversion client
    fixed this problem by putting only one larger ".svn" at the root of working directory, we won't change this
    design unless there're enough reasons)

    VFS contains 2 types of nodes: File and Folder. Each of them has an unique uuid, and is stored in a
    separate file on native file system, the file name is its uuid.

    File node has an attribute "filetype", which is used to determine the type of the file. Currently there are two
    types: object and filter.

    Since too many files in one folder might be slow, Node files are stored in 256 sub folders(see _get_real_path())

    Folders in a parent folder must have different names, but files do NOT have to.(currently, since file names are
    dynamically generated by its content)

    There's a special folder "/Recycle", which is like Recycle Bin under windows. All deleted file/folders are moved
    to Recycle instead of been deleted. But If you delete file/folders in Recycle, they'll been physically removed.

    The abbreviation of "FileSystem" is "FS" or "fs", eg:
        fs_manager: instance of FileSystemManager
        FSNode    : a File System Node

    Node actions:
        create    creates a new file or folder.
        modify    changes content of a file, or name of a folder.
        move      moves a file/folder to a new location.
        delete    moves a file/folder to RecycleBin.
                  will generate a RECYCLE event for each descendants
        undelete  moves a file/folder from RecycleBin to its original location, or a specified location.
                  will generate a RESTORE event for each descendants
        destroy   permanently deletes file/folder from native file system.
    """

    def __init__(self, project, path):
        self._project = project
        self._native_path = path

        # {uuid: Node}
        self._nodes = {}

        self._root = None
        self._recycle = None

    @property
    def project(self):
        return self._project

    @property
    def root(self):
        return self._root

    @property
    def recycle(self):
        return self._recycle
    
    def _create_uuid(self):
        return unicode(uuid.uuid4().hex)

    def iter(self, includes_deleted):
        return self.walk(self._root, includes_deleted)

    def walk_parent_first(self, node, includes_deleted):
        '''Iterates all nodes'''
        if node is self._recycle and not includes_deleted:
            return

        yield node

        if isinstance(node, Folder):
            for child in node.children:
                for grand in self.walk(child, includes_deleted):
                    yield grand

    walk = walk_parent_first

    def load(self):
        '''Returns True if it's a new FS, otherwise False'''
        self._root = None
        is_new = False

        # create native folder if it not exists
        if not os.path.exists(self._native_path):
            os.makedirs(self._native_path)
            is_new = True

        # read all files in 256 sub folders
        for dir in os.listdir(self._native_path):
            if dir == '.svn':
                continue

            dp = os.path.join(self._native_path, dir)

            if not os.path.isdir(dp):
                continue

            for fn in os.listdir(dp):
                if fn == '.svn':
                    continue

                fp = os.path.join(dp, fn)

                # read data
                data = json.load(open(fp, 'rb'))

                # get type
                node_type = data['type']
                node_class = globals()[node_type]

                # create node
                uuid = fn   # fn is uuid
                node = node_class(uuid)

                # init node
                node.load(data)

                # manage node
                self._nodes[uuid] = node

        # fix parent/children of nodes
        for node in self._nodes.itervalues():
            if node._parent_uuid:                
                p = self.get_node_by_uuid(node._parent_uuid)
                assert p, 'parent node of %s not found: %s' % (node.uuid, node._parent_uuid)
                p.add_child(node)
            else:
                assert self._root is None, 'multiple roots: %s %s' % (self._root.uuid, node.uuid)
                self._root = node

        # create root if not exists
        if self._root is None:
            self._root = Folder(self._create_uuid())
            self._save(self._root)
            is_new = True

        # create recycle if not exists
        self._recycle = self._root.get_sub_folder_by_name(RECYCLE)
        if self._recycle is None:
            self._recycle = self.create_folder(self._root, RECYCLE)

        self._root.immutable = True
        self._recycle.immutable = True

        return is_new

    def get_node_by_uuid(self, uuid):
        return self._nodes.get(uuid)

#     def get_node_by_path(self, path):
#         if path == '/':
#             return self._root
#
#         p, s = os.path.split(path)
#         parent = self.get_node_by_path(p)
#         if parent:
#             return parent.children.get_children_by_name(s)

    def _new_event(self, action, *args):
        self.project.event_manager.process(FSEvent(action, *args))

    def create_file(self, parent, filetype, name, data):
        '''Returns new file'''
        if parent == self._recycle:
            raise Exception(u'Can not create file in Recycle')

        file_ = File(self._create_uuid(), filetype, name, data)
        assert file_.uuid not in self._nodes

        self._nodes[file_.uuid] = file_
        parent.add_child(file_)

        try:
            self._save(file_)
        except:
            # rollback
            parent.remove_child(file_)
            self._nodes.pop(file_.uuid)
            raise

        self._new_event(FSEvent.CREATE, file_)
        return file_

    def save_file(self, uuid, data=None):
        file = self._nodes.get(uuid)
        
        if data is not None:
            old_data = file.data
            file.data = data
        try:
            self._save(file)
        except:
            if data is not None:
                file.data = old_data
            raise

        self._new_event(FSEvent.MODIFY, file)

    def is_recycled(self, node_or_uuid):
        if isinstance(node_or_uuid, FSNode):
            node = node_or_uuid
        else:
            node = self.get_node_by_uuid(node_or_uuid)

        if node is self._recycle:
            return False

        while node and node != self._recycle:
            node = node.parent

        if node is self._recycle:
            return True

        return False

    # noinspection PyMethodMayBeStatic
    def is_ancestor(self, a, b):
        while b:
            if a == b:
                return True
            b = b.parent

        return False

#     def is_recycle(self, node_or_uuid):
#         if isinstance(node_or_uuid, FSNode):
#             node = node_or_uuid
#         else:
#             node = self.get_node_by_uuid(node_or_uuid)
#
#         return node == self._recycle

    def create_folder(self, parent, name, strategy=FOLDER_CONFLICTION_STRATEGY_ABORT):
        '''Creates a new folder under given parent folder

        Args:
            parent: parent folder
            name: name of new folder
            strategy: FOLDER_CONFLICTION_STRATEGY_*. what to do if a folder with same name already exists?


        Returns
            new folder
        '''

        # not in Recycle
        if parent is self.recycle:
            raise Exception(u'Can not create folder in Recycle')

        # no name confliction
        duplicated = parent.get_sub_folder_by_name(name)
        if duplicated:
            if strategy == FOLDER_CONFLICTION_STRATEGY_ABORT:
                raise FolderConflictionException('Folder with the same name already exists.')
            if strategy == FOLDER_CONFLICTION_STRATEGY_RENAME:
                base = name
                i = 1
                while parent.get_sub_folder_by_name(name):
                    name = '%s %s' % (base, i)
                    i += 1
            elif strategy == FOLDER_CONFLICTION_STRATEGY_IGNORE:
                pass
            elif strategy == FOLDER_CONFLICTION_STRATEGY_REPLACE:
                self.delete(duplicated.uuid)
            elif strategy == FOLDER_CONFLICTION_STRATEGY_MERGE:
                return duplicated
            else:
                raise Exception('Invalid folder confliction strategy: %s' % strategy)

        # create
        node = Folder(self._create_uuid(), name)
        assert node.uuid not in self._nodes
        self._nodes[node.uuid] = node
        parent.add_child(node)

        try:
            self._save(node)
        except:
            # rollback
            parent.remove_child(node)
            self._nodes.pop(node.uuid)
            raise

        # notify
        self._new_event(FSEvent.CREATE, node)
        return node

    def rename(self, uuid_, name):
        """Renames a folder"""
        node = self.get_node_by_uuid(uuid_)

        # Only folder
        # assert type(node) is Folder

        # no imuutable
        if node.immutable:
            raise Exception("%s is immutable" % node)

        # no name confliction
        if node.parent.get_sub_folder_by_name(name):
            raise Exception('Folder with name "%s" already exists' % name)

        if not name:
            raise Exception('Folder name should not be empty')

        old_name = node.name
        node.name = name
        try:
            self._save(node)
        except:
            # rollback
            node.name = old_name
            raise

        # notify
        self._new_event(FSEvent.MODIFY, node)
        return node

    def copy(self, node, parent, strategy=FOLDER_CONFLICTION_STRATEGY_ABORT):
        '''
        Args:
            stratege: FOLDER_CONFLICTION_STRATEGY_*. what to do if a folder with the same name already exists?
        '''
        assert node != self._root
        assert node != self._recycle
        assert parent != self._recycle

        if self.is_ancestor(node, parent):
            raise Exception("Could not copy to its descendant.")

        new = self._copy_tree(node, parent, strategy)
        return new

    def _copy_tree(self, node, parent, strategy):
        if type(node) is Folder:
            new = self.create_folder(parent, node.name, strategy)

            for child in node.children:
                self._copy_tree(child, new, strategy)
            return new
        elif type(node) is File:
            new = self.create_file(parent, node.file_type, node.name, node.data)
            return new
        else:
            raise Exception('invalid node type: %s' % type(node))

    def move(self, node, parent, strategy=FOLDER_CONFLICTION_STRATEGY_ABORT):
        '''Moves a file/folder to another location

        Args:
            node: file/folder to move
            parent: target location
            strategy: FOLDER_CONFLICTION_STRATEGY_*. what to do if a folder with the same name already exists?

        '''
        assert not node.immutable

        if self.is_ancestor(node, parent):
            raise Exception('Could not move to its descendant.')

        old_parent = node.parent
        if old_parent == parent:
            return old_parent

        if isinstance(node, Folder):
            dup = parent.get_sub_folder_by_name(node.name)
            if dup:  # name collision
                if strategy == FOLDER_CONFLICTION_STRATEGY_ABORT:
                    raise FolderConflictionException('Folder with the same already exists.')

                if strategy == FOLDER_CONFLICTION_STRATEGY_RENAME:
                    # auto rename
                    i = 0
                    while 1:
                        name = '%s (%s)' % (node.name, i)
                        if not parent.get_sub_folder_by_name(name):
                            break
                        i += 1
                    node.name = name
                elif strategy == FOLDER_CONFLICTION_STRATEGY_IGNORE:
                    pass
                elif strategy == FOLDER_CONFLICTION_STRATEGY_MERGE:
                    try:
                        for child in node.children:
                            self.move(child, dup, strategy)
                    except Exception, e:
                        log.error(e, "Not all files/folders moved!")
                        raise

                    self.delete(node.uuid)
                    return old_parent
                elif strategy == FOLDER_CONFLICTION_STRATEGY_REPLACE:
                    self.delete(dup.uuid)

        old_parent.remove_child(node)
        parent.add_child(node)

        try:
            self._save(node)
        except:
            # rollback
            parent.remove_child(node)
            old_parent.add_child(node)
            raise

        self._new_event(FSEvent.MOVE, node, old_parent)
        return old_parent

    def delete(self, uuid_):
        """Delete a FSNode.

        Deleted nodes are marked as "deleted", native files will never been removed physically
        """
        node = self.get_node_by_uuid(uuid_)

        assert node
        assert not node.immutable
        assert not self.is_recycled(node)

        p = node.parent
        try:
            node.orginal_parent_uuid = p.uuid
            self.move(node, self._recycle, FOLDER_CONFLICTION_STRATEGY_IGNORE)
        except:
            node.orginal_parent_uuid = ''
            raise

        for n in self.walk(node, True):
            self._new_event(FSEvent.RECYCLE, n)

    def undelete(self, node, parent=None, strategy=FOLDER_CONFLICTION_STRATEGY_ABORT):
        # node = self.get_node_by_uuid(uuid)
        assert node
        assert not node.immutable
        assert node.parent == self._recycle

        if parent is None:
            parent = self.get_node_by_uuid(node.orginal_parent_uuid)
            if parent is None:
                log.warn("parent not exists, restore to /")
                parent = self._root

        try:
            self.move(node, parent, strategy)
        except:
            raise

        for n in self.walk(node, True):
            self._new_event(FSEvent.RESTORE, n)
        node.orginal_parent_uuid = ''

    def destroy(self, uuid_):
        node = self.get_node_by_uuid(uuid_)

        assert not node.immutable
        assert node.parent == self._recycle

        self._recycle.remove_child(node)

        try:
            self._destroy_tree(node)
        except:
            self._recycle.add_child(node)
            raise

    def _destroy_tree(self, node):
        if isinstance(node, Folder):
            for child in node.children:
                self._destroy_tree(child)

        fp = self._get_real_path(node.uuid)
        os.remove(fp)

        self._nodes.pop(node.uuid)
        self._new_event(FSEvent.DELETE, node)

    def _save(self, node):
        # node.touch()
        data = node.dump()

        rp = self._get_real_path(node.uuid)
        dir_ = os.path.split(rp)[0]
        if not os.path.exists(dir_):
            os.makedirs(dir_)

        open(rp, 'wb').write(json.dumps(data, separators=(',\n', ':\n'), sort_keys=True))

    def _get_real_path(self, uuid_):
        """Returns the location of an uuid on native file system"""
        return os.path.join(self._native_path, uuid_[:2], uuid_)

    def dump(self, node=None, indent=0):
        if node is None:
            node = self._root

        if node:
            print ' '*(indent-1), node.uuid

            if isinstance(node, Folder):
                for child in node.children:
                    self.dump(child, indent+2)

        
class FSNode(object):
    uuid = ''        
    create_time = 0
    modify_time = 0
    orginal_parent_uuid = ''
    name = ''
    immutable = False
    parent = None

    # _parent_uuid should only be used for loading data
    
    def __init__(self, uuid_):
        self.uuid = uuid_
        self.create_time = self.modify_time = time.time()      
        
    def load(self, data):
        '''Loads from native file
        
        Args:
            data: dict
        '''
        self._parent_uuid = data.get('parent', '')
#         self.is_recycled = data.get('is_recycled', 0)
        self.orginal_parent_uuid = data.get('orginal_parent_uuid', '')
        self.modify_time = data.get('modify_time', time.time())
        self.create_time = data.get('create_time', time.time())
        self.name = data.get('name', '')
        
        self._load(data)

    def _load(self, data):
        pass

    def _dump(self):
        """
        :rtype: dict
        """
        raise NotImplementedError()

    # def touch(self):
    #     self.modify_time = time.time()
    
    def dump(self):
        '''dump node to native file
        
        Returns:
            dict
        '''
        r = {'type': self.__class__.__name__,
             'name': self.name, 
             'modify_time': self.modify_time, 
             'create_time': self.create_time}
        
        if self.parent:
            r['parent'] = self.parent.uuid
#         if self.is_recycled:
#             r['is_recycled'] = True
        if self.orginal_parent_uuid:
            r['orginal_parent_uuid'] = self.orginal_parent_uuid
            
        r.update( self._dump() )
        return r

    def __unicode__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.uuid)
    
    def __str__(self):
        return self.__unicode__()


class File(FSNode):        
    def __init__(self, uuid_, file_type='', name='', data=''):
        FSNode.__init__(self, uuid_)
        
        self.file_type = file_type
        self.data = data if data is not None else {}
        self.tags = set()
        self.name = name
        
    def _load(self, data):
        self.file_type = data['filetype']
        self.data = data['data']
        self.tags = set(data.get('tags', []))
        
    def _dump(self):
        return {'data': self.data, 'filetype': self.file_type, 'tags': list(self.tags)}


class Folder(FSNode):
    def __init__(self, uuid_, name=''):
        FSNode.__init__(self, uuid_)
        
        self.children = []
        self.name = name
        
    @property
    def path(self):
        if self.parent:
            return self.parent.path + u"/" + self.name
        
        return u''
        
    def _load(self, data):
        # self.name = data['name']
        pass
               
    def add_child(self, node):
        assert node.parent is None
        assert node not in self.children
        
        self.children.append(node)
        node.parent = self
        
    def remove_child(self, node):
        assert node.parent == self
        
        self.children.remove(node)
        node.parent = None
        
    def _dump(self):
        # return {'name': self.name}
        return {}
    
    def get_sub_folder_by_name(self, name):
        for c in self.children:
            if isinstance(c, Folder) and c.name == name:
                return c
    
    def __unicode__(self):
        return '<Folder %s>' % self.name


class FSEvent(Event):
    CREATE = 'fs-create'  
    # permanently deleted     
    DELETE = 'fs-delete'
    # moved to recycle bin    
    # DELETE  = 'fs-delete'
    MODIFY = 'fs-modify'    
    # "original_parent" is available
    MOVE = 'fs-move'
    
    RECYCLE = 'fs-recycle'
    RESTORE = 'fs-restore'
    
    def __init__(self, action, fs_node, original_parent=None):
        self._action = action
        self._fs_node = fs_node
        self._original_parent = original_parent
        
    @property
    def action(self):
        return self._action
    
    @property
    def fs_node(self):
        return self._fs_node
    
    @property
    def original_parent(self):
        '''Valid in FSEvent.DELETE'''
        return self._original_parent

    def get_keys(self):
        return self.create_sliced_keys((self._action, self._fs_node.uuid))
          
    @staticmethod
    def get_key_of(action, fs_node=None):
        if fs_node:
            return action, fs_node.uuid
        return action,
        
if __name__ == '__main__':
    fm = FileSystemManager('../../test/data')
    fm.load()
    fm.dump()
