from django.contrib import admin
from .models import Lead , TempCSVImport, UpdateLeadNotes
# Register your models here.
# admin.site.register(Lead)

admin.site.register(TempCSVImport)
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id','status')


@admin.register(UpdateLeadNotes)
class UpdateLeadNotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'created_at')