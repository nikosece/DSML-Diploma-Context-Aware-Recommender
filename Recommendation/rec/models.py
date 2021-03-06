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


class BusinessCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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


category_list = [i.name for i in list(BusinessCategory.objects.all())]
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
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BusinessIcon(models.Model):
    name = models.CharField(max_length=220)

    def __str__(self):
        return self.name


class BusinessPrice(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BusinessDays(models.Model):
    monday = models.CharField(max_length=100, default='NA')
    tuesday = models.CharField(max_length=100, default='NA')
    wednesday = models.CharField(max_length=100, default='NA')
    thursday = models.CharField(max_length=100, default='NA')
    friday = models.CharField(max_length=100, default='NA')
    saturday = models.CharField(max_length=100, default='NA')
    sunday = models.CharField(max_length=100, default='NA')

    def __str__(self):
        return 'Nothing to show'


class BusinessPhoto(models.Model):
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    html_attributions = models.CharField(max_length=220)
    photo_reference = models.CharField(max_length=220)

    def __str__(self):
        return 'Nothing to show'


class Business(models.Model):
    name = models.CharField(max_length=140)
    address = models.CharField(max_length=220)
    icon = models.ForeignKey(BusinessIcon, on_delete=models.CASCADE, related_name='businesses',
                             related_query_name='business')
    price_level = models.ForeignKey(BusinessPrice, on_delete=models.CASCADE, related_name='businesses',
                                    related_query_name='business')
    business_id = models.CharField(max_length=70, primary_key=True)
    latitude = models.FloatField()
    longtitude = models.FloatField()
    city = models.ForeignKey(BusinessCity, on_delete=models.CASCADE, related_name='businesses',
                             related_query_name='business')

    stars = models.DecimalField(max_digits=2, decimal_places=1)
    review_count = models.PositiveSmallIntegerField()
    categories = models.ManyToManyField(BusinessCategory)
    photo = models.OneToOneField(BusinessPhoto, on_delete=models.CASCADE, )
    days = models.ForeignKey(BusinessDays, on_delete=models.CASCADE, related_name='businesses',
                             related_query_name='business', null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews',
                                 related_query_name='review')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews', related_query_name='review')
    stars = models.DecimalField(max_digits=2, decimal_places=1, )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
