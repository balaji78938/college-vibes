from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.decorators import login_required, user_passes_test # type: ignore
from django.contrib.auth.hashers import make_password, check_password # type: ignore
from django.contrib.auth.views import LoginView # type: ignore
from django.contrib import messages # type: ignore
from django.db import models # type: ignore
from django import forms # type: ignore
from datetime import date
from .models import Club, Event, StudentRegistration, Student
from .forms import ClubForm
# Helper function to check if user is master
def is_master_user(user):
    return user.is_authenticated and user.is_superuser


def index(request):
    # Fetch all upcoming events (events with date >= today)
    events = Event.objects.all()
    context = {
        'events': events,
    }
    return render(request, 'vibes/index.html', context)



def login_view(request):
    if request.method == "POST":
        roll_no = request.POST['roll_no']
        password = request.POST['password']

        try:
            student = Student.objects.get(roll_no=roll_no)

            if student.password == password:  # If passwords are stored in plain text
                request.session['student_id'] = student.id  # Store session
                return redirect('student_dashboard')  # Redirect to student dashboard
            else:
                return render(request, 'vibes/login.html', {'error': 'Invalid Roll Number or Password'})
        
        except Student.DoesNotExist:
            return render(request, 'vibes/login.html', {'error': 'Invalid Roll Number or Password'})

    return render(request, 'vibes/login.html')



def logout_view(request):
    logout(request)
    return redirect("index")  # Redirect to the index page after logout



def register(request):
    if request.method == "POST":
        roll_no = request.POST['roll_no']
        name = request.POST['name']
        branch = request.POST['branch']
        password = request.POST['password']  # Storing plain text password
        contact = request.POST['contact']
        college = request.POST['college']
        email = request.POST['email']

        # Check if student already exists by roll number or email
        if Student.objects.filter(roll_no=roll_no).exists():
            messages.error(request, 'Roll Number already registered.')
            return redirect('register')
        elif Student.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        # Save student data to database
        student = Student(
            roll_no=roll_no,
            name=name,
            branch=branch,
            password=password,  # Storing as plain text
            contact=contact,
            college=college,
            email=email
        )
        student.save()

        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')  # Redirect to login after registration

    return render(request, 'vibes/register.html')

# Master Login
def master_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:  # Ensure only master user can log in
            login(request, user)
            return redirect("master_dashboard")
        else:
            return render(request, "vibes/master_login.html", {"error": "Invalid credentials!"})

    return render(request, "vibes/master_login.html")

# Master Dashboard (Only for Master User)
@login_required
@user_passes_test(is_master_user)
def master_dashboard(request):
    clubs = Club.objects.all()
    return render(request, "vibes/master_dashboard.html", {"clubs": clubs})
