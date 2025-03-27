from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser



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


@swagger_auto_schema(
    method='GET',
    operation_summary='Get Product list',
    operation_description='This endpoint will return a list of products',
    responses={
        status.HTTP_200_OK: ProductSerializer,
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description='Invalid Request',
        )
    }
)
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




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
        )
    ],
    request_body=ProductSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description='Product Created',
            examples={'application/json': {'message': 'Event created successfully'}}
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
    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
