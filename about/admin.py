from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import About, ContactRequest


@admin.register(About)
class AboutAdmin(SummernoteModelAdmin):
    list_display = ('title', 'updated_on')
    summernote_fields = ('content',)


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'read')
    list_filter = ('category', 'read')
