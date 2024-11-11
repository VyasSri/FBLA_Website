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
    job_questions = models.TextField()
    job_capacity = models.IntegerField()
    students_applied = models.ManyToManyField(to='StudentInfo', through='JobApplication', related_name='applied_jobs', blank=True)
    is_approved = models.BooleanField(default=False)  # Track if job is approved by admin


    def __str__(self):
        return self.job_title

class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    essay_answer = models.TextField(null=True, blank=True)  # Answer to the job questions

    def __str__(self):
        return f'{self.student.student_name} applied to {self.job.job_title}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} - {"Read" if self.is_read else "Unread"}'