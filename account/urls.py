from django.urls import path, include
from .views import *
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register("users",UserListView, basename='user'),
router.register("connections",FriendRequestViewSet, basename='connection')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(),name="Login"),
    
    
    
]
app_name = 'account'