from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
    path('map/', views.show_map, name='map'),
    path('signup/', views.signup, name='signup'),
    path('review/', views.review, name='review'),
]
