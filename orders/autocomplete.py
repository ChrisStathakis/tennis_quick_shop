from dal import autocomplete
from .models import Order, Payment, Costumer

class CostumerAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Costumer.objects.none()
        
        qs = Costumer.objects.all()
        if self.q:
            qs = Costumer.filters_data(self.request, qs)
        return qs