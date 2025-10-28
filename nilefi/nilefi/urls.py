from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('nilefi.apps.accounts.urls')),
    path('api/blockchain/', include('nilefi.apps.blockchain.urls')),
    path('api/funding/', include('nilefi.apps.funding.urls')),
]
