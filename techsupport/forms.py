from django import forms
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket

# This is a form class named TicketCreateForm that inherits from the forms.Form class.
# It provides fields for creating a new support ticket, including the ticket's category,
# subcategory, title, description, priority level, center, and region.


class TicketCreateForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    subcategory = forms.ModelChoiceField(queryset=SubCategory.objects.all())
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    priority = forms.ChoiceField(choices=SupportTicket.Priority.choices)
    centre = forms.ModelChoiceField(queryset=Centre.objects.all())


# Form for updating a support ticket


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        # Fields to be updated
        fields = (
            "category",
            "subcategory",
            "title",
            "description",
            "priority",
            "centre",
        )


# Form for updating the description of a support ticket


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        # Fields to be updated
        fields = ("description",)
        # Field widget to display description with 5 rows
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}
