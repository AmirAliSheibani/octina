from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import UserProfile
from pricing.models import CustomUser
from .models import EmailCode
# from django_recaptcha.fields import ReCaptchaField
User = CustomUser






class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری را وارد کنید'}),
            'Email': forms.EmailInput(attrs={'placeholder': 'ایمیل خود را وارد کنید'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'رمز عبور را ایجاد کنید'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'رمز عبور را تأیید کنید'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('نام کاربری قبلاً استفاده شده است')
        return username

    def clean_Email(self):
        email = self.cleaned_data.get('Email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('ایمیل قبلاً استفاده شده است')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد")
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if len(password2) < 8:
            return password2
        else:
            if password != password2:
                raise ValidationError('رمز عبورها مطابقت ندارند')
        return password2


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری', 'class': 'input100'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'رمز عبور', 'class': 'input100'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            return cleaned_data
        else:
            raise forms.ValidationError('نام کاربری یا رمز عبور اشتباه است')


class VerifiedEmail(forms.ModelForm):
    class Meta:
        model = EmailCode
        fields = ('code',)
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'کد را وارد کنید'}),
        }


    def clean_code(self):
        code = self.cleaned_data.get('code')
        try:
            emailcode = EmailCode.objects.get(code=code)
            return code
        except:
            raise ValidationError('کد وارد شده اشتباه است')


class ChangeUserPassowrd(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'تأیید رمز عبور جدید'}))

    class Meta:
        model = User
        fields = ('password', 'password2')

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if len(password2) < 8:
            return password2
        else:
            if password != password2:
                raise forms.ValidationError('رمز عبورها مطابقت ندارند')
        return password2





class GetUserEmailPass(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'Email')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری را وارد کنید'}),
            'Email': forms.EmailInput(attrs={'placeholder': 'ایمیل خود را وارد کنید'})
        }


    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        Email = self.cleaned_data['Email']

        try:
            User.objects.get(username=username, email=Email)
            return cleaned_data
        except:
            raise forms.ValidationError('کاربری با این مشخصات وجود ندارد')
