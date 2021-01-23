# Generated by Django 3.1.3 on 2021-01-23 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import rec.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('preference', rec.models.ChoiceArrayField(base_field=models.CharField(choices=[('Fast Food', 'Fast Food'), ('Nightlife', 'Nightlife'), ('Bars', 'Bars'), ('Sandwiches', 'Sandwiches'), ('American (Traditional)', 'American (Traditional)'), ('Pizza', 'Pizza'), ('Burgers', 'Burgers'), ('Breakfast & Brunch', 'Breakfast & Brunch'), ('Mexican', 'Mexican'), ('Coffee & Tea', 'Coffee & Tea'), ('Italian', 'Italian'), ('American (New)', 'American (New)'), ('Chinese', 'Chinese'), ('Cafes', 'Cafes'), ('Chicken Wings', 'Chicken Wings'), ('Salad', 'Salad'), ('Event Planning & Services', 'Event Planning & Services'), ('Seafood', 'Seafood'), ('Japanese', 'Japanese'), ('Sushi Bars', 'Sushi Bars'), ('Caterers', 'Caterers'), ('Specialty Food', 'Specialty Food'), ('Delis', 'Delis'), ('Bakeries', 'Bakeries'), ('Asian Fusion', 'Asian Fusion'), ('Desserts', 'Desserts'), ('Sports Bars', 'Sports Bars'), ('Canadian (New)', 'Canadian (New)'), ('Barbeque', 'Barbeque'), ('Mediterranean', 'Mediterranean'), ('Steakhouses', 'Steakhouses'), ('Pubs', 'Pubs'), ('Diners', 'Diners'), ('Indian', 'Indian'), ('Thai', 'Thai'), ('Vietnamese', 'Vietnamese'), ('Middle Eastern', 'Middle Eastern'), ('Cocktail Bars', 'Cocktail Bars'), ('Vegetarian', 'Vegetarian'), ('Ice Cream & Frozen Yogurt', 'Ice Cream & Frozen Yogurt'), ('Juice Bars & Smoothies', 'Juice Bars & Smoothies'), ('Soup', 'Soup'), ('Tacos', 'Tacos'), ('Wine & Spirits', 'Wine & Spirits'), ('Beer', 'Beer'), ('Arts & Entertainment', 'Arts & Entertainment'), ('Wine Bars', 'Wine Bars'), ('Vegan', 'Vegan'), ('Gluten-Free', 'Gluten-Free'), ('Comfort Food', 'Comfort Food'), ('Greek', 'Greek'), ('Tex-Mex', 'Tex-Mex'), ('Korean', 'Korean'), ('French', 'French'), ('Chicken Shop', 'Chicken Shop'), ('Lounges', 'Lounges'), ('Ethnic Food', 'Ethnic Food'), ('Buffets', 'Buffets'), ('Food Delivery Services', 'Food Delivery Services'), ('Hot Dogs', 'Hot Dogs'), ('Food Trucks', 'Food Trucks')], max_length=256), default=list, size=None)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('name', models.CharField(max_length=70)),
                ('business_id', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('latitude', models.FloatField()),
                ('longtitude', models.FloatField()),
                ('stars', models.DecimalField(decimal_places=1, max_digits=2)),
                ('review_count', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='BusinessCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessCity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('stars', models.DecimalField(decimal_places=1, max_digits=2)),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', related_query_name='review', to='rec.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', related_query_name='review', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='business',
            name='categories',
            field=models.ManyToManyField(to='rec.BusinessCategory'),
        ),
        migrations.AddField(
            model_name='business',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesses', related_query_name='business', to='rec.businesscity'),
        ),
        migrations.AddField(
            model_name='business',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesses', related_query_name='business', to='rec.businessstate'),
        ),
    ]
