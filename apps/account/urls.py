from django.urls import path

from .views import author_list_view, author_detail_view

app_name = 'account'
urlpatterns = [
    path("", author_list_view, name="list"),
    path("<slug:id>", author_detail_view, name="detail"),
]
