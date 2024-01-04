from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
import urllib.parse
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.decorators import action
from .throttling import ThreeRequestsPerMinuteThrottle 
from django.db.models import Q
from .pagination import * 

class SignUpView(APIView):
    """
    url = /api/account/signup/
    {
        "email": "akash.sharma@loopmethod.com",
        "password": "test"
    }

    """
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data_serializer = LoginResponceSerializer(user)
        return Response({'data':user_data_serializer.data,'message': "User Created Successfully.  Now perform Login to get your token",},status=status.HTTP_201_CREATED)




from django.db.models import Prefetch
#---------------login API ---------------------------------
class UserLoginView(APIView):
    """
    url = api/account/user/login/
    {
        "email": "akash.sharma@loopmethod.com",
        "password": "test"
    },
    {
        "email": "loopakash7@gmail.com",
        "password": "test"
    }
    """
    serializer_class = TokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = TokenObtainPairSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data
            user = User.objects.get(email=data["email"])
            # Use the UserSerializer to serialize the user data
            user_serializer = LoginResponceSerializer(user)
            return Response({
                "tokens": token,
                "data": user_serializer.data,
                "message": "Login Successfully !!!!!"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"status": 300, "message": "Invalid Login !!!!!!!!!!!!!"})


class UserListView(viewsets.GenericViewSet, ListModelMixin, 
                UpdateModelMixin,RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = LoginResponceSerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter,DjangoFilterBackend]
    search_fields = ['id','first_name','email'] 
    

    def get_serializer_class(self):
        if self.action in ['list']:
            return LoginResponceSerializer
        return LoginResponceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs




class FriendRequestViewSet(viewsets.GenericViewSet, ListModelMixin, 
                UpdateModelMixin,RetrieveModelMixin):
    queryset = Connection.objects.all()
    throttle_classes = [ThreeRequestsPerMinuteThrottle] 
    permission_classes = [IsAuthenticated]
    serializer_class = LoginResponceSerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter,DjangoFilterBackend]
    search_fields = ['id','from_user__first_name','from_user__email']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['list']:
            return ConnectionResponceSerializer
        elif self.action in ['my_request']:
            return ConnectionResponceSerializer
        elif self.action in ['my_friends']:
            return ConnectionResponceSerializer
        elif self.action in ['send_frend_request']:
            return ConnectionResponceSerializer
        elif self.action in ['update_status']:
            return ConnectionSerializer
        return ConnectionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def create(self, request):
        params = request.data.copy()
        from_user = self.request.user.id
        to_user = User.objects.get(email=params.get('to_user'))
        connection = Connection.objects.filter(to_user__email = params.get('to_user'))
        if to_user:
            if not connection:
                    params['from_user'] = from_user
                    params['to_user'] = to_user.id
                    try:
                        serializer = self.get_serializer(data=params)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    except Exception as e:
                        error_message = {"error": str(e)}
                        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({"message": f" You are alreday send request to this user:- {connection}"})
        else:
            return Response({"message": f"User Not Found;{to_user}"})


    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None, **kwargs):
        try:
            connection= super().get_queryset().get(id=pk)
            if request.method == 'PUT':
                data = request.data
                connection.status=data['status']
                serializer = self.get_serializer(connection)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'])
    def my_friends(self, request):
        try:
            to_user = self.request.user
            qs = self.get_queryset().filter(Q(to_user=to_user) | Q(from_user=to_user), status="accepted")
            # Apply search filter
            qs = self.filter_queryset(qs)
            # Paginate the queryset
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = {"error": str(e)}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_request(self, request):
        try:
            to_user = self.request.user
            qs = super().get_queryset()
            qs= qs.filter(to_user = to_user,status="pending")
            # Paginate the queryset
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
                error_message = {"error": str(e)}
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=False, methods=['get'])
    def send_friend_request(self, request):
        try:
            from_user = self.request.user
            qs = super().get_queryset()
            statuss = ["pending","rejected"]
            qs= qs.filter(from_user = from_user,status__in=statuss)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
                error_message = {"error": str(e)}
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)