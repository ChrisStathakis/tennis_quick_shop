from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib import messages
from .forms import ActionVendorForm

from products.models import Product, Vendor, ProductVendor


def action_choose_vendor_view(request):
    form = ActionVendorForm(request.POST or None)
    back_url = reverse('edit_product_list')
    ids = request.GET.getlist('choose_product', None)
    for id in ids:
        product = get_object_or_404(Product, id=id)
        print(product.price_buy)

    if form.is_valid():
        vendor = form.cleaned_data.get('vendor')
        ids = request.GET.getlist('choose_product', None)
        print(ids)
        for id in ids:
            product = get_object_or_404(Product, id=id)
            new_link = ProductVendor.objects.create(
                product=product,
                vendor=vendor,
                value=product.price_buy,
                sku=product.sku
            )
            # product.vendors.add(vendor)
            # product.save()
            print(new_link)
        messages.success(request, 'Η πετάβαση πετυχε')
        return redirect(vendor.get_card_url())
    return render(request, 'form_view.html', {'form': form, 'back_url': back_url})
