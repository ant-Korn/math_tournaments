from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'birth_date', 'phone', 
                  'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'birth_date',
                  'first_name', 'last_name', 'phone',
                  'is_active', 'is_superuser')

    def clean_password(self):
        return self.initial["password"]

class MyUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'birth_date', 'first_name',
                    'last_name', 'phone', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
            (None, {'fields': ('email', 'password')}),
            ('Personal info', {'fields': ('birth_date',
                                          'first_name',
                                          'last_name',
                                          'phone',)
                              }
            ),
            ('Permissions', {'fields': ('is_superuser', 'groups',)}),
    )

    add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('email', 'birth_date', 'password1', 'password2')}
            ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, MyUserAdmin)
