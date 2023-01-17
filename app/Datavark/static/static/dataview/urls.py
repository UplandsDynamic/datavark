from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "dataview"
urlpatterns = [
    path("", views.ReportsView.as_view(), name="reports-view"),
    path("<int:id>", views.DetailView.as_view(), name="detail-view"),
    path("export", views.DataExportView.as_view(), name="data-export-view"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
