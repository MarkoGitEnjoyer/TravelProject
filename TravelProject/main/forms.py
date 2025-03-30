from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["first_name", "last_name", "phone", "email", "notes"]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any special requests or information you\'d like us to know?'})
        }