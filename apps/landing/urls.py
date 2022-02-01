from django.urls import path
from .views import landing

app_name = 'landing'
urlpatterns = [
    path('', landing, name="index")
]
