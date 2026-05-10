from django.contrib.auth import password_validation
from store.models import *
from django import forms
import django
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.db import models
from django.db.models import fields
from django.forms import widgets
from django.forms.fields import CharField
from django.utils.translation import gettext, gettext_lazy as _



class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='Имя',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Логин',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = UsernameField(label=_("Логин"),widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label=_("Пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'class':'form-control'}))


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['locality', 'city', 'state']
        labels = {'locality': 'Улица', 'city': 'Город', 'state': 'Область'}
        widgets = {'locality':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Улица'}), 'city':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Город'}), 'state':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Область'})}


class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Текущий пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'auto-focus':True, 'class':'form-control', 'placeholder':'Текущий пароль'}))
    new_password1 = forms.CharField(label=_("Новый пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder':'Новый пароль'}), help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Потверждение пароля"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder':'Подтверждение пароля'}))


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.EmailInput(attrs={'autocomplete':'email', 'class':'form-control'}))


class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("Новый пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control'}), help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Потверждение пароля"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password','class':'form-control'}))

class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Оставьте ваш комментарий...'
            }),
        }
        labels = {
            'content': 'Ваш комментарий'
        }

class NewsCommentEditForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Отредактируйте ваш комментарий...'
            }),
        }
        labels = {'content': 'Текст комментария'}

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(choices=ProductReview.RATING_CHOICES, attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Поделитесь впечатлениями о товаре...'}),
        }
        labels = {'rating': 'Ваша оценка', 'comment': 'Ваш отзыв'}

class ProductReviewEditForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {'rating': 'Оценка', 'comment': 'Ваш отзыв'}