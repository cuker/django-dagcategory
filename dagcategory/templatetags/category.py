from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()

@register.inclusion_tag('admin/category_hierarchy.html')
def category_hierarchy(cl):
    if getattr(cl.model_admin, 'category_hierarchy', False):
        field_name = cl.model_admin.category_hierarchy
        path_field = '%s__path__startswith' % field_name
        field_generic = '%s__' % field_name
        path_lookup = cl.params.get(path_field)

        link = lambda d: mark_safe(cl.get_query_string(d, [field_generic]))
        field = cl.opts.get_field_by_name(field_name)[0]
        if hasattr(field, 'rel'):
            cat_model = field.rel.to #many2many
        else:
            cat_model = field.model #foreignkey
        if path_lookup:
            try:
                category = cat_model.objects.get(path=path_lookup)
            except:
                return
            cx = {'show':True}
            if category.parent:
                cx['back'] = {
                    'link' : link({path_field:category.parent.path}),
                    'title': category.parent.name
                }
            else:
                cx['back'] = {
                    'link' : link({}),
                    'title': _('All categories')
                }
            cx['choices'] = [{
                'link': link({path_field:child.path}),
                'title': child.name
            } for child in category.children.all()]
            return cx
        else:
            return {'show':True,
                    'choices': [{
                        'link': link({path_field:child.path}),
                        'title': child.name
                    } for child in cat_model.objects.filter(parent__isnull=True)]
                    }

