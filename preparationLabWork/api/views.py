from rest_framework import status, permissions, response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token

from .models import User, Product, Cart, Order
from.serializers import UserRegisterSerializer, UserLogInSerializer, ProductSerializer, CartSerializer, OrderSerializer

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def Register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return response.Response({"data": {"user_token": Token.objects.create(user=user).key}}, status=status.HTTP_201_CREATED)
    return response.Response({"error": {"code": 422, "message": "Нарушение правил валидации", "errors": serializer.errors}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def LogIn(request):
    serializer = UserLogInSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except:
            return response.Response({"error": {"code": 401, "message": "Authentication failed"}}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(serializer.validated_data['password']):
          return response.Response({"error": {"code": 401, "message": "Authentication failed"}}, status=status.HTTP_401_UNAUTHORIZED)
        user, _ = Token.objects.get_or_create(user=user)
        return response.Response({"data": {"user_token": user.key}}, status=status.HTTP_200_OK)
    return response.Response({"error": {"code": 422, "message": "Нарушение правил валидации", "errors": serializer.errors}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LogOut(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        return response.Response({"data": {"message": "logout"}}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ProductView(request):
    product = Product.objects.all()
    serializer = ProductSerializer(product, many=True)
    return response.Response({"body": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ProductAdd(request):
    if not request.user.is_staff:
        return response.Response({"error": {"code": 403, "message": "Нет доступа"}}, status=status.HTTP_403_FORBIDDEN)
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response({"body": {"id": serializer.data['id'], "message": "Product added"}}, status=status.HTTP_201_CREATED)
    return response.Response({"error": {"code": 422, "message": "Нарушение правил валидации", "errors": serializer.errors}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

@api_view(['PATCH', 'DELETE'])
@permission_classes([permissions.IsAdminUser])
def ProductEditDeleteView(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Exception as e:
        return response.Response({"error": {"code": 404, "message": "Не найдено"}}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response({"body": serializer.data}, status=status.HTTP_200_OK)
        return response.Response({"error": {"code": 404, "message": "Не найдено"}}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        product.delete()
        return response.Response({"body": {"message": "Product removed"}}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def CartView(request):
    if request.user.is_staff:
        return response.Response({"error": {"code": 403, "message": "Нет доступа"}}, status=status.HTTP_403_FORBIDDEN)
    cart = Cart.objects.filter(user=request.user)
    for p in cart:
        p.product.id = p.id
    products = [p.product for p in cart]
    return response.Response({"body": ProductSerializer(products, many=True).data}, status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def CartDeleteAdd(request, pk):
    if not request.user.is_staff:
        try:
            products = Product.objects.filter(pk=pk).first()
        except Exception as e:
            return response.Response({"error": {"code": 404, "message": "Не найдено"}}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            try:
                cart = Cart.objects.create(user=request.user, product=products)
            except:
                return response.Response({"error": {"code": 404, "message": "Не найдено"}}, status=status.HTTP_404_NOT_FOUND)
            return response.Response({"body": {"message": "Product add to card"}}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                cart = Cart.objects.get(pk=pk)
            except Exception as e:
                return response.Response({"error": {"code": 404, "message": "Не найдено"}}, status=status.HTTP_404_NOT_FOUND)
            if cart.user != request.user:
                return response.Response({"error": {"code": 403, "message": "Нет доступа"}}, status=status.HTTP_403_FORBIDDEN)
            cart.delete()
            return response.Response({"data": {"message": "Item removed from cart"}}, status=status.HTTP_200_OK)
    return response.Response({"error": {"code": 403, "message": "Нет доступа"}}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def OrderAddView(request):
    if request.user.is_staff:
        return response.Response({"error": {"code": 403, "message": "Нет доступа"}}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return response.Response({"body": serializer.data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        try:
            cart = Cart.objects.filter(user=request.user)
        except Exception as e:
            return response.Response({"error": {"code": 422, "message": "Cart is empty"}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        products = [p.product for p in cart]
        total = sum([p.price for p in products])
        order = Order.objects.create(user=request.user, order_price=total) # _ если этот объект есть, он возвращает False, если нет он его создает и возвращает True
        for p in products:
            order.products.add(p)
        print(order)
        cart.delete()
        return response.Response({"body": OrderSerializer(order).data}, status=status.HTTP_200_OK)

