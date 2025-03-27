from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

# Add an item to the cart.
@swagger_auto_schema(
    method='POST',
    operation_summary='Add item to cart',
    operation_description="Adds a product to the current user's cart. If the product already exists, increments its quantity.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['product_id'],
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the product to add to cart'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity to add (default: 1)')
        }
    ),
    responses={
        201: CartItemSerializer,
        400: "Bad Request - Invalid data or insufficient stock",
        404: "Not Found - Product not found",
        401: "Unauthorized - Authentication required"
    }
)
@api_view(['POST'])
@parser_classes([JSONParser])
def add_to_cart(request):
    user = request.user
    if user.is_anonymous:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    # Retrieve (or create) the user's cart.
    cart, created = Cart.objects.get_or_create(user=user)

    # Validate input data
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    if not product_id:
        return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate that quantity is positive
    if quantity <= 0:
        return Response({"detail": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if this product is already in the cart.
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product, 
        defaults={'quantity': 0}  # Start with 0 and increment below
    )
    
    # Calculate new quantity
    new_quantity = cart_item.quantity + quantity
    
    # Check if enough stock is available
    if new_quantity > product.stock:
        available = product.stock - cart_item.quantity
        if available <= 0:
            return Response(
                {"detail": f"Product '{product.name}' is out of stock."},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"detail": f"Cannot add {quantity} more units of '{product.name}'. Only {available} more units available."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Update quantity
    cart_item.quantity = new_quantity
    cart_item.save()
    
    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

# View all items in the cart.
@swagger_auto_schema(
    method='GET',
    operation_summary='View cart',
    operation_description="Retrieves all items in the current user's cart.",
    responses={200: CartSerializer}
)
@api_view(['GET'])
def view_cart(request):
    user = request.user
    if user.is_anonymous:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({"detail": "Cart is empty."}, status=status.HTTP_200_OK)
    
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Remove an item from the cart.
@swagger_auto_schema(
    method='DELETE',
    operation_summary='Remove item from cart',
    operation_description='Removes a specific item from the cart using its ID.',
    manual_parameters=[
        openapi.Parameter('cart_item_id', openapi.IN_PATH, description="ID of the cart item", type=openapi.TYPE_INTEGER)
    ],
    responses={204: 'No Content'}
)
@api_view(['DELETE'])
def remove_from_cart(request, cart_item_id):
    user = request.user
    if user.is_anonymous:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        cart = Cart.objects.get(user=user)
        cart_item = CartItem.objects.get(cart=cart, id=cart_item_id)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
    
    cart_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
