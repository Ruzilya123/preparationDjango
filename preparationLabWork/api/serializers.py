from rest_framework import serializers

from .models import User, Product, Cart, Order


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
      model = User
      fields = ['fio', 'email', 'password']

    def save(self, **kwargs):
      user = User(
          fio=self.validated_data['fio'],
          email=self.validated_data['email'],
          username=self.validated_data['fio'],
      )
      user.set_password(self.validated_data['password'])
      user.save()
      return user


class UserLogInSerializer(serializers.Serializer):
   email = serializers.EmailField()
   password = serializers.CharField()

class ProductSerializer(serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
   products = ProductSerializer(many=True)
   class Meta:
      model = Cart
      fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
   products = ProductSerializer(many=True)
   class Meta:
      model = Order
      fields = '__all__' 
