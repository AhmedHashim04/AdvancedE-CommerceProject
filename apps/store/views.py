# import hashlib
# from decimal import Decimal
# import time; start = time.time()
# from django.contrib import messages
# from django.core.cache import cache
# from django.core.paginator import Paginator
# from django.db import IntegrityError, transaction
# from django.db.models import Count, Max, Min, Q, ExpressionWrapper, F, DecimalField
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.http import Http404, HttpResponseRedirect
# from django.shortcuts import get_object_or_404
# from django.utils.decorators import method_decorator
# from django.utils.functional import cached_property
# from django.utils.http import urlencode
# from django.views.generic import DetailView, ListView
# # from django_ratelimit.decorators import ratelimit
# from django.views.decorators.cache import cache_page
# from django.utils.translation import gettext as _
# from .forms import ReviewForm
# from .models import Category, Product, Review, Tag

# # Constants for cache management
# CACHE_TIMEOUT_PRODUCTS = 60 * 60 * 4  # 4 hours
# CACHE_TIMEOUT_PRICE_RANGE = 60 * 60 * 24 * 7  # 7 days

# # @method_decorator(ratelimit(key='ip', rate='30/m', block=True), name='dispatch')
# class ProductListView(ListView):
#     model = Product
#     context_object_name = 'products'
#     template_name = 'product/product_list.html'
#     paginate_by = 24
#     sort_options = {
#         'default': '-created_at',
#         'price_asc': 'price',
#         'price_desc': '-price',
#         'name_asc': 'name',
#         'name_desc': '-name',
#         'rating_desc': '-overall_rating',
#     }
#     items_per_page_options = [24, 48, 96]


#     @cached_property
#     def applied_filters(self):
#         """Extract and sanitize filter parameters"""
#         params = self.request.GET.copy()
#         return {
#             'search': params.get('search', '').strip(),
#             'tag': params.get('tag', '').strip(),
#             'category': params.get('category', '').strip(),
#             'sort_by': params.get('sort_by', 'default'),
#             'min_price': params.get('min_price', ''),
#             'max_price': params.get('max_price', ''),
#             'view_mode': params.get('view_mode', 'grid'),
#             'items_per_page': params.get('items_per_page', str(self.paginate_by)),
#         }

#     def get_queryset(self):
#         # 1. Avoid caching for highly dynamic filters like min/max/search
#         filters = self.applied_filters
#         if filters.get('search') or filters.get('min_price') or filters.get('max_price'):
#             return self.build_queryset()
        
#         query_dict = self.request.GET.dict()  # يحوّل QueryDict إلى dict عادي
#         sorted_items = sorted(query_dict.items())  # ترتيب البارامترات أبجديًا
#         sorted_query_str = urlencode(sorted_items)  # تحويلها لسلسلة URL
#         cache_key = f"products_{hashlib.md5(sorted_query_str.encode()).hexdigest()}"
#         queryset = cache.get(cache_key)

#         if queryset is None:
#             queryset = self.build_queryset()
       

#             cache.set(cache_key, queryset, CACHE_TIMEOUT_PRODUCTS)

#         return queryset

#     def build_queryset(self):
#         """Construct the filtered and annotated queryset"""
#         queryset = (Product.objects
#         .select_related("category")
#         .prefetch_related("tags")
#         .filter(available=True)
#         .only("name", "slug", "price","category__name", "discount", "trending","image", "created_at","overall_rating"))
# # annotate(price_after_discount=ExpressionWrapper( 
# #             F("price") - (F("discount") / Decimal("100") * F("price")),
# #             output_field=DecimalField(max_digits=10, decimal_places=2))).
#         filters = self.applied_filters

#         # Apply search filter
#         if search_term := filters['search']:
#             queryset = queryset.filter(
#                 Q(name__icontains=search_term) |
#                 Q(description__icontains=search_term) 
#             )

#         # Apply category filter
#         if category_slug := filters['category']:
#             queryset = queryset.filter(
#                 Q(category__slug=category_slug) |
#                 Q(category__parent__slug=category_slug)
#             )

#         # Apply tag filter
#         if tag_name := filters['tag']:
#             queryset = queryset.filter(tags__name__iexact=tag_name)

