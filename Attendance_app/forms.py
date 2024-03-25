from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from pricing.models import CustomUser, Vacation, VacationType

# from django_recaptcha.fields import ReCaptchaField
User = CustomUser


class StaffCreateUser(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'نام کاربری را وارد کنید'}))
    Email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'ایمیل پرسنل را وارد کنید'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'نام پرسنل را وارد کنید'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'نام خانوادگی پرسنل را وارد کنید'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور را ایجاد کنید'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور را تأیید کنید'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('نام کاربری قبلاً استفاده شده است')
        return username

    def clean_Email(self):
        email = self.cleaned_data.get('Email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('ایمیل قبلاً استفاده شده است')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد")
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if len(password2) < 8:
            return password2
        else:
            if password != password2:
                raise forms.ValidationError('رمز عبورها مطابقت ندارند')
        return password2


from pricing.models import ShiftWork, Day, Positions, Profile, Holidays

from django.forms import TimeInput, CheckboxSelectMultiple, CheckboxSelectMultiple, SelectMultiple


class ShiftWorkForm(forms.ModelForm):
    work_start_time = forms.TimeField(widget=TimeInput(attrs={'type': 'time'}))
    work_end_time = forms.TimeField(widget=TimeInput(attrs={'type': 'time'}))
    work_days = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=CheckboxSelectMultiple,
    )

    class Meta:
        model = ShiftWork
        fields = ['work_start_time', 'work_end_time', 'work_days']


class PositionForm(forms.ModelForm):
    work_days = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),

    )
    shift_work = forms.ModelMultipleChoiceField(
        queryset=ShiftWork.objects.all(),

    )

    class Meta:
        model = Positions
        fields = ['positions', 'position_income', 'work_days', 'shift_work', 'overtime_position_income']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'profile_position']


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holidays
        fields = ['date', 'name']

class VacationForm(forms.ModelForm):
    vacation_type = forms.ModelChoiceField(
        queryset=VacationType.objects.all(),
        widget=forms.RadioSelect  # Use RadioSelect widget for single selection
    )

    class Meta:
        model = Vacation
        fields = ['vacation_type', 'time2', 'reason']


