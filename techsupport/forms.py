from django import forms
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket, UserProfile, User
from django.core.validators import MaxLengthValidator


class TicketCreateForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    subcategory = forms.ModelChoiceField(queryset=SubCategory.objects.all())
    title = forms.CharField(max_length=100, validators=[MaxLengthValidator(50)])
    description = forms.CharField(widget=forms.Textarea, validators=[MaxLengthValidator(100)])
    centre = forms.ModelChoiceField(queryset=Centre.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        if user.centres.count() == 1:
            self.fields['centre'].initial = user.centres.first()


# Form for updating a support ticket

class SupportTicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if user.centres.count() == 1:
            self.fields['centre'].initial = user.centres.first()

        self.fields['subcategory'].queryset = SubCategory.objects.none()
        if 'category' in self.data:
            category_id = self.data['category']
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)

    class Meta:
        model = SupportTicket
        fields = (
            "category",
            "subcategory",
            "title",
            "description",
            "centre",
            "submitted_by",
        )


# Form for updating the description of a support ticket


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        # Fields to be updated
        fields = ("description",)
        # Field widget to display description with 5 rows
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}



class UserTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["title", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["readonly"] = True

    def clean_title(self):
        """
        Ensure that the title cannot be changed by the user.
        """
        return self.instance.title



class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'date_of_birth']
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'role', 'is_active', 'is_staff', 'centres']
