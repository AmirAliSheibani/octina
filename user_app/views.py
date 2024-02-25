from profile import Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from datetime import datetime, timedelta

from django.utils import timezone

from home.form import EmailSendingForm
# from pricing.models import Profile
from .forms import UserRegisterForm, UserLoginForm, VerifiedEmail, ChangeUserPassowrd, GetUserEmailPass
# from Attendance_app.form import PositionForm
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.mail import send_mail
import random
import string
from pricing.models import CustomUser
from .models import EmailCode

User = CustomUser


def UserRegisterView(request):
    if request.user.is_authenticated:
        return redirect(reverse("home:home"))
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('Email')
            password = form.cleaned_data.get('password2')
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            form.save()

            return redirect(reverse('user:send_email', kwargs={'email': email}))

    else:

        form = UserRegisterForm()
    return render(request, 'user_app/UserRegister.html', {'form': form})


def email_form_context(request, email):
    if request.user.verified_email:
        return redirect(reverse("home:home"))

    user = request.user
    current_time = timezone.now()
    two_minutes_ago = current_time - timezone.timedelta(minutes=2)

    try:
        emailcode = EmailCode.objects.get(user=user)
        if emailcode.created_at < two_minutes_ago:
            emailcode.delete()
            raise EmailCode.DoesNotExist
    except EmailCode.DoesNotExist:
        code = random.randint(1000, 9999)
        emailcode = EmailCode.objects.create(user=user, code=code)

        send_mail(
            subject=f'!{user.username}به اکتینا خوش آمدید ',
            message=f"""
            octina.ir
            کد ورود به سایت :
            {code}
            """,
            from_email='octinaweb@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

    return redirect(reverse('user:verified_email'))


def check_verified_email(request):
    user = request.user
    if user.verified_email == True:
        return redirect(reverse('home:home'))
    current_time = timezone.now()
    two_minutes_ago = current_time - timezone.timedelta(minutes=2)

    try:
        emailcode = EmailCode.objects.get(user=user)
        if emailcode.created_at < two_minutes_ago:
            emailcode.delete()
            raise EmailCode.DoesNotExist
    except EmailCode.DoesNotExist:
        return redirect(reverse('user:send_email', kwargs={'email': user.email}))

    if request.method == 'POST':
        form = VerifiedEmail(request.POST)
        form.request = request
        if form.is_valid():
            code = form.cleaned_data.get('form')
            user.verified_email = True

            print(emailcode.code)
            user.save()
            emailcode.delete()
            return redirect(reverse('home:home'))
    else:
        form = VerifiedEmail()

    return render(request, 'user_app/checkEmail.html', {'form': form})


def UserLoginView(request, ):
    if request.user.is_authenticated:
        return redirect(reverse("home:home"))
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                form.save()
                return redirect(reverse('home:home'))
    else:
        form = UserLoginForm()
    return render(request, 'user_app/UserLogin.html', {'form': form})


def UserLoginView(request, ):
    if request.user.is_authenticated:
        return redirect(reverse("home:home"))
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(reverse("home:home"))
    else:
        form = UserLoginForm()
    return render(request, 'user_app/UserLogin.html', {'form': form})


def GetEmail(request):
    if request.method == "POST":
        form = GetUserEmailPass(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('Email')
            return redirect(reverse('user:send_passcode_email', kwargs={"email": email}))
    else:
        form = GetUserEmailPass()
    return render(request, 'user_app/UserGetEmail.html', {'form': form})


def send_password_code(request, email):
    email = email

    user = User.objects.get(email=email)

    try:
        emailcode = EmailCode.objects.get(user=user)
        emailcode.delete()
        raise EmailCode.DoesNotExist
    except EmailCode.DoesNotExist:
        code = random.randint(1000, 9999)
        emailcode = EmailCode.objects.create(user=user, code=code)

    send_mail(
        subject='تغیر پسورد',
        message=f"""
                octina.ir
                کد برای تغییر پسورد:
                {code}
                
            ----------------
            اگر این درخواست توسط شما انجام نشده نیازی نیست کاری انجام بدید
                """,
        from_email='octinaweb@gmail.com',
        recipient_list=[user.email],
        fail_silently=False,
    )
    return redirect(reverse("user:pass_code", kwargs={"email": email}))


def check_password_code(request, email):
    email = email

    user = User.objects.get(email=email)
    current_time = timezone.now()
    two_minutes_ago = current_time - timezone.timedelta(minutes=2)

    try:
        emailcode = EmailCode.objects.get(user=user)
        if emailcode.created_at < two_minutes_ago:
            emailcode.delete()
            raise EmailCode.DoesNotExist
    except EmailCode.DoesNotExist:
        return redirect(reverse('user:pass_code', kwargs={'email': email}))

    if request.method == 'POST':
        form = VerifiedEmail(request.POST)
        form.request = request
        if form.is_valid():  # check form cleaned_data
            code = form.cleaned_data.get('code')

            user.password = f'{code}{code}'
            user.save()
            print(user.password)
            emailcode.delete()
            return redirect(reverse('user:change_password', kwargs={'email': email, "code": user.password}))
    else:
        form = VerifiedEmail()

    return render(request, 'user_app/checkEmail.html', {'form': form})


def change_password(request, email, code):

    user = User.objects.get(email=email)
    print(user.password)
    if user.password != code:
        return redirect(reverse("home:home"))
    if request.method == "POST":
        form = ChangeUserPassowrd(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password2')
            user.password = password
            user.save()
            return redirect(reverse("user:login"))
    else:
        form = ChangeUserPassowrd()
    return render(request, 'user_app/changePassword.html', {'form': form})


def logoutUser(request):
    user = request.user
    logout(request)
    return redirect(reverse("user:login"))




# -------------------------------------------------------------------------------------


def generate_random_username(length=8):
    letters = string.ascii_letters
    username = ''.join(random.choice(letters) for _ in range(length))
    return username


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def send_staff_user_credentials(email, username, password):
    subject = "Staff User Credentials"
    message = f"Username: {username}\nPassword: {password}"
    from_email = "your_email@example.com"  # Replace with your email address
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def create_staff_user_and_send_credentials(email):
    username = generate_random_username()
    password = generate_random_password()

    user = User.objects.create_user(username=username, password=password)
    user.is_staff = True
    user.save()

    group, _ = Group.objects.get_or_create(name="ssd")
    user.groups.add(group)

    send_staff_user_credentials(email, username, password)
