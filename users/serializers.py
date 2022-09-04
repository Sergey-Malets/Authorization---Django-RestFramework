from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password']
        extra_kwargs = { #дополнительные аргументы , чтобы убрать возвращение пароля
            "password": {"write_only": True}
        }

        def create(self, validated_data): #функция для хэширования пароля
            password = validated_data.pop("password",None) #извлечение пароля
            instance = self.Meta.model(**validated_data) #создаём пользователя как экземпляр, что бы он был равен модели Мета и давал проверенные данные
            if password is not None:
                instance.set_password(password)#если пароль не равен нулю создаём для него пароль
            instance.save()
            return instance #возвращаем экземпляр
