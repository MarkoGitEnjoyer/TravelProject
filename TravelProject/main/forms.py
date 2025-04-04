from django import forms
from .models import Registration
from django.core.validators import RegexValidator

# List of country codes with their names
COUNTRY_CODES = [
    ('+1', 'United States/Canada (+1)'),
    ('+44', 'United Kingdom (+44)'),
    ('+49', 'Germany (+49)'),
    ('+33', 'France (+33)'),
    ('+61', 'Australia (+61)'),
    ('+81', 'Japan (+81)'),
    ('+86', 'China (+86)'),
    ('+91', 'India (+91)'),
    ('+52', 'Mexico (+52)'),
    ('+55', 'Brazil (+55)'),
    ('+39', 'Italy (+39)'),
    ('+34', 'Spain (+34)'),
    ('+7', 'Russia (+7)'),
    ('+82', 'South Korea (+82)'),
    ('+31', 'Netherlands (+31)'),
    ('+90', 'Turkey (+90)'),
    ('+972', 'Israel (+972)'),
    # Add more country codes as needed
]

class RegistrationForm(forms.ModelForm):
    country_code = forms.ChoiceField(
        choices=COUNTRY_CODES,
        initial='+972',  # Default to Israel
        label="Country Code"
    )
    
    phone_number = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='Phone number must contain only digits'
            )
        ],
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number without country code'})
    )
    
    class Meta:
        model = Registration
        fields = ["first_name", "last_name", "email", "notes"]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any special requests or information you\'d like us to know?'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        country_code = cleaned_data.get('country_code')
        phone_number = cleaned_data.get('phone_number')
        
        # Combine country code and phone number
        if country_code and phone_number:
            # Store the combined number in the phone field of the model
            cleaned_data['phone'] = f"{country_code}{phone_number}"
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Get the combined phone number from cleaned_data
        if 'phone' in self.cleaned_data:
            instance.phone = self.cleaned_data['phone']
        
        if commit:
            instance.save()
        
        return instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If we're editing an existing registration with a phone number
        if 'instance' in kwargs and kwargs['instance']:
            instance = kwargs['instance']
            # Try to split the phone into country code and number
            # This is a simple implementation and might need adjustment
            if instance.phone:
                for code, _ in COUNTRY_CODES:
                    if instance.phone.startswith(code):
                        self.initial['country_code'] = code
                        self.initial['phone_number'] = instance.phone[len(code):]
                        break