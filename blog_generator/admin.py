from django.contrib import admin
from .models import BlogPost


# Register your models here.
admin.site.register(BlogPost)  # allow admin to see this table
