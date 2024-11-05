from django.contrib.auth.decorators import login_required

from .forms import StudentForm, JobForm
from .models import JobPosting, StudentInfo, JobApplication
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
def home(request):
    return render(request, 'index.html')

def talent(request):
    message = ""
    
    if request.method == 'POST' and 'application_id' in request.POST:
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Only allow action if the application is still pending
        if not application.accepted and not application.rejected:
            # Accept or Reject the application
            if action == 'accept':
                application.accepted = True
                message = f"{application.student.student_name} has been accepted."
            elif action == 'reject':
                application.rejected = True
                message = f"{application.student.student_name} has been rejected."
            
            application.save()
        else:
            # If already accepted/rejected, prevent duplicate actions
            message = f"{application.student.student_name} has already been processed."

        # Redirect to the same page with a message to prevent form resubmission
        return redirect('talent')

    # Only show applications that are still pending (not accepted or rejected)
    job_applications = JobApplication.objects.filter(accepted=False, rejected=False)
    
    return render(request, 'talent.html', {
        'job_applications': job_applications,
        'message': message,
    })


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
            form = JobForm()  # Reset the form after successful submission
        else:
            # If form is invalid, show the error message
            error_msg = "Form is invalid. Please correct the errors below."
    else:
        # If it's not a POST request, show a blank form
        form = JobForm()

    # Render the page with success or error messages
    return render(request, 'employerhome.html', {'form': form, 'success_msg': success_msg, 'error_msg': error_msg})


def jobs(request):
    job_postings = JobPosting.objects.all()
    message = None

    # Fetch the student's info based on the logged-in user
    student_info = StudentInfo.objects.filter(user=request.user).first()

    job_data = []
    for job in job_postings:
        # Check if the student has already applied to the job
        applied = JobApplication.objects.filter(job=job, student=student_info).exists() if student_info else False
        
        # Check if the job has available capacity
        total_applied = JobApplication.objects.filter(job=job).count()
        can_apply = total_applied < job.job_capacity
        
        job_data.append({
            'job': job,
            'has_applied': applied,
            'can_apply_flag': can_apply
        })

    # Handle job application logic
    if request.method == 'POST' and 'apply_job_id' in request.POST:
        job_id = request.POST.get('apply_job_id')
        job = get_object_or_404(JobPosting, id=job_id)

        # Conditions before applying to a job
        if not student_info or not student_info.profile_complete:
            message = "You need to complete your profile before applying."
        elif any(jd['has_applied'] for jd in job_data if jd['job'].id == job.id):
            message = "You have already applied for this opportunity."
        elif not any(jd['can_apply_flag'] for jd in job_data if jd['job'].id == job.id):
            message = "Workshop capacity reached."
        else:
            # Save the job application
            JobApplication.objects.create(job=job, student=student_info)
            message = "Application Successful."

    return render(request, 'employers.html', {
        'job_data': job_data,
        'message': message,
        'profile_exists': student_info.profile_complete if student_info else False,  # Simplified check
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
        return HttpResponseForbidden("You are not allowed to edit this workshop.")
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
            error_msg = "There was an error in updating the workshop. Please check the form for errors."
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
        return HttpResponseForbidden("You are not allowed to delete this workshop.")

    if request.method == 'POST':
        job.delete()  # Deletes the job from the database
        return redirect('/jobedit')  # Redirect back to the list of jobs

    return render(request, 'confirm_delete.html', {'job': job})

@login_required
def jobedit(request):
    jobs = JobPosting.objects.filter(user=request.user)  # Only show jobs posted by the logged-in user
    return render(request, 'jobedit.html', {'jobs': jobs})

@login_required
def employer_list(request):
    # Fetch all job applications where 'accepted' is True
    accepted_applications = JobApplication.objects.filter(accepted=True)
    rejected_applications = JobApplication.objects.filter(rejected=True)

    # Pass the accepted applications to the template
    return render(request, 'employer_list.html', {'accepted_applications': accepted_applications,'rejected_applications': rejected_applications})

def studentinstructions(request):
    return render(request, 'studentinstructions.html')

def employerinstructions(request):
    return render(request, 'employerinstructions.html')