from django.urls import path
from . import views

urlpatterns = [
       path('upload/', views.upload_document, name='upload_document'),
       path('list/', views.document_list, name='document_list'),
       path('<int:document_id>/qa/', views.document_qa, name='document_qa'),
   ]
