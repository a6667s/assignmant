import email
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, Value,Max,F
from django_extensions.db.models import TimeStampedModel




class UserManager(BaseUserManager):
    """
        Manager for :model:`account.User` extending from Base User Manager
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.

        Overrides the function from BaseUserManager
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.

        Overrides the function from BaseUserManager
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a super user with the given email and password.

        Overrides the function from BaseUserManager
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class AbstractEmailUser(AbstractUser):
    """
        User Fields:
            * id
            * email
            * first_name
            * phone
            * is_active,
            * is_staff
            * last_login
        Custom User Model extending Django's AbstractUser model
        which updates the following -
            * Makes Email the default Username
            * Discards username

    """
    email = models.EmailField('email address', unique=True)
    
    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    __original_email = None

    def __init__(self, *args, **kwargs):
        super(AbstractEmailUser, self).__init__(*args, **kwargs)
        self.__original_email = self.email

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = True

    def full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()


class User(AbstractEmailUser,TimeStampedModel):
    profile= models.FileField("Profile Pick", upload_to="profile_photo",null=True, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted")
    
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return str(self.get_full_name()) or str(self.email)
        
    @property
    def full_name(self):
        return str(self.get_full_name()) or str(self.email) 



class Connection(TimeStampedModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )

    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        verbose_name = "Connection"
        verbose_name_plural = "Connections"

    def __str__(self):
        return str(self.id)
        
    

    