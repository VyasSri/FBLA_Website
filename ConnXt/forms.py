from django.forms import ModelForm
from django import forms
from .models import StudentInfo, JobPosting, JobApplication


class StudentForm(ModelForm):
    class Meta:
        model = StudentInfo
        fields = ['student_name', 'student_grade', 'student_email', 'student_skills', 'student_experience',
                  'student_info', 'student_resume']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'student_grade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Grade'}),
            'student_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'student_skills': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Technical Skills'}),
            'student_experience': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Work Experience'}),
            'student_info': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional Info'}),
            'student_resume': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resume Link'})
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['job_title', 'job_hours', 'job_skills', 'job_description', 'company', 'job_questions','job_capacity']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'job_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hours/Week'}),
            'job_skills': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Areas of Interest'}),
            'job_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Job Description'}),
            'company': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Company Name'}),
            'job_questions': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Required Essay Questions'}),
            'job_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Job Capacity'})
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['essay_answer']
        widgets = {
            'essay_answer': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Answer the job questions here'}),
        }