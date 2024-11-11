from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import StudentForm, JobForm, JobApplicationForm
from .models import JobPosting, StudentInfo, JobApplication, Notification
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User


# Create your views here.
def home(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'index.html', {'unread_notifications_count': unread_notifications_count})


def profile(request):
    success_msg = None
    error_msg = None

    # Fetch the student's existing profile based on the logged-in user
    student_info, created = StudentInfo.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Use the existing profile if it exists, otherwise create a new one
        form = StudentForm(request.POST, instance=student_info)

        if form.is_valid():
            # Save the form data but don't commit to the database yet
            student_info = form.save(commit=False)

            # Check if all required fields are filled to mark the profile as complete
            if all([
                student_info.student_name, student_info.student_grade,  # Ensure student_grade is filled
                student_info.student_email, student_info.student_skills,
                student_info.student_experience, student_info.student_resume
            ]):
                student_info.profile_complete = True
            else:
                student_info.profile_complete = False

            # Save the profile to the database
            student_info.save()

            success_msg = "Profile updated successfully!"
        else:
            error_msg = "Form is invalid. Please correct the errors below."

    else:
        # If it's a GET request, pre-populate the form with the student's current info
        form = StudentForm(instance=student_info)

    return render(request, "profile.html", {
        'form': form,
        'success_msg': success_msg if success_msg else None,
        'error_msg': error_msg if error_msg else None
    })


def employer(request):
    success_msg = None
    error_msg = None

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            # Save the job posting
            job = form.save(commit=False)
            job.user = request.user  # Attach the current logged-in user as the job poster
            job.save()
            success_msg = "Job Posted Successfully"

            # Notify admin users for approval
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"A new job '{job.job_title}' has been posted by {request.user.username} and awaits approval."
                )

            # Notify the employer that the job is awaiting admin approval
            Notification.objects.create(
                user=request.user,  # Employer is the current user
                message=f"Your job '{job.job_title}' has been posted and is awaiting admin approval."
            )

            form = JobForm()  # Reset the form after successful submission
        else:
            error_msg = "Form is invalid. Please correct the errors below."
    else:
        form = JobForm()

    return render(request, 'employerhome.html', {'form': form, 'success_msg': success_msg, 'error_msg': error_msg})

def jobs(request):
    job_postings = JobPosting.objects.filter(is_approved=True)
    message = None
    student_info = StudentInfo.objects.filter(user=request.user).first()
    job_data = []

    for job in job_postings:
        applied = JobApplication.objects.filter(job=job, student=student_info).exists() if student_info else False
        total_applied = JobApplication.objects.filter(job=job).count()
        can_apply = total_applied < job.job_capacity
        job_data.append({
            'job': job,
            'has_applied': applied,
            'can_apply_flag': can_apply
        })

    if request.method == 'POST' and 'apply_job_id' in request.POST:
        job_id = request.POST.get('apply_job_id')
        job = get_object_or_404(JobPosting, id=job_id)
        form = JobApplicationForm(request.POST)  # Use the new form

        if form.is_valid():
            if not student_info or not student_info.profile_complete:
                message = "Complete your profile before applying."
            elif any(jd['has_applied'] for jd in job_data if jd['job'].id == job.id):
                message = "You already applied for this opportunity."
            elif not any(jd['can_apply_flag'] for jd in job_data if jd['job'].id == job.id):
                message = "Job capacity reached."
            else:
                application = form.save(commit=False)
                application.job = job
                application.student = student_info
                application.save()
                message = "Application Successful."

                Notification.objects.create(
                    user=job.user,
                    message=f"A new application with an essay answer has been submitted by {student_info.student_name} for your job '{job.job_title}'."
                )
        else:
            message = "Please answer the question."

    else:
        form = JobApplicationForm()

    return render(request, 'employers.html', {
        'job_data': job_data,
        'message': message,
        'profile_exists': student_info.profile_complete if student_info else False,
        'form': form  # Pass the form to the template
    })



def studentdash(request):
    return render(request, 'studentdashboard.html')


def aboutus(request):
    return render(request, 'aboutus.html')


def studenterror(request):
    return render(request, 'studenterror.html')


def employererror(request):
    return render(request, 'employererror.html')


def edit_job(request, id):
    job = get_object_or_404(JobPosting, id=id)
    # Ensure the current user is the one who posted the job
    if job.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this job.")
    success_msg = None
    error_msg = None
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            success_msg = "Job updated successfully."
        else:
            # Debug the form errors
            print(form.errors)
            error_msg = "There was an error in updating the job. Please check the form for errors."
    else:
        form = JobForm(instance=job)
    return render(request, 'edit_job.html', {
        'form': form,
        'success_msg': success_msg,
        'error_msg': error_msg
    })