#         # Apply price range filter
#         if min_price := filters['min_price']:
#             try:
#                 min_val = Decimal(min_price)
#                 queryset = queryset.filter(price__gte=min_val)
#             except (ValueError, TypeError):
#                 pass

#         if max_price := filters['max_price']:
#             try:
#                 max_val = Decimal(max_price)
#                 queryset = queryset.filter(price__lte=max_val)
#             except (ValueError, TypeError):
#                 pass

#         # Apply sorting 
#         sort_field = self.sort_options.get(
#             filters['sort_by'], 
#             self.sort_options['default']
#         )

#         return queryset.order_by(sort_field)

#     def get_paginate_by(self,queryset=None):
#         """Get validated items per page setting"""
#         try:
#             per_page = int(self.applied_filters['items_per_page'])
#             return per_page if per_page in self.items_per_page_options else self.paginate_by
#         except (ValueError, TypeError):
#             return self.paginate_by

#     def get_global_price_range(self):
#         """Get cached global price range"""
#         return cache.get_or_set(
#             'global_price_range',{'min_price': 1, 'max_price': 100000},
#             # lambda: Product.objects.aggregate(
#             #     min_price=Min('price'),
#             #     max_price=Max('price')
#             CACHE_TIMEOUT_PRICE_RANGE
#             )

#     def get_context_data(self, **kwargs):
#         """Add filtering context and aggregations"""
#         context = super().get_context_data(**kwargs)
#         filters = self.applied_filters
#         price_range = self.get_global_price_range()

#         # Handle empty price range
#         min_price_val = price_range['min_price'] or Decimal('0')
#         max_price_val = price_range['max_price'] or Decimal('0')

#         # Get validated pagination values
#         paginate_by = self.get_paginate_by()
#         page_obj = context['page_obj']
#         paginator = context.get('paginator')

#         # Ensure paginator and page_obj are present
#         if not paginator or not page_obj:
#             queryset = context.get('products') or self.get_queryset()

#             paginator = Paginator(queryset, paginate_by)
#             page_number = self.request.GET.get('page')
#             page_obj = paginator.get_page(page_number)
#             context['paginator'] = paginator
#             context['page_obj'] = page_obj
#             context['products'] = page_obj.object_list


#         context.update({
#             'categories': cache.get_or_set('all_categories', lambda: Category.objects.prefetch_related('products').all(), CACHE_TIMEOUT_PRODUCTS),
#             'tags': cache.get_or_set('all_tags', lambda: Tag.objects.all(), CACHE_TIMEOUT_PRODUCTS),
                    
#             # These are the filter and sort values currently applied by the user,
#             # used by the frontend to display the selected filters and sorting options
#             # after a search or filter/sort action, ensuring the UI reflects the user's choices.

#             'selected_filter': filters['search'],
            
#             'selected_category': filters['category'],
#             'selected_tag': filters['tag'],
            
#             'sort_by': filters['sort_by'],
#             'min_price': filters['min_price'] or min_price_val,
#             'max_price': filters['max_price'] or max_price_val,
#             'view_mode': filters['view_mode'],

#             'global_min_price': min_price_val,
#             'global_max_price': max_price_val,

#             'items_per_page': paginate_by,
#             'is_paginated': page_obj.has_other_pages(),
#         })
#         return context




# # @method_decorator(ratelimit(key='ip', rate='30/m', method='ALL', block=True), name='dispatch')
# # @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True), name='post')
# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'product/product_detail.html'
#     context_object_name = 'product'
#     slug_field = "slug"
#     slug_url_kwarg = "slug"
#     form_class = ReviewForm
#     paginate_reviews_by = 5
#     max_related_products = 4
#     max_recently_viewed = 5

#     def get_object(self):
#         """Optimize product retrieval with related data"""
#         return get_object_or_404(
#             Product.objects.select_related('category')
#                             .prefetch_related('tags', 'reviews__user'),
#             slug=self.kwargs['slug']
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         product = self.object
#         context['recently_viewed'] = self.get_recently_viewed_products(product)
#         context.update(self.get_reviews_context(product))
#         context.update(self.get_related_products_context(product))
#         context['review_form'] = ReviewForm()
#         self.update_recently_viewed(self.object)
#         return context

