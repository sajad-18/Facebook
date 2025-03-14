from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls', namespace='home')),
    path('', include('account.urls', namespace='account'))
]
