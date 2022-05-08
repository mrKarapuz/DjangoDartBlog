from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('category/<slug:slug>/', PostByCategory.as_view(), name='category'),
    path('tag/<slug:slug>/', PostByTag.as_view(), name='tag'),
    path('post/<slug:slug>/', GetPost.as_view(), name='single'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout')
]
