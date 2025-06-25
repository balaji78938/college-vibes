from django.db import models # type: ignore

from django.contrib.auth.hashers import make_password # type: ignore

class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Club Name
    block = models.CharField(max_length=50)
    club_head_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)  # Club Login Username
    password = models.CharField(max_length=100)  # Store hashed password later

    def __str__(self):
        return self.name  # Shows club name when printed

from datetime import timedelta, datetime, time
from django.db import models

from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    venue = models.CharField(max_length=200)
    time = models.TimeField(default=time(12, 0))  # Default to 12:00 PM
    description = models.TextField()
    poster = models.ImageField(upload_to='event_posters/', null=True, blank=True)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    is_group_event = models.BooleanField(default=False)
    min_members = models.PositiveIntegerField(null=True, blank=True)
    max_members = models.PositiveIntegerField(null=True, blank=True)
    same_branch_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='event_qrcodes/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_completed = models.BooleanField(default=False)  # New field

    def save(self, *args, **kwargs):
        if self.date and self.time:
            # Create a timezone-aware datetime for the event
            event_datetime = timezone.make_aware(
                datetime.combine(self.date, self.time),
                timezone.get_default_timezone()
            )
            # Ensure registration_deadline is updated dynamically
            self.registration_deadline = event_datetime - timedelta(days=1)

            # Mark event as completed if the date has passed
            if timezone.now() >= event_datetime + timedelta(days=1):
                self.is_completed = True
            else:
                self.is_completed = False

        super().save(*args, **kwargs)

    def clean(self):
        if self.min_members is not None and self.max_members is not None:
            if self.min_members > self.max_members:
                raise ValidationError("Minimum members cannot be greater than maximum members.")
        if self.registration_deadline and self.date and self.time:
            event_datetime = timezone.make_aware(
                datetime.combine(self.date, self.time),
                timezone.get_default_timezone()
            )
            if self.registration_deadline >= event_datetime:
                raise ValidationError("Registration deadline must be before the event date and time.")

    def __str__(self):
        return self.name


class Student(models.Model):
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=50)
    password = models.CharField(max_length=255)  # Store hashed passwords
    contact = models.CharField(max_length=10)
    college = models.CharField(max_length=100)
    email = models.EmailField(unique=True)


    def __str__(self):
        return self.name
    
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
class StudentRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=200, null=True, blank=True)
    is_leader = models.BooleanField(default=False)
    utr = models.CharField(max_length=12, null=True, blank=True)
    transaction_date = models.DateField(null=True, blank=True)
    transaction_time = models.TimeField(null=True, blank=True)
    payment_verified = models.BooleanField(default=False)
    attended = models.BooleanField(default=False)  # New field

    def clean(self):
        event_price = self.event.price if self.event.price is not None else 0

        if self.event.is_group_event:
            if not self.group_name:
                raise ValidationError("Group events require a group name.")

            group_members = StudentRegistration.objects.filter(event=self.event, group_name=self.group_name)
            leader_count = group_members.filter(is_leader=True).count()

            if self.is_leader and leader_count > 0 and not (leader_count == 1 and self.pk and group_members.filter(pk=self.pk, is_leader=True).exists()):
                raise ValidationError("Only one leader is allowed per group.")

            if group_members.exclude(pk=self.pk).count() >= self.event.max_members:
                raise ValidationError(f"Maximum {self.event.max_members} members allowed in a group.")

            if self.event.same_branch_required:
                leader = group_members.filter(is_leader=True).first()
                if leader and leader.student.branch != self.student.branch:
                    raise ValidationError("All group members must be from the same branch.")
        else:
            if self.group_name:
                raise ValidationError("Solo events cannot have a group name.")

        if event_price > 0:
            if not self.utr:
                raise ValidationError("UTR is required for paid events.")
            if not self.transaction_date or not self.transaction_time:
                raise ValidationError("Transaction date and time are required for paid events when UTR is provided.")
            if self.transaction_date > timezone.now().date():
                raise ValidationError("Transaction date cannot be in the future.")
            if self.payment_verified and not self.utr:
                raise ValidationError("Payment cannot be verified without a valid UTR.")
        else:
            if self.utr or self.transaction_date or self.transaction_time:
                raise ValidationError("Transaction details are not applicable for free events.")

    def save(self, *args, **kwargs):
        event_price = self.event.price if self.event.price is not None else 0
        if event_price == 0:
            self.payment_verified = True
            self.utr = None
            self.transaction_date = None
            self.transaction_time = None

        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.group_name:
            return f"{self.student.name} ({'Leader' if self.is_leader else 'Member'}) - {self.event.name} [{self.group_name}]"
        return f"{self.student.name} - {self.event.name}"
    
    
from django.db import models # type: ignore

class Notification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    sender = models.ForeignKey(Club, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(Student, related_name="notifications")

    def __str__(self):
        return f"Notification for {self.event.name} by {self.sender.name}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class EventResult(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='results')
    winner = models.ForeignKey(
        'StudentRegistration',
        on_delete=models.CASCADE,
        related_name='winner_results',
        null=True,
        blank=True
    )
    runner_up = models.ForeignKey(
        'StudentRegistration',
        on_delete=models.CASCADE,
        related_name='runner_up_results',
        null=True,
        blank=True
    )
    winner_group_name = models.CharField(max_length=200, null=True, blank=True)
    runner_up_group_name = models.CharField(max_length=200, null=True, blank=True)
    declared_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Ensure the event is completed
        if not self.event.is_completed:
            raise ValidationError("Results can only be declared for completed events.")

        # Validate solo vs. group event
        if self.event.is_group_event:
            # For group events, group names must be provided
            if not self.winner_group_name or not self.runner_up_group_name:
                raise ValidationError("Group events require winner and runner-up group names.")
            # Ensure winner and runner-up registrations match the group names
            if self.winner and self.winner.group_name != self.winner_group_name:
                raise ValidationError("Winner's group name does not match the provided group.")
            if self.runner_up and self.runner_up.group_name != self.runner_up_group_name:
                raise ValidationError("Runner-up's group name does not match the provided group.")
            # Ensure winner and runner-up are part of the event
            if self.winner and self.winner.event != self.event:
                raise ValidationError("Winner must be registered for this event.")
            if self.runner_up and self.runner_up.event != self.event:
                raise ValidationError("Runner-up must be registered for this event.")
        else:
            # For solo events, group names should not be provided
            if self.winner_group_name or self.runner_up_group_name:
                raise ValidationError("Solo events cannot have group names.")
            # Ensure winner and runner-up are registered and attended
            if self.winner and (self.winner.event != self.event or not self.winner.attended):
                raise ValidationError("Winner must be a registered and attended participant of this event.")
            if self.runner_up and (self.runner_up.event != self.event or not self.runner_up.attended):
                raise ValidationError("Runner-up must be a registered and attended participant of this event.")
            # Prevent same winner and runner-up
            if self.winner and self.runner_up and self.winner == self.runner_up:
                raise ValidationError("Winner and runner-up cannot be the same participant.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Results for {self.event.name}"