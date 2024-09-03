from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


# Create your views here.
@login_required(login_url="login")
def index(request):
    return render(request, "index.html")


# @login_required(login_url="login")
@csrf_exempt  # this is avoiding required csrf_token
def generate_blog(request):
    """Automated generate a blog article"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # get body of json file, which fetched in script in index.html
            ytb_link = data["link"]
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid data sent."}, status=400)


    else:
        return JsonResponse({"error": "Method is not valid."}, status=405)  # prevent user to use different methods except POST


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            error_message = "Invalid username or password"
            return render(request, "login.html", {"error_message": error_message})

    return render(request, "login.html")


def user_signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]

        if password == confirm_password:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect("/")
            except Exception as ex:  # maybe this account have been taken
                error_message = "Error creating account"
                return render(request, "signup.html", {"error_message": error_message})

        else:
            error_message = "Passwords don't match!"
            return render(request, "signup.html", {"error_message": error_message})

    return render(request, "signup.html")


def user_logout(request):
    logout(request)
    return redirect("/login")
