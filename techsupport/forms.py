from django import forms
from django.core.validators import ValidationError
from django.shortcuts import get_object_or_404
from .models import (
    Country,
    Region,
    Centre,
    Category,
    SubCategory,
    SupportTicket,
    UserProfile,
    User,
)


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = [
            "title",
            "description",
            "centre",
            "category",
            "subcategory",
            "priority",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user.centres.count() == 1:
            self.fields["centre"].queryset = user.centres.all()
            self.fields["centre"].initial = user.centres.first()
            
        if user.role == ['technician','admin']:
            self.fields["priority"].initial = "medium"
        else:
            self.fields["priority"].widget = forms.HiddenInput()

    def clean_title(self):
        title = self.cleaned_data.get("title", None)
        if title is None or len(title.strip()) == 0:
            raise forms.ValidationError("Title is required.")
        elif len(title) > 20:
            raise forms.ValidationError("Title should not exceed 20 characters.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description", None)
        if description is None or len(description.strip()) == 0:
            raise forms.ValidationError("Description is required.")
        elif len(description) > 100:
            raise forms.ValidationError("Description should not exceed 100 characters.")
        return description

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        description = cleaned_data.get("description")

        if not title and not description:
            raise forms.ValidationError("Title and Description are required.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = "Open"
        if commit:
            instance.save()
        return instance


class TicketAssignmentForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(role="technician")
    )


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
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = SupportTicket
        fields = (
            "status",
            "resolution_notes",
        )
        widgets = {
            "resolution_notes": forms.Textarea(attrs={"rows": 4}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "avatar", "date_of_birth"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "role", "is_active", "is_staff", "centres"]
