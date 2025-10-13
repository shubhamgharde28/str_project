from django.urls import path
from . import views

urlpatterns = [
    # MonthlyTarget CRUD
    path('targets/', views.target_list, name='target-list'),
    path('targets/create/', views.target_create, name='target-create'),
    path('targets/<int:pk>/update/', views.target_update, name='target-update'),
    path('targets/<int:pk>/delete/', views.target_delete, name='target-delete'),

    # Sale CRUD
    path('sales/', views.sale_list, name='sale-list'),
    path('sales/create/', views.sale_create, name='sale-create'),
    path('sales/<int:pk>/update/', views.sale_update, name='sale-update'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale-delete'),
    path('user/<int:user_id>/target-status/', views.user_target_status, name='user-target-status'),

]
