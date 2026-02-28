from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls'), name='profiles-urls'),
    path('', include('club.urls'), name='club-urls'),
]
