from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderItemSerializer
from cart.models import Cart, CartItem
from django.db import transaction

# Create your views here.

@swagger_auto_schema(
    method='GET',
    operation_summary='List user orders',
    operation_description='Retrieves all orders made by the current user.',
    responses={
        200: OrderSerializer(many=True),
        401: "Unauthorized - Authentication required"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    """
    List all orders for the current user
    """
    # Only show non-cancelled orders
    orders = Order.objects.filter(user=request.user).exclude(status='CANCELLED')
    
    # Ensure all orders have correct total_amount (only if needed in case of legacy data)
    for order in orders:
        if order.total_amount == 0:
            order.recalculate_total()
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_summary='Get order details',
    operation_description='Retrieves details of a specific order including all order items.',
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, description="ID of the order", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: OrderSerializer,
        404: "Not Found - Order not found",
        401: "Unauthorized - Authentication required"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Retrieve details of a specific order
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        # Check if order has been cancelled
        if order.status == 'CANCELLED':
            return Response({"detail": "This order has been cancelled."}, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure the order has correct total_amount (only if needed in case of legacy data)
        if order.total_amount == 0:
            order.recalculate_total()
            
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_summary='Create new order',
    operation_description='Creates a new order from the current cart and clears the cart. Total amount is taken from the cart and deducted from user balance.',
    request_body=OrderCreateSerializer,
    responses={
        201: OrderSerializer,
        400: "Bad Request - Invalid data, empty cart, or insufficient balance",
        401: "Unauthorized - Authentication required"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create a new order from the current cart.
    Total amount is taken from the cart and deducted from user's balance.
    """
    user = request.user

    # Admin users cannot place orders
    if user.is_staff:
        return Response(
            {"detail": "Admin users cannot place orders."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if cart exists and has items
    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            return Response(
                {"detail": "Your cart is empty. Please add items to your cart before placing an order."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Cart.DoesNotExist:
        return Response(
            {"detail": "Your cart is empty. Please add items to your cart before placing an order."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user has sufficient balance
    if not hasattr(user, 'profile') or user.profile.balance is None or user.profile.balance < cart.total_amount:
        return Response(
            {"detail": f"Insufficient balance. Your balance: {user.profile.balance if hasattr(user, 'profile') and user.profile.balance is not None else '0.00'}, Order total: {cart.total_amount}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate order shipping data
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        with transaction.atomic():
            # Create the order using the cart's total amount
            order = serializer.save(total_amount=cart.total_amount)
            
            # Create order items from cart items
            for cart_item in cart_items:
                # Check if there's enough stock
                if cart_item.quantity > cart_item.product.stock:
                    return Response({
                        "detail": f"Not enough stock for '{cart_item.product.name}'. Available: {cart_item.product.stock}"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Ensure the total_amount is correct based on the actual items
            order.recalculate_total()
            
            # Deduct the total from user's balance
            if not user.profile.withdraw(order.total_amount):
                raise Exception("Failed to withdraw funds from user balance")
            
            # Clear the cart
            cart_items.delete()
            # Reset cart total to zero after emptying
            cart.total_amount = 0
            cart.save()
            
            # Fetch the order with updated total_amount
            order.refresh_from_db()
            
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='DELETE',
    operation_summary='Cancel order',
    operation_description='Cancels an order if it has not been shipped yet and refunds the amount to user balance.',
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, description="ID of the order", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(
            description="Order cancelled successfully",
            examples={'application/json': {'detail': 'Order cancelled successfully. Amount refunded: 50.00'}}
        ),
        400: "Bad Request - Order cannot be cancelled",
        404: "Not Found - Order not found",
        401: "Unauthorized - Authentication required"
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """
    Cancel an order if it hasn't been shipped yet
    Returns items to inventory and refunds amount to user balance
    """
    user = request.user
    
    # Admin users cannot cancel orders (they shouldn't have orders)
    if user.is_staff:
        return Response({"detail": "Admin users do not have orders to cancel."}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if order is already cancelled
    if order.status == 'CANCELLED':
        return Response({"detail": "Order is already cancelled."}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    # Check if order can be cancelled
    if order.status in ['SHIPPED', 'DELIVERED']:
        return Response({"detail": "Cannot cancel an order that has been shipped or delivered."}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    with transaction.atomic():
        # Return items to inventory
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.product.stock += item.quantity
            item.product.save()
        
        # Ensure the total_amount is correct before refunding
        if order.total_amount == 0:
            order.recalculate_total()
        
        # Refund to user's balance
        refund_amount = order.total_amount
        refund_description = f"Refund for cancelled order #{order.id}"
        
        # Refund the amount to user's balance
        if not user.profile.refund(refund_amount, refund_description):
            return Response(
                {"detail": "Failed to process refund."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update order status
        order.status = 'CANCELLED'
        order.save()
    
    return Response(
        {"detail": f"Order cancelled successfully. Amount refunded: {refund_amount}"},
        status=status.HTTP_200_OK
    )
