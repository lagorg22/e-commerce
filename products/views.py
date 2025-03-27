from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from .models import Category, Product 
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

# Custom pagination class for product listing
# Allows clients to specify page size (default: 10, max: 100)
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# API endpoint to retrieve all categories
# Returns a list of all available product categories
@swagger_auto_schema(
    method='GET',
    operation_summary='Get Category Details',
    operation_description='This endpoint will return an Category Details',
    responses={
        status.HTTP_200_OK: CategorySerializer,
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description='Invalid Request',
        )
    }
)
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# API endpoint to retrieve a paginated list of products with filtering and sorting capabilities
# Supports:
# - Search by name/description
# - Filter by category and price
# - Sort by price or creation date
# - Pagination with customizable page size
@swagger_auto_schema(
    method='GET',
    operation_summary='Get Product list with Pagination & Filters',
    operation_description='This endpoint returns a paginated list of products. '
                          'You can filter by category or price, search by name/description, and sort by price or date.',
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search by name or description", type=openapi.TYPE_STRING),
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('price', openapi.IN_QUERY, description="Filter by price", type=openapi.TYPE_NUMBER),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Sort by price or date (e.g., 'price' or '-created_at')", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination", type=openapi.TYPE_INTEGER),
    ],
    responses={200: ProductSerializer(many=True)}
)
@api_view(['GET'])
def product_list(request):
    # Start with all products
    products = Product.objects.all()

    # Apply category filter if specified
    category = request.GET.get('category')
    if category:
        products = products.filter(category__id=category)
    
    # Apply price filter if specified
    price = request.GET.get('price')
    if price:
        products = products.filter(price=price)

    # Apply search filter if specified (searches in both name and description)
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(description__icontains=search_query)

    # Apply sorting (default: newest first)
    ordering = request.GET.get('ordering', '-created_at')
    products = products.order_by(ordering)

    # Apply pagination
    paginator = ProductPagination()
    paginated_products = paginator.paginate_queryset(products, request)

    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)

# API endpoint to create a new product
# Supports multipart form data for image upload
# Requires category selection from existing categories
@swagger_auto_schema(
    method='POST',
    operation_summary='POST product Details',
    operation_description='This endpoint will create a product',
    manual_parameters=[
        openapi.Parameter(
            'image',
            openapi.IN_FORM,
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_FILE)
        ),
        openapi.Parameter(
            'category',
            openapi.IN_FORM,
            description=(
                "Select a category by its ID. Available categories:\n"
                + "\n".join([f"- {c.id}: {c.name}" for c in Category.objects.all()])
            ),
            type=openapi.TYPE_INTEGER,
            enum=[c.id for c in Category.objects.all()]
        )
    ],
    request_body=ProductSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description='Product Created',
            examples={'application/json': {'message': 'Product created successfully'}}
        ),
        status.HTTP_422_UNPROCESSABLE_ENTITY: openapi.Response(
            description='Invalid Request',
            examples={'application/json': {"title": ["This field is required."]}}
        )
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_product(request):
    # Validate and save the product data
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

