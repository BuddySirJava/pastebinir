# urls.py
from django.urls import path
from .views import create_paste, view_encrypted_paste, home

urlpatterns = [
    path('', home, name='home'),
    path('paste/create/', create_paste, name='create_paste'),
    path('paste/<int:paste_id>/', view_encrypted_paste, name='view_encrypted_paste'),
]
