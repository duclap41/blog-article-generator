from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
class UserAuthor:
    @login_required(login_url="login")
    @staticmethod
    def index(request):
        return render(request, "index.html")

    @staticmethod
    def login(request):
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

    @staticmethod
    def signup(request):
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

    @staticmethod
    def logout(request):
        logout(request)
        return redirect("/login")
