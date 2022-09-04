from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first() #мы будем филировать эл.почту пользователя,т.к. почта уникальна

        if user is None: #если пользователь не тот, который нам нужен, то мы вызываем исключение
            raise AuthenticationFailed("Пользователь не найден")

        # if not user.check_password(password): # правильность ввода пароля
        #     raise AuthenticationFailed('Неверный пароль')


# Чтобы создать jwt,нам нужна payload, которая будет иметь след.знач.:
# Первый параметр Id пользователя
# второй параметр: срок действия, здаесь установим вреся, каторое будем показывать, как долго токен будет действовать
# третий параметр: Временная зона
        payload = {
            'id':user.id,
            'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=300),
            'iat':datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')
        responce = Response()
        responce.set_cookie(key='jwt', value=token, httponly= True)
        responce.data={
            'jwt':token
        }
        return responce


# Нам нужно получить фалы куки, а из файла куки получить нашего пользователя
# Поэтому сначала давайте получим токен, который равен запросу файлов куки.
class UserView(APIView):
    def get(self,request):
        token = request.COOKIES.get('jwt')
        # return Response(token)

#Теперь декодируем, чтобы получить данные пользователя. Проверяем на наличие
        if not token:
            raise AuthenticationFailed("Не прошедший проверку подлинности")
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        #Получим user, который равен полученным объектам пользователя

        return Response(serializer.data)


class Logout(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie('jwt')
        response.data={
            'message':'Successfully'
        }
        return response

