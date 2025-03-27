from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializers import ProductSerializer  # To display product details

class CartItemSerializer(serializers.ModelSerializer):
    # Display product details in GET responses.
    product = ProductSerializer(read_only=True)
    # For POST/PUT, accept a product ID.
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        extra_kwargs = {
            'quantity': {'default': 1}
        }

class CartSerializer(serializers.ModelSerializer):
    # Show all items in the cart
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_amount']
        read_only_fields = ['user', 'total_amount']