def master_add_student(request):
    if request.method == "POST":
        roll_no = request.POST['roll_no']
        name = request.POST['name']
        branch = request.POST['branch']
        password = request.POST['password']  # Storing plain text password
        contact = request.POST['contact']
        college = request.POST['college']
        email = request.POST['email']

        # Check if student already exists by roll number or email
        if Student.objects.filter(roll_no=roll_no).exists():
            messages.error(request, 'Roll Number already registered.')
            return redirect('master_add_student')
        elif Student.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('master_add_student')

        # Save student data to database
        student = Student(
            roll_no=roll_no,
            name=name,
            branch=branch,
            password=password,  # Storing as plain text
            contact=contact,
            college=college,
            email=email
        )
        student.save()
        
        # ✅ Send welcome email with WhatsApp join link
        subject = '🎉 Your College Vibes Account is Created!'
        message = f'''
Hello {name},

Your account has been successfully created in College Vibes. You can now register for events and enjoy the vibes! 🎊

To receive important WhatsApp updates (like event reminders), join our notification channel by clicking below:

👉 https://api.whatsapp.com/send/?phone=%2B14155238886&text=join+up-gentle&type=phone_number&app_absent=0

Stay tuned!
- Team College Vibes
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Make sure it's configured in settings.py
            [email],
            fail_silently=False
        )

        messages.success(request, 'Registration successful! An email has been sent to the student.')
        return redirect('master_dashboard')# Redirect to login after registration

    return render(request, 'vibes/master_add_student.html')
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import xlrd # type: ignore
from .models import Student

# View to handle student data upload and preview
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import csv
import xlrd
from io import BytesIO
from .models import Student

# View to handle student data upload and preview
def upload_students(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            data = file.read().decode('utf-8')
            students_data = parse_csv(data)
        elif file.name.endswith(('.xls', '.xlsx')):
            data = file.read()
            students_data = parse_excel(data)
        else:
            messages.error(request, "Invalid file format. Please upload a CSV or Excel file.")
            return redirect('upload_students')

        # Render the template with the parsed data
        return render(request, 'vibes/upload_students.html', {'students_data': students_data})

    return render(request, 'vibes/upload_students.html')

# Function to parse CSV file
def parse_csv(data):
    lines = data.splitlines()
    reader = csv.reader(lines)
    headers = next(reader, None)  # Skip the header row
    students_data = [row for row in reader if row]  # Exclude empty rows
    return students_data

# Function to parse Excel file
def parse_excel(data):
    book = xlrd.open_workbook(file_contents=data)
    sheet = book.sheet_by_index(0)
    students_data = []
    for row_index in range(1, sheet.nrows):  # Skip header
        row = sheet.row_values(row_index)
        students_data.append([str(cell) for cell in row])  # Convert to strings
    return students_data

# Function to handle student creation based on submitted data
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from .models import Student
import re
import logging

logger = logging.getLogger(__name__)

def create_students(request):
    if request.method == 'POST':
        students_data = []
        # Extract data from the form (structured as students_data[row][column])
        for key, value in request.POST.items():
            if key.startswith('students_data'):
                # Parse the key to get row and column indices
                match = re.match(r'students_data\[(\d+)\]\[(\d+)\]', key)
                if match:
                    row_idx, col_idx = map(int, match.groups())
                    while len(students_data) <= row_idx:
                        students_data.append([])
                    while len(students_data[row_idx]) <= col_idx:
                        students_data[row_idx].append('')
                    students_data[row_idx][col_idx] = value

        for student_data in students_data:
            if len(student_data) < 7:
                messages.error(request, "Invalid data format for a student entry.")
                continue

            roll_no, name, branch, password, contact, college, email = student_data

            # Validation
            if not all([roll_no, name, email, password]):
                messages.error(request, f"Missing required fields for Roll No: {roll_no}")
                continue

            # Check for duplicates
            if Student.objects.filter(roll_no=roll_no).exists():
                messages.error(request, f"Roll Number {roll_no} already registered.")
                continue
            if Student.objects.filter(email=email).exists():
                messages.error(request, f"Email {email} already registered.")
                continue

            # Create student
            student = Student(
                roll_no=roll_no,
                name=name,
                branch=branch,
                password=make_password(password),  # Hash the password
                contact=contact,
                college=college,
                email=email
            )
            student.save()

            # Send welcome email
            email_subject = "Welcome to College Vibes!"
            full_message = f"""Hello {name},

Your account has been successfully created in College Vibes. You can now register for events and enjoy the vibes! 🎊

**Your Account Details:**
- **Username**: {roll_no}
- **Password**: {password}

Please keep this information secure and do not share it with others.

To receive important WhatsApp updates (like event reminders), join our notification channel by clicking below:

👉 https://api.whatsapp.com/send/?phone=%2B14155238886&text=join+up-gentle&type=phone_number&app_absent=0
"""
            from_email =  settings.EMAIL_HOST_USER # Replace with your sender email
            recipient_email = student.email

            success = send_gmail_message(email_subject, full_message, from_email, recipient_email)
            if not success:
                messages.warning(request, f"Student {name} created, but failed to send welcome email to {email}.")

        messages.success(request, "Students created successfully!")
        return redirect('master_dashboard')

    return redirect('upload_students')
# Register a New Club
@login_required
@user_passes_test(is_master_user)
def register_club(request):
    if request.method == "POST":
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            club.password = make_password(form.cleaned_data["password"])  # Hash password
            club.save()
            return redirect("master_dashboard")
    else:
        form = ClubForm()
    return render(request, "vibes/register_club.html", {"form": form})

# Edit Club Details
@login_required
@user_passes_test(is_master_user)
def edit_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == "POST":
        form = ClubForm(request.POST, instance=club)
        if form.is_valid():
            form.save()
            return redirect("master_dashboard")
    else:
        form = ClubForm(instance=club)
    return render(request, "vibes/edit_club.html", {"form": form})

# Delete a Club
@login_required
@user_passes_test(is_master_user)
def delete_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == "POST":
        club.delete()
        return redirect("master_dashboard")
    return render(request, "vibes/delete_club.html", {"club": club})

@login_required
@user_passes_test(is_master_user)
@login_required
def view_clubs(request):
    clubs = Club.objects.all()
    return render(request, "vibes/view_clubs.html", {"clubs": clubs})

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Club, Event, StudentRegistration
from django.shortcuts import render, redirect
from .models import Club, Event, StudentRegistration
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Club, EventResult, StudentRegistration
@login_required
@user_passes_test(is_master_user)
def master_view_results(request):
    """
    Display all event results (winners and runner-ups) from all clubs.
    """

    # Fetch all results with related event, winner, and runner-up info
    results = EventResult.objects.all().select_related(
        'event',
        'event__club',
        'winner__student',
        'runner_up__student'
    )

    # Prepare results with group members for group events
    results_with_members = []
    for result in results:
        result_data = {
            'result': result,
            'winner_group_members': [],
            'runner_up_group_members': []
        }

        if result.event.is_group_event:
            # Fetch group members for winner
            if result.winner_group_name:
                result_data['winner_group_members'] = StudentRegistration.objects.filter(
                    event=result.event,
                    group_name=result.winner_group_name
                ).select_related('student')

            # Fetch group members for runner-up
            if result.runner_up_group_name:
                result_data['runner_up_group_members'] = StudentRegistration.objects.filter(
                    event=result.event,
                    group_name=result.runner_up_group_name
                ).select_related('student')

        results_with_members.append(result_data)

    return render(request, 'vibes/master_view_results.html', {
        'results_with_members': results_with_members
    })

@login_required
@user_passes_test(is_master_user)
def master_current_events(request): # Retrieve the club object
    events = Event.objects.filter( date__gte=timezone.now()) # Fetch only this club's events
    return render(request, 'vibes/master_current_events.html', {'events': events})

def master_completed_events(request):
    events = Event.objects.filter(is_completed=True).order_by('-date')  # Order by date descending (most recent first)
    return render(request, 'vibes/master_completed_events.html', {'events': events})

def master_solo_event_registrations(request):
    """
    Display registrations for solo (individual) events that are not completed, for all clubs.
    """
    # Filter solo events that are not completed
    events = Event.objects.filter(
        is_group_event=False,
        is_completed=False
    )
    # Filter solo registrations for non-completed events
    registrations = StudentRegistration.objects.filter(
        event__in=events,
        payment_verified=True
    )

    return render(request, 'vibes/master_solo_event_registrations.html', {
        'registrations': registrations
    })

def master_group_event_registrations(request):
    """
    Display registrations for group events that are not completed, including group name, for all clubs.
    """
    # Filter group events that are not completed
    events = Event.objects.filter(
        is_group_event=True,
        is_completed=False
    )
    # Filter group registrations for non-completed events
    registrations = StudentRegistration.objects.filter(
        event__in=events,
        payment_verified=True
    )

    return render(request, 'vibes/master_group_event_registrations.html', {
        'registrations': registrations
    })

def master_students_attended(request):
    attended_registrations = StudentRegistration.objects.filter(
        attended=True,
        event__is_completed=True
    ).select_related('student', 'event')
    return render(request, 'vibes/master_students_attended.html', {
        'attended_registrations': attended_registrations
    })

def club_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        try:
            club = Club.objects.get(username=username)
           
            if club.password == password:  # If passwords are not hashed
            # if check_password(password, club.password):  # Use this if passwords are hashed
                request.session['club_id'] = club.id  # Store session for login
                return redirect('club_dashboard')
            else:
                return render(request, 'vibes/club_login.html', {'error': 'Invalid club username or password'})
        except Club.DoesNotExist:
            return render(request, 'vibes/club_login.html', {'error': 'Invalid club username or password'})

    return render(request, 'vibes/club_login.html')


def club_dashboard(request):
    # Check if the club is logged in using session
    club_id = request.session.get("club_id")
    
    if not club_id:
        messages.error(request, "You must be logged in to access this page.")
        return redirect("club_login")  # Redirect to club login if not logged in
    
    # Fetch club details
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        messages.error(request, "Club not found.")
        return redirect("club_login")

    return render(request, "vibes/club_dashboard.html", {"club": club})



@login_required
@user_passes_test(is_master_user)  # Ensure only the master user can view student details
def student_details(request):
    students = Student.objects.all().order_by('roll_no')  # Fetch all students from the database
    return render(request, "vibes/student_details.html", {"students": students})


from .models import Student, Event  # Ensure you have these models

from django.shortcuts import render, get_object_or_404, redirect # type: ignore
from django.contrib.auth.hashers import make_password # type: ignore
from .models import Student

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student.name = request.POST.get('name')
        student.branch = request.POST.get('branch')
        student.college = request.POST.get('college')
        student.contact = request.POST.get('contact')
        student.email = request.POST.get('email')
        if Student.objects.filter(email=student.email).exclude(id=student_id).exists():
            messages.error(request, "Email already exists. Please use a different email.")
            return render(request, 'vibes/edit_student.html', {'student': student})
        new_password = request.POST.get('password')
        if new_password:  # Update password only if a new one is provided
            student.password=new_password

        student.save()
        return redirect('student_details')  # Redirect to the student details page after updating

    return render(request, 'vibes/edit_student.html', {'student': student})


from django.shortcuts import get_object_or_404, redirect # type: ignore
from django.contrib import messages # type: ignore
from .models import Student  # Import your Student model

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    
    return redirect('student_details')  # Redirect to student details page


def manage_events(request):
    if 'club_id' not in request.session:  # Check if the club is logged in
        return redirect('club_login')

    club_id = request.session['club_id']  # Get logged-in club's ID
    club = Club.objects.get(id=club_id)  # Retrieve the club object
    events = Event.objects.filter(club=club, date__gte=timezone.now()) # Fetch only this club's events
  

    return render(request, 'vibes/manage_events.html', {'events': events})

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Event, Club  # Assuming Club model exists

def completed_events(request):
    if 'club_id' not in request.session:  # Check if the club is logged in
        return redirect('club_login')

    club_id = request.session['club_id']  # Get logged-in club's ID
    club = Club.objects.get(id=club_id)  # Retrieve the club object
    # Fetch only this club's completed events
    events = Event.objects.filter(
        club=club,
        is_completed=True
    ).order_by('-date')  # Order by date descending (most recent first)

    return render(request, 'vibes/completed_events.html', {'events': events})
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Club, Event, StudentRegistration
from django.shortcuts import render, redirect
from .models import Club, Event, StudentRegistration

def solo_event_registrations(request):
    """
    Display registrations for solo (individual) events that are not completed.
    """
    if 'club_id' not in request.session:  # Ensure only logged-in clubs access this page
        return redirect('club_login')

    club_id = request.session['club_id']  # Get the logged-in club's ID
    club = Club.objects.get(id=club_id)  # Fetch the club object
    # Filter solo events that are not completed
    events = Event.objects.filter(
        club=club,
        is_group_event=False,
        is_completed=False
    )
    # Filter solo registrations for non-completed events
    registrations = StudentRegistration.objects.filter(
        event__in=events,
        payment_verified=True
    )

    return render(request, 'vibes/solo_event_registrations.html', {'registrations': registrations})
    

import logging
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import transaction
from .models import Club, Event, StudentRegistration

logger = logging.getLogger(__name__)

def is_attend(request):
    """
    Display completed solo and group event registrations with individual attendance status.
    Allow bulk updates of attendance via a single form submission.
    """
    if 'club_id' not in request.session:
        logger.warning("No club_id in session, redirecting to club_login")
        messages.error(request, "You must be logged in to view attendance.")
        return redirect('club_login')

    club_id = request.session['club_id']
    logger.debug(f"Processing is_attend for club_id: {club_id}")

    club = Club.objects.get(id=club_id)

    if request.method == "POST":
        updated_count = 0
        try:
            with transaction.atomic():
                # Fetch valid registrations to validate against
                valid_registrations = StudentRegistration.objects.filter(
                    event__club_id=club_id,
                    event__is_completed=True,
                    payment_verified=True
                ).select_related('student', 'event')

                # Create a dictionary for quick lookup
                valid_registrations_dict = {str(reg.id): reg for reg in valid_registrations}

                # Process all registrations to determine attendance
                for registration in valid_registrations:
                    # Checkbox name: attended_{registration.id}
                    checkbox_name = f'attended_{registration.id}'
                    # If checkbox is checked, it's present in POST with value 'on'
                    new_status = checkbox_name in request.POST
                    if registration.attended != new_status:
                        registration.attended = new_status
                        registration.save(update_fields=['attended'])
                        updated_count += 1
                        logger.info(
                            f"Attendance for student '{registration.student.id}' in event "
                            f"'{registration.event.id}' set to {'attended' if new_status else 'not attended'}"
                        )

                if updated_count > 0:
                    messages.success(request, f"Updated attendance for {updated_count} student(s).")
                else:
                    messages.info(request, "No attendance changes were made.")

        except Exception as e:
            logger.error(f"Error updating attendance for club_id {club_id}: {str(e)}")
            messages.error(request, "An error occurred while updating attendance. Please try again.")
        return redirect('is_attend')

    # Fetch completed events (solo and group)
    events = Event.objects.filter(
        club=club,
        is_completed=True
    )

    # Fetch all registrations (solo and group, no leader filter)
    registrations = StudentRegistration.objects.filter(
        event__in=events,
        payment_verified=True
    ).select_related('student', 'event').order_by('event__name', 'group_name', 'student__name')

    logger.debug(f"Found {registrations.count()} registrations for attendance")
    return render(
        request,
        'vibes/is_attend.html',  # Corrected template name to match your latest
        {'registrations': registrations}
    )


from django.shortcuts import render
from .models import StudentRegistration

from django.shortcuts import get_object_or_404

def students_attended(request):
    club_id = request.session.get('club_id')
    if not club_id:
        return redirect('club_login')  # Redirect to login if not logged in

    club = get_object_or_404(Club, id=club_id)

    attended_registrations = StudentRegistration.objects.filter(
        attended=True,
        event__is_completed=True,
        event__club=club
    ).select_related('student', 'event')

    return render(request, 'vibes/students_attended.html', {
        'attended_registrations': attended_registrations
    })


def group_event_registrations(request):
    """
    Display registrations for group events that are not completed, including group name.
    """
    if 'club_id' not in request.session:  # Ensure only logged-in clubs access this page
        return redirect('club_login')

    club_id = request.session['club_id']  # Get the logged-in club's ID
    club = Club.objects.get(id=club_id)  # Fetch the club object
    # Filter group events that are not completed
    events = Event.objects.filter(
        club=club,
        is_group_event=True,
        is_completed=False
    )
    # Filter group registrations for non-completed events
    registrations = StudentRegistration.objects.filter(
        event__in=events,
        payment_verified=True
    )

    return render(request, 'vibes/group_event_registrations.html', {'registrations': registrations})

from django.shortcuts import render, redirect # type: ignore
from .models import Event, StudentRegistration, Notification
from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect # type: ignore
from .models import Notification, Event, Student, StudentRegistration, Club
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings

import logging
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Club, Event, Student, Notification

logger = logging.getLogger(__name__)
import logging
import requests
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Club, Event, Student, Notification

import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import Club, Event, Student, Notification

logger = logging.getLogger(__name__)

import logging
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Club, Event, Student, Notification
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import Club, Event, Student, Notification
import logging

logger = logging.getLogger(__name__)

def send_notifications(request):
    club_id = request.session.get("club_id")
    if not club_id:
        messages.error(request, "You must be logged in to send notifications.")
        return redirect("login")

    if request.method == "POST":
        event_id = request.POST.get("event_id")
        message = request.POST.get("message")

        try:
            club = Club.objects.get(id=club_id)
            event = Event.objects.get(id=event_id, club=club)

            registered_students = Student.objects.filter(studentregistration__event=event)
            logger.info(f"Found {registered_students.count()} students for event {event.name}")

            if not registered_students.exists():
                messages.warning(request, "No students are registered for this event.")
                return render(request, "vibes/send_notifications.html", {
                    "events": Event.objects.filter(club_id=club_id),
                    "selected_event": event_id,
                    "message": message
                })

            notification = Notification.objects.create(
                event=event,
                sender=club,
                message=message
            )
            notification.recipients.set(registered_students)

            # Prepare message details
            full_message = f"{message}\n\nEvent: {event.name}\nClub: {club.name}"
            email_subject = f"Notification from {club.name} - {event.name}"
            from_email = settings.EMAIL_HOST_USER  # Use EMAIL_HOST_USER from settings
            email_sent_count = 0
            whatsapp_sent_count = 0

            for student in registered_students:
                # Send email using separate view
                if student.email:
                    if send_gmail_message(email_subject, full_message, from_email, student.email):
                        email_sent_count += 1
                else:
                    logger.warning(f"Student {student.id} has no email address")

                # Send WhatsApp using message only
                if student.contact and student.contact.isdigit() and len(student.contact) == 10:
                    try:
                        sid = send_whatsapp_message(
                            to_number=student.contact,
                            user_name=student.name,
                            message=full_message
                        )
                        if sid:
                            whatsapp_sent_count += 1
                            logger.info(f"WhatsApp sent to {student.contact}, SID: {sid}")
                        else:
                            logger.warning(f"WhatsApp message not sent to {student.contact}")
                    except Exception as e:
                        logger.error(f"Error sending WhatsApp to {student.contact}: {e}")
                else:
                    logger.warning(f"Invalid or missing contact for student {student.id}: {student.contact}")

            if email_sent_count == 0 and whatsapp_sent_count == 0:
                messages.warning(request, "No notifications sent: No students have valid email or contact.")
                return render(request, "vibes/send_notifications.html", {
                    "events": Event.objects.filter(club_id=club_id),
                    "selected_event": event_id,
                    "message": message
                })

            messages.success(request, f"Notifications sent: {email_sent_count} email(s), {whatsapp_sent_count} WhatsApp message(s)")
            return redirect("send_notifications")

        except (Event.DoesNotExist, Club.DoesNotExist):
            messages.error(request, "Invalid event or club.")
            return render(request, "vibes/send_notifications.html", {
                "error": "Invalid event or club.",
                "events": Event.objects.filter(club_id=club_id)
            })

    club_events = Event.objects.filter(club_id=club_id)
    return render(request, "vibes/send_notifications.html", {"events": club_events})

def send_gmail_message(email_subject, full_message, from_email, recipient_email):
    """
    Send an email to a single recipient.
    
    Args:
        email_subject (str): Subject of the email
        full_message (str): Complete email message content
        from_email (str): Sender's email address
        recipient_email (str): Recipient's email address
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        send_mail(
            email_subject,
            full_message,
            from_email,
            [recipient_email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return False
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import StudentRegistration, Event

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import StudentRegistration, Event
import logging
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .models import StudentRegistration

logger = logging.getLogger(__name__)

def verify_payment(request, registration_id=None):
    # Check if the user is authorized (e.g., club admin)
    if 'club_id' not in request.session:
        logger.warning("No club_id in session, redirecting to login")
        messages.error(request, "You must be logged in to verify payments.")
        return redirect('login')

    club_id = request.session['club_id']
    logger.debug(f"Processing verify_payment for club_id: {club_id}, registration_id: {registration_id}")

    if request.method == "POST" and registration_id:
        registration = get_object_or_404(StudentRegistration, id=registration_id, event__club_id=club_id)
        
        # Check if it's a paid event
        if registration.event.price and registration.event.price > 0:
            if registration.utr:  # Ensure UTR exists
                # If it's a group event, update all group members
                if registration.event.is_group_event and registration.group_name:
                    group_registrations = StudentRegistration.objects.filter(
                        event=registration.event,
                        group_name=registration.group_name
                    )
                    new_status = not registration.payment_verified  # Toggle status
                    group_registrations.update(payment_verified=new_status)
                    logger.info(f"Payment for group '{registration.group_name}' in event '{registration.event.id}' set to {'verified' if new_status else 'unverified'}")
                    messages.success(request, f"Payment for group '{registration.group_name}' in '{registration.event.name}' {'verified' if new_status else 'unverified'} successfully!")
                else:
                    # Solo event, update single registration
                    registration.payment_verified = not registration.payment_verified
                    registration.save(update_fields=['payment_verified'])
                    logger.info(f"Payment for student '{registration.student.id}' in event '{registration.event.id}' set to {'verified' if registration.payment_verified else 'unverified'}")
                    messages.success(request, f"Payment for {registration.student.name} in '{registration.event.name}' {'verified' if registration.payment_verified else 'unverified'} successfully!")
            else:
                logger.warning(f"Attempted to verify payment for registration {registration_id} without UTR")
                messages.error(request, "Cannot verify payment without a UTR.")
        else:
            logger.warning(f"Attempted to verify payment for non-paid event in registration {registration_id}")
            messages.error(request, "This is not a paid event.")
        return redirect('verify_payment')

    # Fetch registrations for paid events under the club
    # For group events, only include leader registrations; for solo events, include all
    registrations = StudentRegistration.objects.filter(
        event__club_id=club_id,
        event__price__gt=0
    ).filter(
        # Include solo events (is_group_event=False) or leader registrations (is_leader=True)
        models.Q(event__is_group_event=False) | models.Q(is_leader=True)
    ).select_related('student', 'event').order_by('event__name', 'group_name')

    logger.debug(f"Found {registrations.count()} registrations for payment verification")
    return render(request, 'vibes/verify_payment.html', {'registrations': registrations})
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Event, EventResult, StudentRegistration
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Club, Event, EventResult, StudentRegistration
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Club, Event, EventResult, StudentRegistration

def mark_results(request):
    club_id = request.session.get('club_id')
    if not club_id:
        messages.error(request, "Please log in to access this page.")
        return redirect('club_login')

    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        messages.error(request, "Invalid club session.")
        return redirect('club_login')

    completed_events = Event.objects.filter(club=club, is_completed=True)
    
    # Prepare data for each event
    event_data = []
    for event in completed_events:
        registrations = StudentRegistration.objects.filter(
            event=event, 
            attended=True
        ).select_related('student')
        
        selections = []
        info = {}
        if event.is_group_event:
            # Get distinct group names for group events
            group_names = list(
                StudentRegistration.objects
                .filter(event=event, attended=True)
                .values_list('group_name', flat=True)
                .distinct()
                .exclude(group_name__isnull=True)
                .order_by('group_name')
            )
            selections = group_names
            # Get leader info for each group
            for group_name in group_names:
                leader = StudentRegistration.objects.filter(
                    event=event, 
                    group_name=group_name, 
                    is_leader=True, 
                    attended=True
                ).select_related('student').first()
                if leader:
                    info[group_name] = {
                        'name': leader.student.name,
                        'roll_no': leader.student.roll_no,
                        'registration_id': leader.id
                    }
        else:
            # Get roll numbers for solo events
            selections = [reg.student.roll_no for reg in registrations]
            # Map roll numbers to student info
            info = {
                reg.student.roll_no: {
                    'name': reg.student.name,
                    'roll_no': reg.student.roll_no,
                    'registration_id': reg.id
                } for reg in registrations
            }

        # Get existing result for pre-population
        existing_result = EventResult.objects.filter(event=event).first()

        event_data.append({
            'event': event,
            'registrations': registrations,
            'selections': selections,
            'info': info,
            'existing_result': existing_result
        })

    if request.method == "POST":
        event_id = request.POST.get("event_id")
        winner_selection = request.POST.get(f"winner_{event_id}")
        runner_up_selection = request.POST.get(f"runner_up_{event_id}")

        # Validate distinct selections
        if winner_selection and runner_up_selection and winner_selection == runner_up_selection:
            messages.error(request, "Winner and runner-up cannot be the same.")
            return redirect('mark_results')

        try:
            event = Event.objects.get(id=event_id, club=club)
            result, created = EventResult.objects.get_or_create(event=event)
            
            # Handle winner and runner-up based on event type
            if event.is_group_event:
                result.winner_group_name = winner_selection if winner_selection else None
                result.runner_up_group_name = runner_up_selection if runner_up_selection else None
                if winner_selection:
                    leader = StudentRegistration.objects.filter(
                        event=event, group_name=winner_selection, is_leader=True, attended=True
                    ).first()
                    result.winner = leader if leader else None
                else:
                    result.winner = None
                if runner_up_selection:
                    leader = StudentRegistration.objects.filter(
                        event=event, group_name=runner_up_selection, is_leader=True, attended=True
                    ).first()
                    result.runner_up = leader if leader else None
                else:
                    result.runner_up = None
            else:
                result.winner_group_name = None
                result.runner_up_group_name = None
                if winner_selection:
                    registration = StudentRegistration.objects.get(
                        event=event, student__roll_no=winner_selection, attended=True
                    )
                    result.winner = registration
                else:
                    result.winner = None
                if runner_up_selection:
                    registration = StudentRegistration.objects.get(
                        event=event, student__roll_no=runner_up_selection, attended=True
                    )
                    result.runner_up = registration
                else:
                    result.runner_up = None

            result.save()
            messages.success(request, f"Results for {event.name} saved successfully.")
        except Event.DoesNotExist:
            messages.error(request, "Event not found or you don’t have permission.")
        except StudentRegistration.DoesNotExist:
            messages.error(request, "Invalid winner or runner-up selected.")
        except Exception as e:
            messages.error(request, f"Error saving results: {str(e)}")
        
        return redirect('mark_results')

    return render(request, 'vibes/mark_results.html', {
        'event_data': event_data,
        'club': club
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Club, EventResult, StudentRegistration

def view_results(request):
    club_id = request.session.get('club_id')
    if not club_id:
        messages.error(request, "Please log in to access this page.")
        return redirect('club_login')

    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        messages.error(request, "Invalid club session.")
        return redirect('club_login')

    # Fetch results with related data
    results = EventResult.objects.filter(event__club=club).select_related(
        'event',
        'winner__student',
        'runner_up__student'
    )

    # Prepare results with group members for group events
    results_with_members = []
    for result in results:
        result_data = {
            'result': result,
            'winner_group_members': [],
            'runner_up_group_members': []
        }
        if result.event.is_group_event:
            # Fetch group members for winner
            if result.winner_group_name:
                result_data['winner_group_members'] = StudentRegistration.objects.filter(
                    event=result.event,
                    group_name=result.winner_group_name
                ).select_related('student')
            # Fetch group members for runner-up
            if result.runner_up_group_name:
                result_data['runner_up_group_members'] = StudentRegistration.objects.filter(
                    event=result.event,
                    group_name=result.runner_up_group_name
                ).select_related('student')
        results_with_members.append(result_data)

    return render(request, 'vibes/view_results.html', {
        'results_with_members': results_with_members,
        'club': club
    })
from .models import Event, Club
from .forms import EventForm  

from django.shortcuts import render, redirect  #type: ignore
from .forms import EventForm
from .models import Club

def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            if 'club_id' in request.session:  # Ensure club is logged in
                club = Club.objects.get(id=request.session['club_id'])  # Get club from session
                event = form.save(commit=False)  # Don't save yet
                event.club = club  # Assign the logged-in club
                event.save()  # Save event with correct club
                return redirect('manage_events')  # Redirect to events page
            else:
                return render(request, 'vibes/add_event.html', {'form': form, 'error': 'You must be logged in as a club to add an event.'})
    else:
        form = EventForm()

    return render(request, 'vibes/add_event.html', {'form': form})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Event
from .forms import EventForm

def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if 'club_id' not in request.session or event.club.id != request.session['club_id']:
        return render(request, 'vibes/edit_event.html', {'event': event, 'error': 'You are not authorized to edit this event.'})

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('manage_events')
        else:
            return render(request, 'vibes/edit_event.html', {
                'form': form,
                'event': event,
                'error': 'Please correct the errors below.'
            })
    else:
        form = EventForm(instance=event)
        form.initial['has_price'] = bool(event.price)

    return render(request, 'vibes/edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure only the club that created the event can delete it
    if 'club_id' not in request.session or event.club.id != request.session['club_id']:
        return redirect('manage_events')  # Redirect if unauthorized

    event.delete()
    return redirect('manage_events')  # Redirect after deletion



from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from .models import Student, Event, StudentRegistration

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json
from .models import Event, Student, StudentRegistration  # Replace with your actual models

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('login')
    
    student_id = request.session['student_id']
    student = Student.objects.get(id=student_id)

    today = timezone.now().date()
    events = Event.objects.all()
    
    # Fetch registered events with payment verification status
    registered_events = StudentRegistration.objects.filter(student=student).select_related('event')
    registered_event_data = {
        reg.event_id: {
            'is_registered': True,
            'payment_verified': reg.payment_verified,
            'is_paid': reg.event.price is not None and reg.event.price > 0  # Handle None price safely
        } for reg in registered_events
    }

    # Attach registration and payment verification status to events
    for event in events:
        event_data = registered_event_data.get(event.id, {'is_registered': False, 'payment_verified': False, 'is_paid': False})
        event.is_registered = event_data['is_registered']
        event.payment_verified = event_data['payment_verified']
        event.is_paid = event_data['is_paid']

    return render(request, 'vibes/student_dashboard.html', {
        'student': student,
        'events': events
    })

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.utils import timezone
from twilio.rest import Client

def send_whatsapp_message(to_number, user_name, message):
    account_sid = 'your account_sid'
    auth_token = 'your auth_token'
    client = Client(account_sid, auth_token)

    msg_body = f"✅ Hello {user_name}! {message}"
    
    message = client.messages.create(
        body=msg_body,
        from_='whatsappnumber',
        to=f'whatsapp:+91{to_number}'
    )
    return message.sid

def register_event(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Not logged in'}, status=403)

    student = get_object_or_404(Student, id=request.session['student_id'])
    event = get_object_or_404(Event, id=event_id)

    if event.is_group_event:
        return JsonResponse({'error': 'This is a group event. Please use group registration.'}, status=400)

    if StudentRegistration.objects.filter(student=student, event=event).exists():
        return JsonResponse({'error': 'You are already registered for this event.'}, status=400)

    # Handle None price as free event
    event_price = event.price if event.price is not None else 0

    if event_price == 0:  # Free event
        registration = StudentRegistration(
            student=student,
            event=event,
            group_name=None,
            is_leader=False,
            utr=None,
            payment_verified=True,  # Must be True for free events
            transaction_date=None,
            transaction_time=None
        )
        registration.save()

        # Send WhatsApp notification for free event
        message = f"You have successfully registered for the event: {event.name}.\nClub:{event.club}"
        send_whatsapp_message(
            to_number=student.contact,  # Assuming Student model has phone_number field
            user_name=student.name,         # Assuming Student model has name field
            message=message
        )
       
        return JsonResponse({'message': 'Registration successful', 'status': 'success'})
    
    # Paid event (price > 0)
    utr = request.POST.get('utr', '').strip()
    transaction_date = request.POST.get('transaction_date')
    transaction_time = request.POST.get('transaction_time')

    if not utr or len(utr) != 12 or not utr.isdigit():
        return JsonResponse({'error': 'A valid 12-digit UTR number is required for paid events.'}, status=400)
    
    if StudentRegistration.objects.filter(utr=utr).exists():
        return JsonResponse({'error': 'This UTR number has already been used.'}, status=400)
    
    if not transaction_date or not transaction_time:
        return JsonResponse({'error': 'Transaction date and time are required for paid events when UTR is provided.'}, status=400)

    registration = StudentRegistration(
        student=student,
        event=event,
        group_name=None,
        is_leader=False,
        utr=utr,
        payment_verified=False
    )
    
    if transaction_date and transaction_time:
        transaction_datetime = timezone.make_aware(datetime.combine(
            datetime.strptime(transaction_date, '%Y-%m-%d').date(),
            datetime.strptime(transaction_time, '%H:%M').time()
        ))
        registration.transaction_date = transaction_datetime.date()
        registration.transaction_time = transaction_datetime.time()
    
    registration.save()

    # Send WhatsApp notification for paid event
    message = f"Your registration for the event: {event.name} has been submitted. Payment verification is pending."
    send_whatsapp_message(
        to_number=student.phone_number,
        user_name=student.name,
        message=message
    )

    return JsonResponse({'message': 'Registration submitted. Payment verification pending.', 'status': 'pending'})
# utils.py

import requests
from django.conf import settings
import logging

# twilio_utils.py

from twilio.rest import Client

    
import json
from django.shortcuts import render, get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from .models import Event, Student, StudentRegistration

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from .models import Event, Student, StudentRegistration

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .models import Event, Student, StudentRegistration
 
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from .models import Student, Event, StudentRegistration

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json
from .models import Event, Student, StudentRegistration  # Replace with your actual models

def group_registration(request, event_id):
    """
    Render the group registration page for the specified event.
    """
    if 'student_id' not in request.session:
        return redirect('login')

    student_id = request.session['student_id']
    student = get_object_or_404(Student, id=student_id)
    event = get_object_or_404(Event, id=event_id)
    
    if not event.is_group_event:
        return JsonResponse({'error': 'This is not a group event'}, status=400)

    return render(request, 'vibes/group_registration.html', {
        'event': event,
        'student': student
    })
def register_group_event(request, event_id):
    """
    Handle the group event registration submission.
    Ensures 'Verification Pending' for paid events, immediate success for free events,
    checks for duplicate group names across all events, and updates team members.
    Sends WhatsApp notifications to all group members upon registration.
    """
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == "POST":
        if 'student_id' not in request.session:
            return JsonResponse({'error': 'Not logged in'}, status=403)
        
        student = get_object_or_404(Student, id=request.session['student_id'])

        if not event.is_group_event:
            return JsonResponse({'error': 'This is not a group event'}, status=400)

        data = request.POST
        group_name = data.get('group_name', '').strip()
        leader_roll_no = student.roll_no  # Leader is the logged-in student
        teammates_roll_nos = json.loads(data.get('teammates', '[]'))

        # Handle None price as free event
        event_price = event.price if event.price is not None else 0

        # Validation for group name (applies to both free and paid events)
        if not group_name:
            return JsonResponse({'error': 'Group name is required.'}, status=400)

        # Check if group name exists across all events
        if StudentRegistration.objects.filter(group_name=group_name).exists():
            return JsonResponse({'error': 'This team name already exists. Please choose another team name.'}, status=400)

        # Validate team size (including leader)
        total_members = len(teammates_roll_nos) + 1  # +1 for the leader
        if total_members < event.min_members or total_members > event.max_members:
            return JsonResponse({'error': f'Team size must be between {event.min_members} and {event.max_members}.'}, status=400)

        # Check if all roll numbers exist in the Student database
        all_roll_nos = [leader_roll_no] + teammates_roll_nos
        existing_students = Student.objects.filter(roll_no__in=all_roll_nos)
        if existing_students.count() != len(all_roll_nos):
            invalid_roll_nos = set(all_roll_nos) - set(existing_students.values_list('roll_no', flat=True))
            return JsonResponse({'error': f'Invalid roll numbers: {", ".join(invalid_roll_nos)}'}, status=400)

        # Fetch teammates
        teammates = list(existing_students.exclude(roll_no=leader_roll_no))  # Exclude leader from teammates

        # Check for duplicate registrations for this event
        already_registered = StudentRegistration.objects.filter(event=event, student__roll_no__in=all_roll_nos)
        if already_registered.exists():
            registered_roll_nos = already_registered.values_list('student__roll_no', flat=True)
            return JsonResponse({'error': f'Students already registered for this event: {", ".join(registered_roll_nos)}'}, status=400)

        # Enforce same branch rule
        if event.same_branch_required and any(teammate.branch != student.branch for teammate in teammates):
            return JsonResponse({'error': 'All teammates must be from the same branch.'}, status=400)

        # For free events (price is None or 0)
        if event_price == 0:
            # Register the leader
            leader_registration = StudentRegistration.objects.create(
                student=student,
                event=event,
                group_name=group_name,
                is_leader=True,
                utr=None,
                transaction_date=None,
                transaction_time=None,
                payment_verified=True  # Free events are immediately verified
            )

            # Register teammates
            for teammate in teammates:
                StudentRegistration.objects.create(
                    student=teammate,
                    event=event,
                    group_name=group_name,
                    is_leader=False,
                    utr=None,
                    transaction_date=None,
                    transaction_time=None,
                    payment_verified=True  # Free events are immediately verified
                )

            # Send WhatsApp notifications to all group members
            for member in [student] + teammates:
                message = f"You have been successfully registered for the group event: {event.name} with group name: {group_name}."
                send_whatsapp_message(
                    to_number=member.phone_number,  # Assuming Student model has phone_number field
                    user_name=member.name,         # Assuming Student model has name field
                    message=message
                )

            return JsonResponse({
                'message': 'Group registration successful',
                'status': 'success'
            })

        # For paid events (price > 0)
        utr = data.get('utr', '').strip()
        transaction_date = data.get('transaction_date')
        transaction_time = data.get('transaction_time')

        if not utr or len(utr) != 12 or not utr.isdigit():
            return JsonResponse({'error': 'A valid 12-digit UTR number is required for paid events.'}, status=400)
        
        if StudentRegistration.objects.filter(utr=utr).exists():
            return JsonResponse({'error': 'This UTR number has already been used.'}, status=400)
        
        if not transaction_date or not transaction_time:
            return JsonResponse({'error': 'Transaction date and time are required for paid events when UTR is provided.'}, status=400)

        # Convert transaction date and time to timezone-aware datetime
        transaction_datetime = timezone.make_aware(datetime.combine(
            datetime.strptime(transaction_date, '%Y-%m-%d').date(),
            datetime.strptime(transaction_time, '%H:%M').time()
        ))
        transaction_date = transaction_datetime.date()
        transaction_time = transaction_datetime.time()

        # Register the leader
        leader_registration = StudentRegistration.objects.create(
            student=student,
            event=event,
            group_name=group_name,
            is_leader=True,
            utr=utr,
            transaction_date=transaction_date,
            transaction_time=transaction_time,
            payment_verified=False  # Paid events need verification
        )

        # Register teammates
        for teammate in teammates:
            StudentRegistration.objects.create(
                student=teammate,
                event=event,
                group_name=group_name,
                is_leader=False,
                utr=utr,
                transaction_date=transaction_date,
                transaction_time=transaction_time,
                payment_verified=False  # Paid events need verification
            )

        # Send WhatsApp notifications to all group members
        for member in [student] + teammates:
            message = f"Your group registration for the event: {event.name} with group name: {group_name} has been submitted. Payment verification is pending.\n\n{event.club}"
            send_whatsapp_message(
                to_number=member.contact,
                user_name=member.name,
                message=message
            )

        return JsonResponse({
            'message': 'Group registration submitted. Payment verification pending.',
            'status': 'pending'
        })

    # Render the template for GET requests
    student = get_object_or_404(Student, id=request.session['student_id'])
    context = {
        'event': event,
        'student': student,
    }
    return render(request, 'vibes/group_registration.html', context)
from django.shortcuts import get_object_or_404, redirect # type: ignore
from django.contrib import messages # type: ignore
from .models import Student, Event, StudentRegistration
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Event, StudentRegistration
import logging
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Event, StudentRegistration

logger = logging.getLogger(__name__)

def unregister_event(request, event_id):
    logger.debug(f"Unregister request for event_id: {event_id}, session student_id: {request.session.get('student_id')}")

    # Ensure the student is logged in
    if 'student_id' not in request.session:
        logger.warning("No student_id in session, redirecting to login")
        return redirect('login')

    student_id = request.session['student_id']
    student = get_object_or_404(Student, id=student_id)
    event = get_object_or_404(Event, id=event_id)

    # Check if the student is registered for this event
    registration = StudentRegistration.objects.filter(student=student, event=event).first()
    if not registration:
        logger.debug(f"No registration found for student {student_id} in event {event_id}")
        messages.error(request, "You are not registered for this event.")
        return redirect('registered_events')

    # Check if the event is a group event
    if event.is_group_event:
        # Check if the student is the leader
        if registration.is_leader:
            # Delete all registrations under the same group name
            StudentRegistration.objects.filter(event=event, group_name=registration.group_name).delete()
            logger.info(f"Group {registration.group_name} unregistered from event {event_id} by leader {student_id}")
            messages.success(request, "Group registration successfully removed.")
        else:
            # Remove only this student
            registration.delete()
            logger.info(f"Student {student_id} unregistered from group {registration.group_name} in event {event_id}")
            messages.success(request, "You have been unregistered from the group.")
    else:
        # For individual events, just remove the student
        registration.delete()
        logger.info(f"Student {student_id} unregistered from solo event {event_id}")
        messages.success(request, "You have been unregistered from the event.")

    logger.debug(f"Redirecting to registered_events after unregistration for event {event_id}")
    return redirect('registered_events')

def myprofile(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')  # Redirect to login if not authenticated

    try:
        student = Student.objects.get(id=student_id)
        return render(request, 'vibes/myprofile.html', {'student': student})
    except Student.DoesNotExist:
        return redirect('login')
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student  # Assuming Student model exists

def change_password(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Verify old password (plain text comparison)
        if old_password != student.password:
            messages.error(request, "Incorrect old password.")
            return redirect('change_password')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('change_password')

        # Validate new password (e.g., minimum length)
        if len(new_password) < 2:
            messages.error(request, "New password must be at least 8 characters long.")
            return redirect('change_password')

        # Update password (plain text)
        student.password = new_password
        student.save()
        messages.success(request, "Password changed successfully.")
        return redirect('myprofile')

    return render(request, 'vibes/change_password.html', {'student': student})

from .models import Student, StudentRegistration, Event  # Adjust based on your app structure
from django.utils import timezone # type: ignore
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Student, StudentRegistration

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Student, StudentRegistration  # Replace with your actual models

def registered_events(request):
    student_id = request.session.get('student_id')  # Get student_id from session
    
    if not student_id:
        # If not logged in, redirect to login page
        return redirect('login')  

    student = Student.objects.get(id=student_id)  # Fetch student object

    # Fetch registered events with registration details, sorted by date and time
    registered_event_objs = StudentRegistration.objects.filter(
        student=student
    ).select_related('event').order_by('event__date', 'event__time')
    
    # Filter for upcoming events, keeping the full registration objects
    registered_registrations = [
        reg for reg in registered_event_objs 
        if reg.event.date >= timezone.now().date()
    ]

    context = {
        'student': student,
        'registered_events': registered_registrations,  # Pass registration objects
    }
    return render(request, 'vibes/registered_events.html', context)
from vibes.models import Notification, Student
from django.shortcuts import render, redirect # type: ignore
from vibes.models import Notification, Student
from vibes.models import Notification, Student, StudentRegistration
def notifications(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')  # Redirect if student is not logged in

    try:
        student = Student.objects.get(id=student_id)

        # Get events the student registered for
        registered_events = StudentRegistration.objects.filter(student=student).values_list('event', flat=True)

        # Get notifications for those events
        student_notifications = Notification.objects.filter(event__in=registered_events).order_by('-timestamp')

        context = {
            'student': student,
        }

        if not student_notifications.exists():
            context['error'] = 'No notifications found'
        else:
            context['notifications'] = student_notifications

        return render(request, 'vibes/notifications.html', context)

    except Student.DoesNotExist:
        return render(request, 'vibes/notifications.html', {'error': 'Student not found'})


from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import Club, Event, Student, Notification
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging

def send_whatsapp_message(to_number, user_name, message):
    """
    Send a WhatsApp message to a single recipient.
    
    Args:
        to_number (str): Recipient's phone number (10-digit Indian number)
        user_name (str): Name of the recipient
        message (str): Message content
    
    Returns:
        str or None: Message SID if sent successfully, None if failed
    """
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    import logging

    logger = logging.getLogger(__name__)

    # Validate phone number format
    if not (to_number.isdigit() and len(to_number) == 10):
        logger.error(f"Invalid phone number format: {to_number}")
        return None

    # Twilio credentials
    account_sid = 'your account_sid'
    auth_token = 'your auth_token'
    whatsapp_number = 'whatsapp_number'

    try:
        client = Client(account_sid, auth_token)
        msg_body = f"✅ Hello {user_name}!\n{message}"
        message = client.messages.create(
            body=msg_body,
            from_=whatsapp_number,
            to=f'whatsapp:+91{to_number}'
        )
        logger.info(f"WhatsApp sent to {to_number}, SID: {message.sid}")
        return message.sid
    except TwilioRestException as e:
        logger.error(f"Twilio error sending WhatsApp to {to_number}: {e} (Status: {e.status}, Code: {e.code})")
        return None
    except Exception as e:
        logger.error(f"Unexpected error sending WhatsApp to {to_number}: {e}")
        return None
    

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Q
from .models import EventResult, StudentRegistration, Event
import os

# def generate_and_send_certificates(event_id):
#     try:
#         event_result = EventResult.objects.get(event_id=event_id)
#         event = event_result.event

#         # Get winner and runner-up details
#         winner_reg = event_result.winner
#         runner_up_reg = event_result.runner_up

#         # Generate and send winner certificate
#         if winner_reg:
#             winner_student = winner_reg.student
#             winner_group = winner_reg.group_name if event.is_group_event else None
#             subject = f"Certificate of Achievement - Winner - {event.name}"
#             body = render_to_string('vibes/winner_certificate.html', {
#                 'event_name': event.name,
#                 'recipient_name': winner_student.name,
#                 'event_date': event.date,
#                 'group_name': winner_group,
#                 'issue_date': event_result.declared_at.date()
#             })
#             email = EmailMessage(subject, body, to=[winner_student.email])
#             email.content_subtype = "html"
#             email.send()

#         # Generate and send runner-up certificate
#         if runner_up_reg:
#             runner_up_student = runner_up_reg.student
#             runner_up_group = runner_up_reg.group_name if event.is_group_event else None
#             subject = f"Certificate of Achievement - Runner-Up - {event.name}"
#             body = render_to_string('vibes/runner_up_certificate.html', {
#                 'event_name': event.name,
#                 'recipient_name': runner_up_student.name,
#                 'event_date': event.date,
#                 'group_name': runner_up_group,
#                 'issue_date': event_result.declared_at.date()
#             })
#             email = EmailMessage(subject, body, to=[runner_up_student.email])
#             email.content_subtype = "html"
#             email.send()

#         # Generate and send participation certificates for other attendees
#         participants = StudentRegistration.objects.filter(
#             event=event,
#             attended=True
#         ).exclude(
#             Q(id=winner_reg.id) if winner_reg else Q(),
#             Q(id=runner_up_reg.id) if runner_up_reg else Q()
#         )
#         for participant in participants:
#             student = participant.student
#             group_name = participant.group_name if event.is_group_event else None
#             subject = f"Certificate of Participation - {event.name}"
#             body = render_to_string('vibes/participation_certificate.html', {
#                 'event_name': event.name,
#                 'recipient_name': student.name,
#                 'event_date': event.date,
#                 'group_name': group_name,
#                 'issue_date': event_result.declared_at.date()
#             })
#             email = EmailMessage(subject, body, to=[student.email])
#             email.content_subtype = "html"
#             email.send()

#     except EventResult.DoesNotExist:
#         raise ValueError("Event result not found for the given event ID.")
#     except Exception as e:
#         raise Exception(f"Error generating or sending certificates: {str(e)}")

# def generate_certificates_view(request):
#     completed_events = Event.objects.filter(is_completed=True)
#     if request.method == 'POST':
#         event_id = request.POST.get('event_id')
#         if event_id:
#             try:
#                 event_result = get_object_or_404(EventResult, event_id=event_id)
#                 generate_and_send_certificates(event_id)
#                 messages.success(request, f"Certificates for event '{event_result.event.name}' have been generated and sent successfully!")
#             except Exception as e:
#                 messages.error(request, f"Error: {str(e)}")
#         return redirect('generate_certificates')
#     return render(request, 'vibes/generate_certificates.html', {'completed_events': completed_events})
# vibes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Q
from .models import EventResult, StudentRegistration, Event
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os

def generate_and_send_certificates(event_id):
    try:
        event_result = EventResult.objects.get(event_id=event_id)
        event = event_result.event

        # Get winner and runner-up details
        winner_reg = event_result.winner
        runner_up_reg = event_result.runner_up

        # Generate and send winner certificate
        if winner_reg:
            winner_student = winner_reg.student
            winner_group = winner_reg.group_name if event.is_group_event else None
            subject = f"Certificate of Achievement - Winner - {event.name}"
            body = render_to_string('vibes/winner_certificate.html', {
                'event_name': event.name,
                'recipient_name': winner_student.name,
                'event_date': event.date,
                'group_name': winner_group,
                'issue_date': event_result.declared_at.date()
            })
            email = EmailMessage(subject, body, to=[winner_student.email])
            email.content_subtype = "html"
            email.send()

        # Generate and send runner-up certificate
        if runner_up_reg:
            runner_up_student = runner_up_reg.student
            runner_up_group = runner_up_reg.group_name if event.is_group_event else None
            subject = f"Certificate of Achievement - Runner-Up - {event.name}"
            body = render_to_string('vibes/runner_up_certificate.html', {
                'event_name': event.name,
                'recipient_name': runner_up_student.name,
                'event_date': event.date,
                'group_name': runner_up_group,
                'issue_date': event_result.declared_at.date()
            })
            email = EmailMessage(subject, body, to=[runner_up_student.email])
            email.content_subtype = "html"
            email.send()

        # Generate and send participation certificates for other attendees
        participants = StudentRegistration.objects.filter(
            event=event,
            attended=True
        ).exclude(
            Q(id=winner_reg.id) if winner_reg else Q(),
            Q(id=runner_up_reg.id) if runner_up_reg else Q()
        )
        for participant in participants:
            student = participant.student
            group_name = participant.group_name if event.is_group_event else None
            subject = f"Certificate of Participation - {event.name}"
            body = render_to_string('vibes/participation_certificate.html', {
                'event_name': event.name,
                'recipient_name': student.name,
                'event_date': event.date,
                'group_name': group_name,
                'issue_date': event_result.declared_at.date()
            })
            email = EmailMessage(subject, body, to=[student.email])
            email.content_subtype = "html"
            email.send()

    except EventResult.DoesNotExist:
        raise ValueError("Event result not found for the given event ID.")
    except Exception as e:
        raise Exception(f"Error generating or sending certificates: {str(e)}")
# vibes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Q
from .models import EventResult, StudentRegistration, Event
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os
# vibes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Q
from .models import EventResult, StudentRegistration, Event
import os

# def generate_and_send_certificates(event_id):
#     try:
#         event_result = EventResult.objects.get(event_id=event_id)
#         event = event_result.event

#         # Get winner and runner-up details
#         winner_reg = event_result.winner
#         runner_up_reg = event_result.runner_up

#         # Generate and send winner certificate
#         if winner_reg:
#             winner_student = winner_reg.student
#             winner_group = winner_reg.group_name if event.is_group_event else None
#             subject = f"Certificate of Achievement - Winner - {event.name}"
#             body = render_to_string('vibes/winner_certificate.html', {
#                 'event_name': event.name,
#                 'recipient_name': winner_student.name,
#                 'event_date': event.date,
#                 'group_name': winner_group,
#                 'issue_date': event_result.declared_at.date()
#             })
#             email = EmailMessage(subject, body, to=[winner_student.email])
#             email.content_subtype = "html"
#             email.send()

#         # Generate and send runner-up certificate
#         if runner_up_reg:
#             runner_up_student = runner_up_reg.student
#             runner_up_group = runner_up_reg.group_name if event.is_group_event else None
#             subject = f"Certificate of Achievement - Runner-Up - {event.name}"
#             body = render_to_string('vibes/runner_up_certificate.html', {
#                 'event_name': event.name,
#                 'recipient_name': runner_up_student.name,
#                 'event_date': event.date,
#                 'group_name': runner_up_group,
#                 'issue_date': event_result.declared_at.date()
#             })
#             email = EmailMessage(subject, body, to=[runner_up_student.email])
#             email.content_subtype = "png"
#             email.send()

#         # Generate and send participation certificates for other attendees
#         participants = StudentRegistration.objects.filter(
#             event=event,
#             attended=True
#         ).exclude(
#             Q(id=winner_reg.id) if winner_reg else Q(),
#             Q(id=runner_up_reg.id) if runner_up_reg else Q()
#         )
#         for participant in participants:
#             student = participant.student
#             group_name = participant.group_name if event.is_group_event else None
#             subject = f"Certificate of Participation - {event.name}"
#             body = render_to_string('vibes/participation_certificate.html', {
#                 'event_name': event.name,
#                 'recipient_name': student.name,
#                 'event_date': event.date,
#                 'group_name': group_name,
#                 'issue_date': event_result.declared_at.date()
#             })
#             email = EmailMessage(subject, body, to=[student.email])
#             email.content_subtype = "html"
#             email.send()

#     except EventResult.DoesNotExist:
#         raise ValueError("Event result not found for the given event ID.")
#     except Exception as e:
#         raise Exception(f"Error generating or sending certificates: {str(e)}")

# def generate_certificates_view(request):
#     completed_events = Event.objects.filter(is_completed=True)
#     if request.method == 'POST':
#         event_id = request.POST.get('event_id')
#         if event_id:
#             try:
#                 event_result = get_object_or_404(EventResult, event_id=event_id)
#                 generate_and_send_certificates(event_id)
#                 messages.success(request, f"Certificates for event '{event_result.event.name}' have been generated and sent successfully!")
#             except Exception as e:
#                 messages.error(request, f"Error: {str(e)}")
#         return redirect('generate_certificates')
#     return render(request, 'vibes/generate_certificates.html', {'completed_events': completed_events})
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
from django.conf import settings

# def generate_and_send_certificates(event_id):
#     try:
#         event_result = EventResult.objects.get(event_id=event_id)
#         event = event_result.event

#         # Get winner and runner-up details
#         winner_reg = event_result.winner
#         runner_up_reg = event_result.runner_up

#         # Function to generate certificate image
#         def create_certificate(recipient_name, event_name, event_date, issue_date, certificate_type="Winner"):
#             # Image dimensions based on the sample (approx. 800x600 pixels)
#             width, height = 800, 600
#             image = Image.new('RGB', (width, height), color=(255, 255, 255))  # White background
#             draw = ImageDraw.Draw(image)

#             # Define fonts (use default or specify a .ttf file)
#             try:
#                 title_font = ImageFont.truetype("arial.ttf", 40)
#                 text_font = ImageFont.truetype("arial.ttf", 20)
#             except:
#                 title_font = ImageFont.load_default()
#                 text_font = ImageFont.load_default()

#             # Draw border (yellow as per sample)
#             draw.rectangle([(0, 0), (width-1, height-1)], outline=(255, 215, 0), width=10)

#             # Add institute logo or text (simulated as text for simplicity)
#             institute_text = "Mahatma Gandhi Institute of Technology\nGandipet, Telangana"
#             draw.text((50, 50), institute_text, fill=(0, 0, 255), font=title_font)

#             # Add certificate title
#             title = f"Certificate of Achievement\n{certificate_type}"
#             draw.text((300, 150), title, fill=(0, 100, 0), font=title_font)

#             # Add recipient name
#             draw.text((300, 250), f"[ {recipient_name} ]", fill=(0, 0, 0), font=text_font)

#             # Add description
#             description = (f"This certificate is proudly awarded to {recipient_name} for securing the "
#                           f"First Position in {event_name} held on {event_date}. Your outstanding "
#                           f"performance and dedication are truly commendable.")
#             wrapped_text = textwrap.fill(description, width=50)
#             draw.text((50, 350), wrapped_text, fill=(0, 0, 0), font=text_font)

#             # Add date
#             draw.text((600, 500), f"Date: {issue_date}", fill=(0, 0, 0), font=text_font)

#             # Save image to bytes buffer
#             buffer = io.BytesIO()
#             image.save(buffer, format="PNG")
#             buffer.seek(0)
#             return buffer

#         # Generate and send winner certificate
#         if winner_reg:
#             winner_student = winner_reg.student
#             winner_group = winner_reg.group_name if event.is_group_event else None
#             subject = f"Certificate of Achievement - Winner - {event.name}"
#             image_buffer = create_certificate(
#                 winner_student.name, event.name, event.date, event_result.declared_at.date(), "Winner"
#             )
#             email = EmailMessage(subject, "Please find your certificate attached.", to=[winner_student.email])
#             email.attach('certificate_winner.png', image_buffer.getvalue(), 'image/png')
#             email.send()

#         # Generate and send runner-up certificate
#         if runner_up_reg:
#             runner_up_student = runner_up_reg.student
#             runner_up_group = runner_up_reg.group_name if event.is_group_event else None
#             subject = f"Certificate of Achievement - Runner-Up - {event.name}"
#             image_buffer = create_certificate(
#                 runner_up_student.name, event.name, event.date, event_result.declared_at.date(), "Runner-Up"
#             )
#             email = EmailMessage(subject, "Please find your certificate attached.", to=[runner_up_student.email])
#             email.attach('certificate_runnerup.png', image_buffer.getvalue(), 'image/png')
#             email.send()

#         # Generate and send participation certificates for other attendees
#         participants = StudentRegistration.objects.filter(
#             event=event,
#             attended=True
#         ).exclude(
#             Q(id=winner_reg.id) if winner_reg else Q(),
#             Q(id=runner_up_reg.id) if runner_up_reg else Q()
#         )
#         for participant in participants:
#             student = participant.student
#             group_name = participant.group_name if event.is_group_event else None
#             subject = f"Certificate of Participation - {event.name}"
#             image_buffer = create_certificate(
#                 student.name, event.name, event.date, event_result.declared_at.date(), "Participation"
#             )
#             email = EmailMessage(subject, "Please find your certificate attached.", to=[student.email])
#             email.attach('certificate_participation.png', image_buffer.getvalue(), 'image/png')
#             email.send()

#     except EventResult.DoesNotExist:
#         raise ValueError("Event result not found for the given event ID.")
#     except Exception as e:
#         raise Exception(f"Error generating or sending certificates: {str(e)}")

# def generate_certificates_view(request):
#     completed_events = Event.objects.filter(is_completed=True)
#     if request.method == 'POST':
#         event_id = request.POST.get('event_id')
#         if event_id:
#             try:
#                 event_result = get_object_or_404(EventResult, event_id=event_id)
#                 generate_and_send_certificates(event_id)
#                 messages.success(request, f"Certificates for event '{event_result.event.name}' have been generated and sent successfully!")
#             except Exception as e:
#                 messages.error(request, f"Error: {str(e)}")
#         return redirect('generate_certificates')
#     return render(request, 'vibes/generate_certificates.html', {'completed_events': completed_events})
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.contrib import messages
from django.db.models import Q
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
from django.conf import settings

def generate_and_send_certificates(event_id):
    try:
        event_result = EventResult.objects.get(event_id=event_id)
        event = event_result.event

        # Get winner and runner-up details
        winner_reg = event_result.winner
        runner_up_reg = event_result.runner_up

        # Function to generate certificate image
        def create_certificate(recipient_name, event_name, event_date, issue_date, certificate_type="Winner"):
            # Image dimensions based on the sample (approx. 800x600 pixels)
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color=(255, 255, 255))  # White background
            draw = ImageDraw.Draw(image)

            # Define fonts (use default or specify a .ttf file)
            try:
                clg_font = ImageFont.truetype("arial.ttf", 40)  # Reduced from 50 to 40
                title_font = ImageFont.truetype("arial.ttf", 40)
                text_font = ImageFont.truetype("arial.ttf", 20)
            except:
                clg_font = ImageFont.load_default()
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()

            # Draw yellow border as per sample
            draw.rectangle([(0, 0), (width-1, height-1)], outline=(255, 215, 0), width=10)

            # Add college name in large, light font centered at the top
            clg_name = "Mahatma Gandhi Institute of Technology\nGandipet, Telangana"
            clg_lines = clg_name.split('\n')
            y_clg = 60
            for line in clg_lines:
                clg_width = draw.textlength(line, font=clg_font)
                draw.text(((width - clg_width) / 2, y_clg), line, fill=(173, 216, 230), font=clg_font)  # Reverted to light blue
                y_clg += 50  # Adjusted line spacing for reduced font size

            # Add certificate title (centered)
            title = "Certificate of Achievement"
            title_width = draw.textlength(title, font=title_font)
            draw.text(((width - title_width) / 2, 250), title, fill=(0, 100, 0), font=title_font)

            # Add certificate type (e.g., Winner, centered)
            type_text = certificate_type
            type_width = draw.textlength(type_text, font=title_font)
            draw.text(((width - type_width) / 2, 300), type_text, fill=(255, 215, 0), font=title_font)

            # Add recipient name (centered)
            draw.text(((width - draw.textlength(f"[ {recipient_name} ]", font=text_font)) / 2, 350),
                     f"[ {recipient_name} ]", fill=(0, 0, 0), font=text_font)

            # Add description (centered and wrapped)
            description = (f"This certificate is proudly awarded to {recipient_name} for securing the "
                          f"First Position in {event_name} held on {event_date}. Your outstanding "
                          f"performance and dedication are truly commendable.")
            wrapped_text = textwrap.fill(description, width=50)
            y_text = 400
            for line in wrapped_text.split('\n'):
                line_width = draw.textlength(line, font=text_font)
                draw.text(((width - line_width) / 2, y_text), line, fill=(0, 0, 0), font=text_font)
                y_text += 30

            # Add date (bottom-right)
            draw.text((600, 550), f"Date: {issue_date}", fill=(0, 0, 0), font=text_font)

            # Save image to bytes buffer
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer

        # Generate and send winner certificate
        if winner_reg:
            winner_student = winner_reg.student
            winner_group = winner_reg.group_name if event.is_group_event else None
            subject = f"Certificate of Achievement - Winner - {event.name}"
            image_buffer = create_certificate(
                winner_student.name, event.name, event.date, event_result.declared_at.date(), "Winner"
            )
            email = EmailMessage(subject, "Please find your certificate attached.", to=[winner_student.email])
            email.attach('certificate_winner.png', image_buffer.getvalue(), 'image/png')
            email.send()

        # Generate and send runner-up certificate
        if runner_up_reg:
            runner_up_student = runner_up_reg.student
            runner_up_group = runner_up_reg.group_name if event.is_group_event else None
            subject = f"Certificate of Achievement - Runner-Up - {event.name}"
            image_buffer = create_certificate(
                runner_up_student.name, event.name, event.date, event_result.declared_at.date(), "Runner-Up"
            )
            email = EmailMessage(subject, "Please find your certificate attached.", to=[runner_up_student.email])
            email.attach('certificate_runnerup.png', image_buffer.getvalue(), 'image/png')
            email.send()

        # Generate and send participation certificates for other attendees
        participants = StudentRegistration.objects.filter(
            event=event,
            attended=True
        ).exclude(
            Q(id=winner_reg.id) if winner_reg else Q(),
            Q(id=runner_up_reg.id) if runner_up_reg else Q()
        )
        for participant in participants:
            student = participant.student
            group_name = participant.group_name if event.is_group_event else None
            subject = f"Certificate of Participation - {event.name}"
            image_buffer = create_certificate(
                student.name, event.name, event.date, event_result.declared_at.date(), "Participation"
            )
            email = EmailMessage(subject, "Please find your certificate attached.", to=[student.email])
            email.attach('certificate_participation.png', image_buffer.getvalue(), 'image/png')
            email.send()

    except EventResult.DoesNotExist:
        raise ValueError("Event result not found for the given event ID.")
    except Exception as e:
        raise Exception(f"Error generating or sending certificates: {str(e)}")

def generate_certificates_view(request):
    completed_events = Event.objects.filter(is_completed=True)
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        if event_id:
            try:
                event_result = get_object_or_404(EventResult, event_id=event_id)
                generate_and_send_certificates(event_id)
                messages.success(request, f"Certificates for event '{event_result.event.name}' have been generated and sent successfully!")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        return redirect('generate_certificates')
    return render(request, 'vibes/generate_certificates.html', {'completed_events': completed_events})