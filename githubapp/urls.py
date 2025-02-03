from django.urls import path
from .views import github_user_search

urlpatterns = [
    path('', github_user_search, name='github_search'),
]
