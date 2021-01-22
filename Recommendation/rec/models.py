from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import pathlib
import pickle
from django import forms
from .managers import CustomUserManager


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.
    Uses Django's Postgres ArrayField
    and a MultipleChoiceField for its formfield.
    """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)


category_list = pickle.load(open(str(pathlib.Path().absolute()) + "/Dataset/category_list.pickle", "rb"))
category_tuple = ((),)
for j in category_list:
    category_tuple = category_tuple + ((j, j),)
category_tuple = list(category_tuple)
category_tuple.pop(0)
category_tuple = tuple(category_tuple)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    preference = ChoiceArrayField(
        base_field=models.CharField(max_length=256, choices=category_tuple),
        default=list)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'preference']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class BusinessCity(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BusinessState(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Business(models.Model):
    name = models.CharField(max_length=70)
    business_id = models.CharField(max_length=40, primary_key=True)
    latitude = models.FloatField()
    longtitude = models.FloatField()
    city = models.ManyToManyField(BusinessCity, related_name='businesses')
    state = models.ManyToManyField(BusinessState, related_name='businesses')
    stars = models.DecimalField(max_digits=3, decimal_places=2)
    review_count = models.IntegerField()
    categories = ArrayField(
        base_field=models.CharField(max_length=256),
        default=list)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews',
                                 related_query_name='review')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews', related_query_name='review')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.title
