from django.db import models
import uuid
from accounts.models import Users
# Create your models here.
class Company(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4 )
    manager = models.ForeignKey(Users, blank=True, null=True, on_delete=models.CASCADE, related_name='companyManager')
    name = models.CharField(max_length=255, blank=True, null=True)
    total_employees = models.IntegerField(default=0)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


    class Meta:
        db_table = 'company_table'
        verbose_name  = 'Company'
        verbose_name_plural= 'Companies'
