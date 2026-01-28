from django.db import models
import uuid
from accounts.models import Users
from decimal import Decimal
from companies.models import Company
# Create your models here.


class Lead(models.Model):
    SOURCES=(
        ('manual','Manual') , #for manual entries from portal
        ('whatsapp','WhatsApp'),
        ('webform','Web Forms'),
        ('calls','Calls'),
    )
    STATUS=(
        ('inprogress','In Progress'),
        ('success','Success'),
        ('failure','Failure'),
    )
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, choices=SOURCES , default='manual')
    status = models.CharField(max_length=255, choices=STATUS , default='inprogress')
    handler = models.ForeignKey(Users,blank=True, null=True, on_delete=models.CASCADE, related_name='employeeLeads')
    value = models.DecimalField( max_digits=12, decimal_places=2,default=Decimal(0.00))
    expected_closure_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at =  models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.handler.name}'s Lead"
    

    class Meta:
        db_table = 'lead_table'
        verbose_name='Lead'
        verbose_name_plural='Leads'



class UpdateLeadNotes(models.Model):

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='update_notes_leads')
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.lead.name + "Note"


    class Meta:
        db_table = 'lead_notes_table'
        verbose_name = 'Update Lead Note'
        verbose_name_plural = 'Update Lead Notes'
        ordering = ['-created_at']


class TempCSVImport(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField() # Stores the file in the DB temporarily
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'temp_csv_imports'