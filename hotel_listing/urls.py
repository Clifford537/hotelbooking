from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path("book/<int:room_id>/", views.book_room, name="book_room"),
]
