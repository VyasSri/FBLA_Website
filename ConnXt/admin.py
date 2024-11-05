from django.contrib import admin

from .models import StudentInfo, JobPosting

# Register your models here.
admin.site.register(StudentInfo)
admin.site.register(JobPosting)