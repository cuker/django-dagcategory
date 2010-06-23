from django.conf import settings
from django.http import Http404, HttpResponseBadRequest
from django.views.generic import list_detail
from django.db.models.sql.query import FieldError
from django.template.loader import render_to_string

from models import DAGCategory

def render_bad_response(msg, **kwargs):
    return HttpResponseBadRequest(render_to_string('400.html', {'why':msg}, **kwargs))

class DAGCategoryView(object):
    '''
    A generic categorical view handler.
    Implement your own by inheriting this class and setting category_model and object_method
    object_method is the method name beloning to the category that returns a queryset of the items of interest

    An example urls.py entry:

        url(r'^section/(?P<path>.*)/$', 'NewsCategoryView', name='news.views.category'),

    This will take the following as valid urls:

        /section/catparentslug/
        /section/catparentslug/catchildslug/
        /section/catparentslug/catchildslug/objectid/
    '''
    category_model = DAGCategory
    category_method = None
    slug_field = None
    paginate_by = getattr(settings, 'DEFAULT_PAGINATE_BY', 20)
    max_view_all = None
    available_sorts = None

    def __new__(cls, request, **kwargs):
        obj = super(DAGCategoryView, cls).__new__(cls)
        return obj(request, **kwargs)

    def __call__(self, request, path, **kwargs):
        '''
        Dispatches the request
        Attempts to find a category followed by the object (if any)
        '''
        obj, extras = self.lookup_category(request, path)
        queryset = self.get_queryset(obj)
        if extras:
            if (self.paginate_by and len(extras) == 1 and extras[0] == 'view-all'):
                return self.view_all(request, obj, queryset, **kwargs)
            return self.object_detail(request, obj, queryset, extras, **kwargs)
        orders = request.GET.getlist('order')
        if orders:
            kwargs.setdefault('extra_context', dict())
            kwargs['extra_context']['order'] = orders
            if self.available_sorts:
                p_orders = list()
                for order in orders:
                    order = self.available_sorts.get(order, None)
                    if order is None:
                        return render_bad_response('Invalid order option')
                p_orders.append(order)
            else:
                p_orders = orders
            queryset = queryset.order_by(*p_orders)
            try:
                if hasattr(queryset.query, 'as_sql'):
                    queryset.query.as_sql()
                else: #fix for Django 1.2 
                    unicode(queryset.query) #TODO investigate if there is a better way, like a validate function
            except FieldError:
                return render_bad_response('Invalid order option')
        return self.category_detail(request, obj, queryset, **kwargs)

    def lookup_category(self, request, path, limit=1):
        obj, extras = self.category_model.objects.select_from_url(path, limit)
        if not obj:
            raise Http404('Category Not Found')
        return obj, extras

    def get_queryset(self, obj):
        return getattr(obj, self.category_method)()

    def category_detail(self, request, category, queryset, **kwargs):
        '''
        Renders the category view
        '''
        kwargs.setdefault('extra_context', {})
        if self.paginate_by is not None:
            kwargs.setdefault('paginate_by', int(request.GET.get('paginate_by', self.paginate_by)))
        kwargs['extra_context']['category'] = category
        kwargs['extra_context']['available_sorts'] = self.available_sorts
        return list_detail.object_list(request, queryset, **kwargs)
    
    def view_all(self, request, category, queryset, **kwargs):
        kwargs.setdefault('extra_context', {})
        kwargs.pop('paginate_by', None)
        kwargs['extra_context']['category'] = category
        kwargs['extra_context']['view_all'] = True
        if self.max_view_all:
            queryset = queryset[:self.max_view_all]
        return list_detail.object_list(request, queryset, **kwargs)

    def object_detail(self, request, category, queryset, extras, **kwargs):
        '''
        Renders the object view
        '''
        id = extras.pop(0)
        if self.slug_field:
            kwargs['slug_field'] = self.slug_field
            kwargs['slug'] = id
        else:
            kwargs['object_id'] = id
        kwargs.pop('paginate_by', None)
        kwargs.setdefault('extra_context', {})
        kwargs['extra_context'].update({'category': category,
                                        'extras':extras,})
        return list_detail.object_detail(request, queryset, **kwargs)

class DAGDateCategoryView(DAGCategoryView):
    '''
    A categorical and date based view handler
    You must specifiy a date_field in order for this to work

    This will take the following as valid urls:

        /section/catparentslug/2009/08/
        /section/catparentslug/catchildslug/2009/08/01/
        /section/catparentslug/catchildslug/2009/08/01/objectid/
    '''
    date_field = None

    def __call__(self, request, path, **kwargs):
        obj, extras = self.lookup_category(request, path, limit=4)
        queryset = self.get_queryset(obj)
        filters = dict()
        if extras:
            fields = ['__year', '__month', '__day']
            try:
                while extras and fields:
                    filters[self.date_field+fields.pop(0)] = int(extras.pop(0))
            except ValueError:
                raise Http404('Invalid Date') #not a valid integer
            queryset = queryset.filter(**filters)
        kwargs.setdefault('extra_context', {})
        kwargs['extra_context']['date_list'] = self.get_dates(obj, queryset, filters)
        if extras:
            return self.object_detail(request, obj, queryset, extras, **kwargs)
        return self.category_detail(request, obj, queryset, **kwargs)

    def get_dates(self, category, queryset, filters, order='DESC'):
        kind = ('year', 'month', 'day', 'day')[len(filters)]
        return queryset.dates(self.date_field, kind, order)
