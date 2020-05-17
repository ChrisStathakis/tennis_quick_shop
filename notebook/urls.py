from django.urls import path
from .views import (NoteHomepageView, validate_new_note_view, NoteUpdateView, pinned_view, delete_note_view,
                    ShowNoteView, TagListView, UpdateTagView, CreateTagView, delete_tag_view
                    )

app_name = 'notes'

urlpatterns = [
    path('', NoteHomepageView.as_view(), name='home'),
    path('pinned/<int:pk>/', pinned_view, name='pinned'),
    path('validate-note-creation/', validate_new_note_view, name='validate_note_creation'),
    path('note/update/<int:pk>/', NoteUpdateView.as_view(), name='note_update'),
    path('note/delete/<int:pk>/', delete_note_view, name="delete_note"),
    path('show-note/<int:pk>/', ShowNoteView.as_view(), name='show_note'),

    path('tag-list/', TagListView.as_view(), name='tag_list'),
    path('tag-create/', CreateTagView.as_view(), name='tag_create'),
    path('tag-update/<int:pk>/', UpdateTagView.as_view(), name='tag_update'),
    path('tag-delete/<int:pk>/', delete_tag_view, name='tag_delete'),
]
