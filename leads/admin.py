from django.contrib import admin
from .models import Lead, LeadNotes
# Register your models here.
admin.site.register(Lead)
admin.site.register(LeadNotes)