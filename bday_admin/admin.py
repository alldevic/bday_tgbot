from django.contrib import admin

from .forms import ProfileForm
from .models import Message
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ( 'name','external_id', 'is_sub')
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'text', 'created_at')
