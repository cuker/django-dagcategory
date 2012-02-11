from django.contrib import admin

class DAGItemAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dagcategory/dagcategory/change_list.html'
    
    def lookup_allowed(self, key, value):
        ret = super(DAGItemAdmin, self).lookup_allowed(key, value)
        if not ret:
            cat_key = '%s__path__startswith' % self.category_hierarchy
            ret = (key == cat_key)
        return ret

class DAGCategoryAdmin(DAGItemAdmin):
    search_fields = ('path',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('sites', )
    list_display = ('name', 'path')
    raw_id_fields = ('parent',)    
    category_hierarchy = 'parent'
