from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

# User Registration View
@api_view(['POST'])
def user_create_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if username and password and email:
        User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

# User Detail View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# Menu Item Views for Customers and Delivery Crew
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def menu_item_list_view(request):
    menu_items = MenuItem.objects.all()
    serializer = MenuItemSerializer(menu_items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def menu_item_detail_view(request, pk):
    menu_item = get_object_or_404(MenuItem, pk=pk)
    serializer = MenuItemSerializer(menu_item)
    return Response(serializer.data)

# Menu Item Views for Managers
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manager_menu_item_list_view(request):
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        menu_items = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manager_menu_item_detail_view(request, pk):
    menu_item = get_object_or_404(MenuItem, pk=pk)

    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = MenuItemSerializer(menu_item, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        menu_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Group Views for Managers
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_manager_user_list_view(request):
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    manager_group = Group.objects.get(name='Manager')

    if request.method == 'GET':
        managers = manager_group.user_set.all()
        return Response([user.username for user in managers])

    elif request.method == 'POST':
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            manager_group.user_set.add(user)
            return Response({'message': 'User added to manager group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def group_manager_user_detail_view(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
        manager_group = Group.objects.get(name='Manager')
        manager_group.user_set.remove(user)
        return Response({'message': 'User removed from manager group'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Group Views for Delivery Crew
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_delivery_crew_user_list_view(request):
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    delivery_crew_group = Group.objects.get(name='Delivery crew')

    if request.method == 'GET':
        delivery_crew = delivery_crew_group.user_set.all()
        return Response([user.username for user in delivery_crew])

    elif request.method == 'POST':
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            delivery_crew_group.user_set.add(user)
            return Response({'message': 'User added to delivery crew group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def group_delivery_crew_user_detail_view(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
        delivery_crew_group = Group.objects.get(name='Delivery crew')
        delivery_crew_group.user_set.remove(user)
        return Response({'message': 'User removed from delivery crew group'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Cart Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_items_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_cart_item_view(request):
    serializer = CartSerializer(data=request.data)
    if serializer.is_valid():
        menu_item = serializer.validated_data.get('menuitem')
        quantity = serializer.validated_data.get('quantity', 1)
        cart_item, created = Cart.objects.get_or_create(user=request.user, menuitem=menu_item)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()
        return Response({'message': 'Item added to cart successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart_view(request):
    Cart.objects.filter(user=request.user).delete()
    return Response({'message': 'All items removed from cart'}, status=status.HTTP_204_NO_CONTENT)

# Order Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders_view(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(user=request.user, date=datetime.date.today())
    order_items = [
        OrderItem(
            order=order,
            menuitem=item.menuitem,
            quantity=item.quantity,
            price=item.price
        )
        for item in cart_items
    ]
    OrderItem.objects.bulk_create(order_items)
    cart_items.delete()  # Clear cart after creating order

    return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_orders_view(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if 'status' in request.data:
        order.status = request.data['status']
    if 'delivery_crew' in request.data:
        delivery_crew_id = request.data['delivery_crew']
        delivery_crew = get_object_or_404(User, id=delivery_crew_id)
        order.delivery_crew = delivery_crew
    
    order.save()
    return Response({'message': 'Order updated successfully'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delivery_crew_orders_view(request):
    orders = Order.objects.filter(delivery_crew=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_crew=request.user)
    if 'status' in request.data:
        order.status = request.data['status']
        order.save()
        return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)
    return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)