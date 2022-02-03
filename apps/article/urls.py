from django.urls import path

from .views import article_list, article_detail

app_name = 'article'

urlpatterns = [
    path('', article_list, name='list'),
    path('<slug:id>', article_detail, name='detail')
]
