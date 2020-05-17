from .autocomplete_view import VendorAutocomplete, CategoryAutocomplete, ProductAutoComplete
from django.urls import path, re_path
from .views import (ProductHomepageView, ProductListView, ProductEditListView, ProductCreateView, ProductUpdateView,
                    create_product_vendor_view, product_vendor_delete_view, ProductVendorUpdateView, delete_product_view, copy_product_view

                    )

from .action_views import action_choose_vendor_view
from .product_vendors import ProductVendorListView

urlpatterns = [
    path('homepage/', ProductHomepageView.as_view(), name='product_homepage'), 
    path('list-analysis/', ProductListView.as_view(), name='product_list_analysis'),


    path('edit-views/product/list/', ProductEditListView.as_view(), name='edit_product_list'),
    path('edit-views/product/create/', ProductCreateView.as_view(), name='edit_product_create'),
    path('edit-views/product/update/<int:pk>/', ProductUpdateView.as_view(), name='edit_product_update'),
    path('edit-views/product-vendor-create/<int:pk>/', create_product_vendor_view, name='product_vendor_create'),
    path('edit-views/product-delete/<int:pk>/', delete_product_view, name='edit_product_delete'),

    path('edit-views/product-vendor/<int:pk>/', ProductVendorUpdateView.as_view(), name='product_vendor_edit'),
    path('edit-views/product-vendor-delete/<int:pk>/', product_vendor_delete_view, name='product_vendor_delete'),
    path('edit-views/product/copy/<int:pk>/', copy_product_view, name='copy_product_view'),


    re_path(r'^vendor-autocomplete/$', VendorAutocomplete.as_view(), name='vendor-autocomplete', ),
    re_path(r'^category-autocomplete/$', CategoryAutocomplete.as_view(), name='category-autocomplete', ),
    re_path(r'^product-autocomplete/$', ProductAutoComplete.as_view(), name='product-autocomplete', ),

    # products vendors
    path('product-vendors/list/', ProductVendorListView.as_view(), name='products_vendors_list'),

    # actions
    path('action/choose-vendor/', action_choose_vendor_view, name='action_choose_vendor')
]
