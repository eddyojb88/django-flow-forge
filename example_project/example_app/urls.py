from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('trigger_data_science_proj1', views.trigger_data_science_proj1, name='trigger-data-science-proj1'),
]
