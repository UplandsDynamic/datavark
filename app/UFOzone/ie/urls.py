from django.urls import path

from . import views

app_name = "ie"
urlpatterns = [
    path("", views.IEView.as_view(), name="index"),
]
