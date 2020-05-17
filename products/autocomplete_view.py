from dal import autocomplete

from .models import Vendor, Category
from products.models import Product


class VendorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Vendor.objects.none()
        qs = Vendor.objects.all()
        if self.q:
            print('q', self.q.upper())
            qs = qs.filter(title__icontains=self.q.upper())
        return qs


class CategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        print('user', self.request.user)
        if not self.request.user.is_authenticated:
            return Category.objects.none()
        qs = Category.objects.all()
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs


class ProductAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Product.objects.none()
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(title__icontains=self.q)
        return qs