#     def get_reviews_context(self, product):
#         """Handle review filtering and pagination"""
#         reviews = Review.objects.filter(product=product).select_related('user')
        
#         # Apply rating filter
#         if rating_filter := self.request.GET.get('rating'):
#             if rating_filter.isdigit() and 1 <= (rating := int(rating_filter)) <= 5:
#                 reviews = reviews.filter(rating=rating)
        
#         # Paginate reviews
#         paginator = Paginator(reviews, self.paginate_reviews_by)
#         page_number = self.request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
        
#         return {
#             'reviews': page_obj.object_list,
#             'page_obj': page_obj,
#             'rating_filter': rating_filter
#         }

#     def get_related_products_context(self, product):
#         """Get context for related products"""
#         max_related = self.max_related_products
#         excluded_ids = {product.id}
        
#         related_products = list(
#             Product.objects.filter(category=product.category)
#             .exclude(id=product.id)
#             .select_related('category')[:max_related]
#         )
#         excluded_ids.update(p.id for p in related_products)
#         if product.category and len(related_products) < max_related:
#             parent_category = product.category.parent
#             if parent_category:
#                 additional_products = Product.objects.filter(
#                     category=parent_category
#                 ).exclude(id__in=excluded_ids).select_related('category')[
#                     :max_related - len(related_products)
#                 ]
#                 related_products += list(additional_products)

#         related_products = related_products[:max_related]

#         return {'related_products': related_products}

#     def get_recently_viewed_products(self, product):
#         """Retrieve recently viewed products from session"""
#         session_key = 'recently_viewed'
#         viewed_slugs = self.request.session.get(session_key, [])
#         # Remove current product and limit
#         if product.slug in viewed_slugs:
#             viewed_slugs.remove(product.slug)
#         viewed_slugs = viewed_slugs[:self.max_recently_viewed]
        
#         return Product.objects.filter(
#             slug__in=viewed_slugs
#         ).select_related('category').exclude(slug=product.slug)

#     def update_recently_viewed(self, product):
#         """Update session with recently viewed products"""
#         session_key = 'recently_viewed'
#         viewed_slugs = self.request.session.get(session_key, [])
        
#         # Remove duplicates and add to beginning
#         if product.slug in viewed_slugs:
#             viewed_slugs.remove(product.slug)
#         viewed_slugs.insert(0, product.slug)
        
#         # Apply limit
#         viewed_slugs = viewed_slugs[:self.max_recently_viewed]
#         self.request.session[session_key] = viewed_slugs
#         self.request.session.modified = True
    
#     def post(self, request, *args, **kwargs):
#         """Handle review submission"""
#         self.object = self.get_object()
#         form = self.form_class(request.POST)
        
#         if form.is_valid():
#             return self.form_valid(form)
#         return self.form_invalid(form)

#     def form_valid(self, form):
#         """Process valid review form"""
#         try:
#             with transaction.atomic():
#                 review, created = Review.objects.get_or_create(
#                     user=self.request.user,
#                     product=self.object,
#                     defaults=form.cleaned_data
#                 )
                
#                 if not created:
#                     # Update existing review
#                     for field, value in form.cleaned_data.items():
#                         setattr(review, field, value)
#                     review.save()
#                     message = "Your review has been updated!"
#                 else:
#                     message = "Thank you for your review!"
                
#                 # Update product rating
#                 self.object.update_rating()
#                 messages.success(self.request, message)
                
#         except IntegrityError:
#             messages.warning(self.request,_("You've already reviewed this product!"))
        

        
#         # Redirect to prevent duplicate submissions
#         return HttpResponseRedirect(self.object.get_absolute_url())

#     def form_invalid(self, form):
#         """Handle invalid form submission"""
#         messages.error(self.request,  _("Please correct the errors below."))
#         context = self.get_context_data(form=form)
#         return self.render_to_response(context)

# # @receiver(post_save, sender=Product)
# # def clear_product_cache(sender, **kwargs):
# #     cache.delete_pattern("products_*")
