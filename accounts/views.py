from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model

from accounts.forms import UserLoginForm, UserRegForm, UserUpdateForm, ContactForm

from django.contrib import messages

import datetime as dt
from scraper.models import Vacancy, Error, Url, City, Language

User = get_user_model()


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        email = data['email']
        password = data['password']
        user = authenticate(request, email=email, password=password)
        login(request, user)
        # Redirect to a success page.
        return redirect("home")

    context = {"form": form}
    return render(request, "accounts/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def register_view(request):
    form = UserRegForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data["password"])
        new_user.save()
        messages.success(request, "Пользователь зарегистрирован")
        context = {"new_user": new_user}
        return render(request, "accounts/register_done.html", context)
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def update_view(request):
    contact_form = ContactForm()
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = UserUpdateForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user.city = data["city"]
                user.language = data["language"]
                user.send_email = data["send_email"]
                user.save()
                messages.success(request, "Настройки успешно изменены")
                return redirect("accounts:update")
        else:
            form = UserUpdateForm(initial={"city": user.city, "language": user.language,
                                           "send_email": user.send_email})
            context = {"form": form, "contact_form": contact_form}
            return render(request, "accounts/update.html", context)
    else:
        return redirect("accounts:login")


def delete_view(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            qs = User.objects.get(pk=user.pk)
            qs.delete()
            messages.error(request, 'Ваш аккаунт удален.')
    return redirect("home")


def contact_view(request):
    if request.method == "POST":
        contact_form = ContactForm(request.POST or None)
        if contact_form.is_valid():
            data = contact_form.cleaned_data
            city = data.get("city")
            language = data.get("language")
            email = data.get("email")
            qs = Error.objects.filter(timestamp=dt.date.today())
            if qs.exists():
                err = qs.first()
                data = err.data.get("user_data", [])
                data.append({"city": city, "language": language, "email": email})
                err.data["user_data"] = data
                err.save()
            else:
                data = [{"city": city, "language": language, "email": email}]
                Error(data=f"user_data:{data}").save()
            messages.success(request, 'Данные отправлены')
            return redirect("accounts:update")
        else:
            return redirect("accounts:update")
    else:
        return redirect("accounts:login")
