from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LogIn),
    path('signup/', Register),
    path('logout/', LogOut.as_view()),
    path('products/', ProductView),
    path('product/', ProductAdd),
    path('product/<int:pk>/', ProductEditDeleteView),
    path('cart/', CartView),
    path('cart/<int:pk>/', CartDeleteAdd),
    path('order/', OrderAddView),
]