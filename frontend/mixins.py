from django.views.generic.edit import FormMixin
from django.contrib import messages


class MyFormMixin(FormMixin):
    template_name = 'form_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = self.success_url

        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Οι αλλαγές σας Αποθηκεύτηκαν')
        return super().form_valid(form)
