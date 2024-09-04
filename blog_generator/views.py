from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import yt_dlp
import os
import assemblyai as aai
# from openai import OpenAI


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

        # get ytb link
        title = ytb_title(ytb_link)

        # get transcription (to English)
        transcription = get_transcription(ytb_link)
        if not transcription:
            return JsonResponse({"error": "Failed to get transcription."}, status=500)

        # use OpenAI model to generate the blog article
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({"error": "Failed to generate blog article."}, status=500)

        # save blog article to database

        # return blog article as a response
        return JsonResponse({"content": blog_content})

    else:
        return JsonResponse({"error": "Method is not valid."}, status=405)  # prevent user to use different methods excepting POST


def ytb_title(link):
    """Get the title of a YouTube video"""
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        title = info_dict.get('title', None)
    return title


def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(settings.AUDIO_ROOT, '%(title)s.%(ext)s')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        out_file = ydl.prepare_filename(info_dict)
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp3" # convert extension to .mp3 instead of webm
        # os.rename(out_file, new_file)

    return new_file


def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "cada8d494b3a42c5ad44898849d839e0"
    transcriber = aai.Transcriber()
    transcription = transcriber.transcribe(audio_file)
    print("Transcription done")
    return transcription.text


# def generate_blog_from_transcription_gpt(transcription):
#     client = OpenAI(api_key=settings.OPENAI_API_KEY)
#     prompt = (f"Based on the following transcription from a YouTube video, write a comprehensive blog article,"
#               f"write it based on the transcription, but don't make it look like a YouTube video,"
#               f"make it look like a blog article:\n\n{transcription}\n\nArticle")
#     response = client.chat.completions.create(
#         model="gpt-4o-mini", #gpt-4o-mini  gpt-3.5-turbo-instruct
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt},
#         ],
#         max_tokens=1000,
#     )
#
#     # generate_content = response.choices[0].text.strip()
#     generate_content = response['choices'][0]['message']['content']
#     return generate_content


def generate_blog_from_transcription(transcription):
    prompt = f"I haven't enough money to continue use openai API :((( \n {transcription}"
    return prompt

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
