from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    # User Registration and Details
    path('api/users', views.user_create_view, name='user-create'),
    path('api/users/me/', views.user_detail_view, name='user-detail'),

    # Token Authentication (assuming you're using django-rest-framework-simplejwt or similar)
    path('token/login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),

    # Menu Item Views for Customers and Delivery Crew
    path('api/menu-items', views.menu_item_list_view, name='menu-item-list'),
    path('api/menu-items/<int:pk>/', views.menu_item_detail_view, name='menu-item-detail'),

    # Menu Item Views for Managers
    path('api/menu-items/manager', views.manager_menu_item_list_view, name='manager-menu-item-list'),
    path('api/menu-items/manager/<int:pk>/', views.manager_menu_item_detail_view, name='manager-menu-item-detail'),

    # Group Management Views for Managers
    path('api/groups/manager/users', views.group_manager_user_list_view, name='manager-group-user-list'),
    path('api/groups/manager/users/<int:user_id>/', views.group_manager_user_detail_view, name='manager-group-user-detail'),

    # Group Management Views for Delivery Crew
    path('api/groups/delivery-crew/users', views.group_delivery_crew_user_list_view, name='delivery-crew-group-user-list'),
    path('api/groups/delivery-crew/users/<int:user_id>/', views.group_delivery_crew_user_detail_view, name='delivery-crew-group-user-detail'),

    # Cart Management

    path('api/cart/menu-items', views.cart_items_view, name='cart-items'),
    path('api/cart/menu-items/add', views.add_cart_item_view, name='add-cart-item'),
    path('api/cart/menu-items/delete', views.clear_cart_view, name='clear-cart'),

    # Orders Management
    path('api/orders', views.user_orders_view, name='user-orders'),
    path('api/orders/create', views.create_order_view, name='create-order'),
    path('api/orders/<int:order_id>/', views.order_detail_view, name='order-detail'),
    path('api/orders/all', views.all_orders_view, name='all-orders'),
    path('api/orders/<int:order_id>/update', views.update_order_view, name='update-order'),
    path('api/orders/<int:order_id>/delete', views.delete_order_view, name='delete-order'),
    path('api/orders/delivery-crew', views.delivery_crew_orders_view, name='delivery-crew-orders'),
    path('api/orders/<int:order_id>/status', views.update_order_status_view, name='update-order-status'),

]
