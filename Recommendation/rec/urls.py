from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results/<str:price_level>/<str:sort_type>/', views.results, name='results'),
    path('results/<str:price_level>/', views.results, name='results'),
    path('results/', views.results, name='results'),
    path('map/', views.show_map, name='map'),
    path('signup/', views.signup, name='signup'),
    path('review/', views.review, name='review'),
    path('apply_review/<str:b_id>/', views.apply_review, name='apply_review'),
    path('apply_review/', views.apply_review, name='apply_review'),
    path('show_directions/<int:b_id>/', views.show_directions, name='show_directions'),
    path('show_business/<str:b_id>/', views.show_business, name='show_business'),
    path('show_profile/', views.show_profile, name='show_profile'),
    path('show_reviews/', views.show_reviews, name='show_reviews'),
]
