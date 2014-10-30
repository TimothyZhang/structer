import wx, os

class Plugin(object):
    name = 'Plugin'
    label = name
    
    def execute(self, project):
        print 'Plugin.execute'
        

class PluginManager(object):
    def __init__(self):        
        self._plugins = {}
    
    def load_plugins(self):
        # todo: load from src and project folders
        plugin = ImportI18NPlugin()        
        self._plugins[plugin.name] = plugin
        
        plugin = CheckI18NPlugin()
        self._plugins[plugin.name] = plugin
        
        plugin = ExportI18NPlugin()
        self._plugins[plugin.name] = plugin
        
    
    def iter_plugins(self):
        for p in self._plugins.itervalues():
            yield p        

class ExportI18NPlugin(Plugin):
    name = 'i18n_exporter'
    label = "&Export I18N"
    
    def get_languages(self, project):
        i18n = project.type_manager.get_struct_by_name("I18N")
        assert i18n
        
        return [i18n.get_attr_by_index(i).name for i in xrange(i18n.get_attr_count())]

    def choose_dir(self, project):
        dlg = wx.DirDialog(None, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
                        
        ret = dlg.ShowModal()
        dlg.Destroy()
        
        if ret == wx.ID_OK:
            return dlg.GetPath()
        return None        
    
    def execute(self, project):
        ret = {}  # {lang: [ ]}
        
        def check(data):
            if type(data) is dict:
                if 'en' not in data:
                    for v in data.itervalues():
                        check(v)
                elif data['en']:
                    en = data['en']
                    for lang in ret:                        
                        if data[lang]==en:                            
                            ret[lang].append('%s='%en)
                        else:
                            ret[lang].append('%s=%s'%(en, data[lang]))                    
            elif type(data) is list:
                for v in data:
                    check(v)
        
        for lang in self.get_languages(project):
            ret[lang] = []
        
        for clazz in project.type_manager.get_clazzes():
            for lang in ret:
                ret[lang].append('########## %s ##########' % clazz.name)
            objects = list(project.object_manager.iter_objects(clazz))
            objects.sort(key=lambda x:x.id)
            for obj in objects:
                for lang in ret:
                    ret[lang].append('# %s %s' % (obj.id, obj.name))                
                check(obj.raw_data)
            for lang in ret:
                ret[lang].append('')
                    
        self._dump(ret, project)
        

    def _dump(self, ret, project):
        path = self.choose_dir(project)
        if not path:
            return 
        
        for lang, lines in ret.iteritems():
            fn = 'all_i18n_%s.txt' % lang
            fp = os.path.join(path, fn)
            open(fp, 'w').write( '\n'.join(lines).encode('utf-8'))
        wx.MessageBox("Exported to %s" % project.path)        
        
        
class CheckI18NPlugin(Plugin):
    name = 'i18n_checker'
    label = "&Check I18N"
    
    def execute(self, project):
        misses = {}  # {'lang': [en,...]}
        
        def check(data):
            if type(data) is dict:
                if 'en' not in data:
                    for v in data.itervalues():
                        check(v)
                elif data['en']:
                    for lang, val in data.iteritems():
                        if not val:
                            misses.setdefault(lang, set()).add(data['en'])
            elif type(data) is list:
                for v in data:
                    check(v)
        
        for obj in project.object_manager.iter_all_objects():
            check(obj.raw_data)
            
        self._dump(misses, project)
        
        
    def choose_dir(self, project):
        dlg = wx.DirDialog(None, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
                        
        ret = dlg.ShowModal()
        dlg.Destroy()
        
        if ret == wx.ID_OK:
            return dlg.GetPath()
        return None     
            
    def _dump(self, misses, project):
        path = self.choose_dir(project)
        if not path:
            return
        
        for lang, vals in misses.iteritems():
            fn = 'missed_i18n_%s.txt' % lang
            fp = os.path.join(path, fn)
            open(fp, 'w').write( '\n'.join(vals).encode('utf-8'))
        wx.MessageBox("Exported to %s" % project.path)
                
class ImportI18NPlugin(Plugin):
    name = 'i18n_importer'
    label = "&Import I18N"            
    
    def execute(self, project):        
        def patch(data):
            miss = []
            if type(data) is dict:
                # not an i18n dict
                if 'en' not in data:
                    for v in data.itervalues():
                        miss += patch(v)
                    return miss
                
                # is an i18n dict                
                # English text is empty, so translated text should be empty, too
                if not data['en']:
                    data[lang] = u''
                    return []
                
                translated = translation.get(data['en'])
                # not translated...
                if not translated:                        
                    if not data.get(lang):                        
                        data[lang] = u''
                        return [data['en']]
                else:
                    used.add(data['en'])
                    data[lang] = translated
                                                        
            elif type(data) is list:
                for v in data:
                    miss += patch(v)
            
            return miss
                    
        path = self.choose_file()
        if not path:
            print 'Cancelled'
            return
        
        name = os.path.split(path)[1]
        lang = name.split('.')[0].split('_')[1]
        print 'lang:', lang
                        
        content = open(path).read().decode('utf-8')            
        if content[0]==u'\ufeff':  # BOM
            content = content[1:]
                   
        # parse translation                   
        translation = {}
        for i,line in enumerate(content.split('\n')):
            line = line.strip()           
            if not line or line[0]=='#':
                continue
            
            if line.count('=')!=1:
                print 'invalid occurrences of "=" in line', i
                return
            en, translated = line.split('=')
            translation[en] = translated
            
        used = set()           
        print '-'*40, 'not translated map'
        # Recursively update objects  
        all_missing = [] 
        for obj in project.object_manager.iter_all_objects():            
            miss = patch(obj.raw_data) 
            if miss:
                all_missing += miss
                print obj.clazz.name,':', '"%s"(%s)'%(obj.name, obj.id)
                for key in miss:
                    print '   ', key
            project.save_object(obj)
            
        print
        print '-'*40, 'not translated'
        all_missing = set(all_missing)
        for m in all_missing:
            print m
        
        # log translation keys not been used.           
        not_used = set(translation.keys()).difference(used)
        print
        print '-'*40, 'not used'
        for en in not_used:
            print repr(en)
            
    def choose_file(self):
        wildcard = "Text File (*.txt)|*.txt"
        dlg = wx.FileDialog(None, message="Choose export location",                               
                                #defaultDir=self.project.path, 
                                #defaultFile="",
                                wildcard=wildcard ,
                                style=wx.OPEN
                               )
        if wx.ID_CANCEL == dlg.ShowModal():
            dlg.Destroy()
            return None
                            
        path = dlg.GetPath()
        dlg.Destroy()
        return path
