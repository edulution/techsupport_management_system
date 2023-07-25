from django import forms
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket, UserProfile, User
from django.core.validators import ValidationError
from django.shortcuts import get_object_or_404


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'centre', 'category', 'subcategory', 'priority']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user.centres.count() == 1:
            self.fields['centre'].initial = user.centres.first().pk
            self.fields['centre'].widget = forms.HiddenInput()

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if len(title) > 20:
            raise ValidationError("Title should not exceed 20 characters.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) > 100:
            raise ValidationError("Description should not exceed 100 characters.")
        return description


class TicketAssignmentForm(forms.Form):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.filter(role='technician'))


# Form for updating the description of a support ticket
class SupportTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["title", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["readonly"] = True

    def clean_title(self):
        return self.instance.title


class TicketResolutionForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = SupportTicket
        fields = ('status', 'resolution_notes',)
        widgets = {
            'resolution_notes': forms.Textarea(attrs={'rows': 4}),
        }



class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'date_of_birth']
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'role', 'is_active', 'is_staff', 'centres']
