import logging
from gettext import ngettext

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UsernameField, ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from accounts.models import User, OAuthApp, OAuthConfig, OAuthUser, Profile, XGroup

logger = logging.getLogger(__name__)
# Register your models here.


admin.site.unregister(Group)


class UserCreationForm(forms.ModelForm):
    """
    admin 新增表单
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不一致")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.source = "admin"
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    admin 修改表单
    """
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = "__all__"
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format(
                f"../../{self.instance.pk}/password/"
            )
        user_permissions = self.fields.get("user_permissions")
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related(
                "content_type"
            )


class ProfileInline(admin.StackedInline):
    """
    将 Profile 嵌入到 User 后台中
    """
    model = Profile


class OAuthConfigInline(admin.StackedInline):
    """
    将 OAuthConfig 嵌入到 OAuthApp中
    """
    model = OAuthConfig


class OAuthUserInline(admin.StackedInline):
    """
    将OAuthUser 嵌入到 User 中去
    """
    model = OAuthUser


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    User 后台
    """
    form = UserChangeForm
    add_form = UserCreationForm
    inlines = [ProfileInline, OAuthUserInline]
    list_display = ['username', 'email', 'avatar_tag', 'is_active', 'is_staff', 'last_login']
    search_fields = ("username", "first_name", "last_name", "email", "phone_number")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    fieldsets = [
        (None, {"fields": ["username", "email", "phone_number", "password", "source"]}),
        ("用户信息", {"fields": ["first_name", "last_name", "nickname"]}),
        ("用户状态", {"fields": ["is_active", "date_joined", "last_login", "last_login_IP"]}),
        ("用户权限", {"fields": ["is_staff", "is_superuser", "groups", "user_permissions"]}),
    ]

    actions = ["make_active", "make_not_active"]

    @admin.display(description="头像")
    def avatar_tag(self, obj):
        """
        在 admin 中显示头像
        :return:
        """
        return format_html(
            '<a href="/media/{}"><img src="/media/{}" width=15 height=15 /></a>',
            obj.profile_set.avatar,
            obj.profile_set.avatar
        )

    @admin.action(description="选中用户活跃")
    def make_active(self, request, queryset):
        active = queryset.update(is_active=True)
        self.message_user(
            request,
            ngettext(
                "%d 个用户成功活跃",
                "%d 个用户成功活跃",
                active
            ) % active,
            messages.SUCCESS
        )

    @admin.action(description="选中用户不活跃")
    def make_not_active(self, request, queryset):
        not_active = queryset.update(is_active=False)
        self.message_user(
            request,
            ngettext(
                "%d 个用户成功取消活跃",
                "%d 个用户成功取消活跃",
                not_active
            ) % not_active,
            messages.SUCCESS
        )


@admin.register(XGroup)
class GroupAdmin(admin.ModelAdmin):
    """
    注册 Group 的后台，对应模型是 XGroup
    """
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("permissions",)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "permissions":
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            kwargs["queryset"] = qs.select_related("content_type")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)


@admin.register(OAuthApp)
class OAuthAppAdmin(admin.ModelAdmin):
    """
    OAuth App 后台
    """
    inlines = [OAuthConfigInline]
    list_display = ['code', 'app_name', 'is_enabled']

    @admin.display(description="oauth配置状态")
    def is_enabled(self, obj):
        """
        oauth配置状态
        """
        if obj.oauthconfig.is_enable:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')


@admin.register(OAuthConfig)
class OAuthConfigAdmin(admin.ModelAdmin):
    """
    OAuthConfig 的后台
    """
    list_display = ['oauth_app', 'app_key', 'app_secret', 'is_enable']
    list_filter = ['oauth_app']


@admin.register(OAuthUser)
class OAuthUserAdmin(admin.ModelAdmin):
    """
    OAuthUser 的后台
    """
    search_fields = ['nickname']
    list_per_page = 20
    list_display = ['id', 'nickname', 'link_to_user_model', 'show_user_image', 'oauth_app']
    list_filter = ['user', 'oauth_app']
    list_display_links = ['id', 'nickname']

    @admin.display(description="用户")
    def link_to_user_model(self, obj):
        if obj.user:
            info = (obj.user.get_meta_data().app_label, obj.user.get_meta_data().model_name)
            link = reverse("admin:%s_%s_change" % info, args=(obj.user.id,))
            return format_html(
                '<a href="{}">{}</a>',
                link,
                obj.nickname if obj.user.nickname else obj.user.email
            )

    @admin.display(description="用户头像")
    def show_user_image(self, obj):
        return format_html(
            '<a href="{}"><img src="{}" width=15 height=15 /></a>',
            obj.picture,
            obj.picture
        )