@login_required
def delete_job(request, id):
    job = get_object_or_404(JobPosting, id=id)

    # Ensure the current user is the one who posted the job
    if job.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this job.")

    if request.method == 'POST':
        job.delete()  # Deletes the job from the database
        return redirect('/jobedit')  # Redirect back to the list of jobs

    return render(request, 'confirm_delete.html', {'job': job})

@login_required
def jobedit(request):
    jobs = JobPosting.objects.filter(user=request.user)  # Only show jobs posted by the logged-in user
    return render(request, 'jobedit.html', {'jobs': jobs})

@login_required
def manage_applications(request):
    message = ""
    
    if request.method == 'POST' and 'application_id' in request.POST:
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        application = get_object_or_404(JobApplication, id=application_id)
        
        if not application.accepted and not application.rejected:
            if action == 'accept':
                application.accepted = True
                application.save()
                message = f"{application.student.student_name} has been accepted."
                
                # Send notification to the student about acceptance
                Notification.objects.create(
                    user=application.student.user,
                    message=f"Congratulations! You have been accepted for the job '{application.job.job_title}' by {application.job.user.username}."
                )
                
            elif action == 'reject':
                application.rejected = True
                application.save()
                message = f"{application.student.student_name} has been rejected."
                
                # Send notification to the student about rejection
                Notification.objects.create(
                    user=application.student.user,
                    message=f"Unfortunately, your application for the job '{application.job.job_title}' has been rejected by {application.job.user.username}."
                )

        return redirect('manage_applications')

    # Retrieve all applications (pending, accepted, and rejected)
    pending_applications = JobApplication.objects.filter(accepted=False, rejected=False)
    accepted_applications = JobApplication.objects.filter(accepted=True)
    rejected_applications = JobApplication.objects.filter(rejected=True)
    
    return render(request, 'manage_applications.html', {
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
        'rejected_applications': rejected_applications,
        'message': message,
    })

def studentinstructions(request):
    return render(request, 'studentinstructions.html')

def employerinstructions(request):
    return render(request, 'employerinstructions.html')


# Check if the user is a superuser
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
@login_required
def adminpanel(request):
    # Fetch all unapproved job postings
    unapproved_jobs = JobPosting.objects.filter(is_approved=False)

    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        action = request.POST.get('action')
        job = get_object_or_404(JobPosting, id=job_id)

        # Check the action and update job approval status
        if action == 'approve':
            job.is_approved = True
            job.save()
            
            # Notify the employer of approval if not already notified
            approval_message = f"Your job '{job.job_title}' has been approved and is now live."
            if not Notification.objects.filter(user=job.user, message=approval_message).exists():
                Notification.objects.create(user=job.user, message=approval_message)
                
        elif action == 'reject':
            job.delete()  # Optionally delete the job if rejected
            
            # Notify the employer of rejection if not already notified
            rejection_message = f"Your job '{job.job_title}' has been rejected by the admin."
            if not Notification.objects.filter(user=job.user, message=rejection_message).exists():
                Notification.objects.create(user=job.user, message=rejection_message)

        # Redirect back to the admin panel after the action
        return redirect('adminpanel')

    return render(request, 'adminpanel.html', {
        'unapproved_jobs': unapproved_jobs,
    })

def update_application_status(request, application_id, action):
    application = JobApplication.objects.get(id=application_id)
    
    if action == 'approve':
        application.accepted = True
        application.save()
        message = f'Your application for {application.job.job_title} has been approved.'
    elif action == 'reject':
        application.rejected = True
        application.save()
        message = f'Your application for {application.job.job_title} has been rejected.'
    
    # Create a notification for the student
    Notification.objects.create(user=application.student.user, message=message)

    return redirect(request, 'adminpanel.html')  # or any relevant page

def inbox(request):
    if request.user.is_authenticated:
        # Handle deletion if a delete request is sent
        if request.method == 'POST' and 'notification_id' in request.POST:
            notification_id = request.POST.get('notification_id')
            notification = Notification.objects.filter(id=notification_id, user=request.user).first()
            if notification:
                notification.delete()
            return redirect('inbox')  # Redirect to the inbox after deletion

        # Retrieve all notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        return render(request, 'inbox.html', {'notifications': notifications})
    return redirect('/login')

def licensing(request):
    return render(request, 'licensing.html')