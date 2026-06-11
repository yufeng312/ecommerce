from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/', views.index, name='category_product'),
    path('category/<slug:category>/<slug:product>/', views.product_detail, name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)