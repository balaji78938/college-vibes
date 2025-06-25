from django import forms # type: ignore
from .models import Club

class ClubForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))  # Hide password input

    class Meta:
        model = Club
        fields = ["name", "block", "club_head_name", "contact_number", "email", "username", "password"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Club Name"}),
            "block": forms.TextInput(attrs={"class": "form-control", "placeholder": "College Block"}),
            "club_head_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Club Head Name"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contact Number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Club Username"}),
        }
from django import forms # type: ignore
from .models import Event

from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    has_price = forms.BooleanField(required=False, label="Does this event have a price?")
    is_group_event = forms.BooleanField(required=False, label="Group Event")
    same_branch_required = forms.BooleanField(required=False, label="Same Branch Required")
    is_completed = forms.BooleanField(required=False, label="Is Completed")

    class Meta:
        model = Event
        fields = [
            'name', 'date', 'time', 'venue', 'registration_deadline', 'description', 
            'poster', 'has_price', 'price', 'qr_code', 'is_group_event', 
            'min_members', 'max_members', 'same_branch_required', 'is_completed'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Event Name'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Venue'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Event Description'}),
            'poster': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'qr_code': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'min_members': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            
        }

    def clean(self):
        cleaned_data = super().clean()
        has_price = cleaned_data.get('has_price')
        price = cleaned_data.get('price')
        qr_code = cleaned_data.get('qr_code')
        is_group_event = cleaned_data.get('is_group_event')
        min_members = cleaned_data.get('min_members')
        max_members = cleaned_data.get('max_members')

        # Validation for price and QR code
        if has_price:
            if not price:
                self.add_error('price', 'Price is required if the event has a price.')
            if not qr_code and not self.instance.qr_code:  # Check if no new QR code and no existing one
                self.add_error('qr_code', 'QR code is required if the event has a price.')

        # Validation for group event
        if is_group_event:
            if not min_members:
                self.add_error('min_members', 'Minimum members are required for a group event.')
            if not max_members:
                self.add_error('max_members', 'Maximum members are required for a group event.')
            if min_members and max_members and min_members > max_members:
                self.add_error('max_members', 'Maximum members must be greater than or equal to minimum members.')

        return cleaned_data
# forms.py
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Upload CSV or Excel file',
        help_text='Supported formats: .csv, .xls, .xlsx',
        widget=forms.FileInput(attrs={'accept': '.csv,.xls,.xlsx'})
    )