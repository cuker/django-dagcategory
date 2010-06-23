from django.contrib import admin

class DAGItemAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dagcategory/dagcategory/change_list.html'

class DAGCategoryAdmin(DAGItemAdmin):
    search_fields = ('path',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('sites', )
    list_display = ('name', 'path')
    raw_id_fields = ('parent',)    
    category_hierarchy = 'parent'
