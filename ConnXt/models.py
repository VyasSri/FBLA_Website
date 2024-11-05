from django.db import models
from django.contrib.auth.models import User

# StudentInfo Model: A profile for students associated with the user
class StudentInfo(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    student_grade = models.IntegerField(default=0)
    student_email = models.EmailField(max_length=100)
    student_skills = models.CharField(max_length=200)
    student_experience = models.CharField(max_length=200)
    student_info = models.CharField(max_length=200)
    student_resume = models.CharField(max_length=200)
    profile_complete = models.BooleanField(default=False)  # Track if profile is complete

    def __str__(self):
        return self.student_name

# JobPosting Model: Defines job/workshop details posted by employers
class JobPosting(models.Model):
    job_title = models.CharField(max_length=100)
    job_hours = models.IntegerField()
    job_skills = models.CharField(max_length=200)
    job_description = models.TextField()
    company = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The employer posting the job
    job_date = models.CharField(max_length=100, default='')
    job_location = models.CharField(max_length=100, default='')
    job_capacity = models.IntegerField()
    students_applied = models.ManyToManyField(to='StudentInfo', through='JobApplication', related_name='applied_jobs', blank=True)

    def __str__(self):
        return self.job_title

# JobApplication Model: Tracks applications made by students for jobs
class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.student_name} applied to {self.job.job_title}'
