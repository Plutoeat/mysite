#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/19 0:33
# @Author  : Joker
# @File    : forms.py
# @Software: PyCharm
import logging

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from accounts.models import Profile
from utils.accounts_utils import verify as verify_code


logger = logging.getLogger(__name__)


class RegisterForm(UserCreationForm):
    """
    注册表单
    """

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("该邮箱已经存在.")
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class LoginForm(AuthenticationForm):
    """
    登录表单
    """

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)


class ForgetPasswordForm(forms.Form):
    """
    忘记密码表单
    """
    new_password1 = forms.CharField(
        label="新密码",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                'placeholder': "密码"
            }
        ),
    )

    new_password2 = forms.CharField(
        label="密码确认",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                'placeholder': "密码确认"
            }
        ),
    )

    email = forms.EmailField(
        label='邮箱',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "邮箱"
            }
        ),
    )

    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "验证码"
            }
        ),
    )

    def clean_new_password2(self):
        password1 = self.data.get("new_password1")
        password2 = self.data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("两次密码不一致")
        password_validation.validate_password(password2)
        return password2

    def clean_email(self):
        user_email = self.cleaned_data.get("email")
        if not get_user_model().objects.filter(
                email=user_email
        ).exists():
            raise ValidationError("未找到邮箱对应的用户")
        return user_email

    def clean_code(self):
        code = self.cleaned_data.get("code")
        verify_code(
            email=self.cleaned_data.get("email"),
            code=code,
        )
        return code


class ForgetPasswordCodeForm(forms.Form):
    """
    忘记密码验证码表单
    """
    email = forms.EmailField(
        label="邮箱号"
    )


class RequireEmailForm(forms.Form):
    """
    补全邮箱表单
    """
    email = forms.EmailField(label='电子邮箱', required=True)
    oauth_id = forms.IntegerField(widget=forms.HiddenInput, required=False)


class UserProfileForm(forms.ModelForm):
    """
    用户个人信息表单
    """
    class Meta:
        model = get_user_model()
        fields = ['nickname', 'email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # 动态添加 Profile 模型的字段
        for field in Profile._meta.fields:
            if field.name in ['avatar', 'gender', 'bio']:
                if field.name == 'avatar':
                    self.fields[field.name] = forms.ImageField(required=False)
                elif hasattr(field, 'required'):
                    self.fields[field.name] = forms.CharField(required=field.required)
                else:
                    self.fields[field.name] = forms.CharField()

