from django.shortcuts import render, reverse, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from django_tables2 import RequestConfig

from .models import Tags, NoteBook
from .forms import NotebookForm, TagForm
from .tables import TagsTable


@method_decorator(staff_member_required, name='dispatch')
class NoteHomepageView(ListView):
    template_name = 'notes/homepage.html'
    model = NoteBook
    
    def get_queryset(self):
        qs = NoteBook.objects.all()
        qs = NoteBook.filters_data(self.request, qs)
        return qs

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = NotebookForm()
        context['pinned_qs'] = self.object_list.filter(pinned=True)
        context['qs'] = self.object_list.filter(pinned=False)[:30]
        return context


@staff_member_required
def validate_new_note_view(request):
    form = NotebookForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New message added')
    return redirect(reverse('notes:home'))


@method_decorator(staff_member_required, name='dispatch')
class NoteUpdateView(UpdateView):
    form_class = NotebookForm
    success_url = reverse_lazy('notes:home')
    template_name = 'notes/form.html'
    model = NoteBook

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['page_title'] = f'Επεξεργασια {self.object.title}'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'Η σημειωση ανανεώθηκε!')
        return super().form_valid(form)


@staff_member_required
def pinned_view(request, pk):
    instance = get_object_or_404(NoteBook, id=pk)
    instance.pinned = False if instance.pinned else True
    instance.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'), reverse('notes:home'))


@staff_member_required
def delete_note_view(request, pk):
    instance = get_object_or_404(NoteBook, id=pk)
    instance.delete()
    messages.warning(request, 'Διαγραφηκε')
    return redirect(reverse('notes:home'))


@method_decorator(staff_member_required, name='dispatch')
class ShowNoteView(DetailView):
    template_name = 'notes/note_show.html'
    model = NoteBook


@method_decorator(staff_member_required, name='dispatch')
class TagListView(ListView):
    template_name = 'list_view.html'
    model = Tags
    paginate_by = 100

    def get_queryset(self):
        qs = Tags.objects.all()
        qs = Tags.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        queryset_table = TagsTable(self.object_list)
        RequestConfig(self.request, {'per_page': self.paginate_by}).configure(queryset_table)
        create_url = reverse('notes:tag_create')
        back_url = reverse('notes:home')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateTagView(CreateView):
    model = Tags
    form_class = TagForm
    template_name = 'form_view.html'
    success_url = reverse_lazy('notes:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Δημιουργία Tag'
        back_url = self.success_url
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νέο Tag Προστέθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class UpdateTagView(UpdateView):
    model = Tags
    form_class = TagForm
    template_name = 'form_view.html'
    success_url = reverse_lazy('notes:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Επεξεργασια Tag {self.object.title}'
        back_url = self.success_url
        delete_url = self.object.get_delete_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Ανανέωση Επιτυχής!')
        return super().form_valid(form)


@staff_member_required
def delete_tag_view(request, pk):
    instance = get_object_or_404(Tags, id=pk)
    instance.delete()
    messages.warning(request, 'To Tag διαγραφηκε')
    return redirect('notes:tag_list')