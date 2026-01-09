from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Autenticación
    path('auth/registro/', views.RegistroView.as_view(), name='registro'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Denuncias
    path('denuncias/generar/', views.generar_denuncia_view, name='generar_denuncia'),
    path('denuncias/', views.listar_denuncias_view, name='listar_denuncias'),
]
