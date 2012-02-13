from django.conf import settings
from django.views.generic import ListView, DetailView

from django.db.models.sql.query import FieldError

from models import DAGCategory

class DAGCategoryItemView(DetailView):
    pass

class DAGCategoryView(ListView):
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
    #model = DAGItems
    
    detail_view = DAGCategoryItemView
    category_model = DAGCategory
    category_method = None
    slug_field = None
    paginate_by = getattr(settings, 'DEFAULT_PAGINATE_BY', 20)
    max_view_all = None
    available_sorts = None
    extra_args = 1
    
    def fetch_category_and_extras(self):
        if 'category' in self.kwargs:
            self.category = self.kwargs['category']
            self.extras = None
        else:
            self.category, self.extras = self.category_model.objects.select_from_url(self.kwargs['path'], self.extra_args)
    
    def get_category(self):
        if not hasattr(self, 'category'):
            self.fetch_category_and_extras()
        return self.category
    
    def get_order_by(self):
        orders = self.request.GET.getlist('order')
        if orders:
            if self.available_sorts:
                p_orders = list()
                for order in orders:
                    order = self.available_sorts.get(order, None)
                    if order is None:
                        raise ResponseException(BadResponseView(request=self.request).render_to_response({'why':'Invalid order option'}))
                p_orders.append(order)
            else:
                p_orders = orders
            return p_orders
    
    def get_context_data(self, **kwargs):
        data = ListView.get_context_data(self, **kwargs)
        data['order'] = self.get_order_by()
        data['category'] = self.get_category()
        data['available_sorts'] = self.available_sorts
        return data
    
    def get_paginate_by(self, queryset):
        category = self.get_category()
        
        if self.extras:
            if (self.paginate_by and len(self.extras) == 1 and self.extras[0] == 'view-all'):
                return None
        return ListView.get_paginate_by(self, queryset)
    
    def get_queryset(self):
        queryset = ListView.get_queryset(self).distinct()
        category = self.get_category()
        if category:
            queryset &= getattr(category, self.category_method)()
        
        order_by = self.get_order_by()
        if order_by:
            queryset = queryset.order_by(*order_by)
        return queryset
    
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        
        self.fetch_category_and_extras()
        if self.extras and self.extras[0] != 'view-all':
            return self.detail_view.as_view(queryset=self.get_queryset())(request, slug=self.extras[0], category=self.get_category())
        return ListView.dispatch(self, request, *args, **kwargs)


