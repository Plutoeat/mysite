# Generated by Django 5.0.2 on 2024-07-28 10:11

import accounts.models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthApp',
            fields=[
                ('code', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='代码')),
                ('app_name', models.CharField(max_length=50, verbose_name='app 名称')),
            ],
            options={
                'verbose_name': 'oauth app',
                'verbose_name_plural': 'oauth app',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nickname', models.CharField(blank=True, max_length=100, verbose_name='昵称')),
                ('phone_number', models.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name='电话号码')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('last_login_IP', models.GenericIPAddressField(blank=True, null=True, verbose_name='上次登录IP')),
                ('source', models.CharField(blank=True, max_length=100, verbose_name='注册来源')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'ordering': ['-id'],
                'get_latest_by': 'id',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='OAuthConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=300, verbose_name='应用ID')),
                ('app_key', models.CharField(max_length=300, verbose_name='AppKey')),
                ('app_secret', models.CharField(max_length=300, verbose_name='AppSecret')),
                ('callback_url', models.CharField(default='https://www.baidu.com', max_length=300, verbose_name='回调地址')),
                ('is_enable', models.BooleanField(default=False, verbose_name='是否使用')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('oauth_app', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.oauthapp')),
            ],
            options={
                'verbose_name': 'oauth 配置',
                'verbose_name_plural': 'oauth 配置',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='OAuthUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=50)),
                ('nickname', models.CharField(blank=True, max_length=50, null=True, verbose_name='昵称')),
                ('access_token', models.CharField(blank=True, max_length=300, null=True)),
                ('refresh_token', models.CharField(blank=True, max_length=300, null=True)),
                ('picture', models.CharField(blank=True, max_length=350, null=True)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('metadata', models.TextField(blank=True, null=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('oauth_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.oauthapp', verbose_name='认证 app')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': 'oauth 用户',
                'verbose_name_plural': 'oauth 用户',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(height_field='image_height', upload_to=accounts.models.user_directory_path, verbose_name='头像', width_field='image_width')),
                ('gender', models.IntegerField(blank=True, choices=[(0, '男'), (1, '女'), (2, '外星人')], null=True, verbose_name='性别')),
                ('bio', models.CharField(blank=True, max_length=25, null=True, verbose_name='简介')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='生日')),
                ('image_width', models.IntegerField(blank=True, editable=False, null=True)),
                ('image_height', models.IntegerField(blank=True, editable=False, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '档案',
                'verbose_name_plural': '档案',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='XGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='name')),
                ('permissions', models.ManyToManyField(blank=True, to='auth.permission', verbose_name='permissions')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='accounts.xgroup', verbose_name='groups'),
        ),
    ]