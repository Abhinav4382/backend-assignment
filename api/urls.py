from django.urls import path
from .views import TotalEmissionsAPI

urlpatterns = [
    path('', TotalEmissionsAPI.as_view(), name='total_emissions'),
]
