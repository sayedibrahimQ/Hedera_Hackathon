
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("nilefi.apps.users.urls")),
    path("api/blockchain/", include("nilefi.apps.blockchain.urls")),
]
