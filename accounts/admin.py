from django.contrib import admin
from .models import Users
# Register your models here.

# admin.site.register(Users)

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display =('id','username','email')