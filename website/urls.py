# urls.py
from django.conf.urls import handler404
from django.urls import path
from .views import create_paste, view_encrypted_paste, history, err404, about

urlpatterns = [
    path('', create_paste, name='create_paste'),
    path('history/', history, name='history'),
    path('about/',about , name='about'),

    path('<str:paste_id>/', view_encrypted_paste, name='view_encrypted_paste'),

]
handler404 = err404

