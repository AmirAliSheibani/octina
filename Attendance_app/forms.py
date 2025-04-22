from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from pricing.models import CustomUser, Vacation, VacationType

# from django_recaptcha.fields import ReCaptchaField
User = CustomUser

from django import forms


class StaffCreateUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری را وارد کنید'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل پرسنل را وارد کنید'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'نام پرسنل را وارد کنید'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'نام خانوادگی پرسنل را وارد کنید'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'رمز عبور را ایجاد کنید'}),
        }

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور را تأیید کنید'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        current_user = self.instance
        if User.objects.filter(username=username).exclude(id=current_user.id).exists():
            raise forms.ValidationError('نام کاربری قبلاً استفاده شده است')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_user = self.instance
        if User.objects.filter(email=email).exclude(id=current_user.id).exists():
            raise forms.ValidationError('ایمیل قبلاً استفاده شده است')
        return email

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if len(password2) < 8:
            raise forms.ValidationError('رمز عبور باید حداقل شامل 8 کاراکتر باشد')
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
        fields = ['work_start_time', 'work_end_time', 'work_days', 'name']


class PositionForm(forms.ModelForm):

    shift_work = forms.ModelMultipleChoiceField(queryset=ShiftWork.objects.none())

    class Meta:
        model = Positions
        fields = ['positions', 'monthly', 'position_income', 'shift_work', 'overtime_position_income']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['shift_work'].queryset = ShiftWork.objects.filter(created_by=request.user)


class ProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.none())
    profile_position = forms.ModelChoiceField(queryset=Positions.objects.none())

    class Meta:
        model = Profile
        fields = ['user', 'profile_position']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(created_who=request.user, possit__isnull=True)
        self.fields['profile_position'].queryset = Positions.objects.filter(created_by=request.user)


class UpdateProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.none())
    profile_position = forms.ModelChoiceField(queryset=Positions.objects.none())

    class Meta:
        model = Profile
        fields = ['user', 'profile_position']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(created_who=request.user)
        self.fields['profile_position'].queryset = Positions.objects.filter(created_by=request.user)


from django import forms
from jalali_date.fields import JalaliDateField, SplitJalaliDateTimeField
from jalali_date.widgets import AdminJalaliDateWidget, AdminSplitJalaliDateTime


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holidays
        fields = ('name', 'date')

    def __init__(self, *args, **kwargs):
        super(HolidayForm, self).__init__(*args, **kwargs)

        self.fields['date'] = JalaliDateField(
            label='تاریخ',
            widget=AdminJalaliDateWidget(attrs={
                'class': 'p-2 border border-gray-300 rounded-xl w-full'
            })
        )

        self.fields['name'].widget.attrs.update({
            'class': 'p-2 border border-gray-300 rounded-xl w-full'
        })


class VacationForm(forms.ModelForm):
    vacation_type = forms.ModelChoiceField(
        queryset=VacationType.objects.all(),
        widget=forms.RadioSelect  # Use RadioSelect widget for single selection
    )

    class Meta:
        model = Vacation
        fields = ['vacation_type', 'reason']
