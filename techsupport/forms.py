from django import forms
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket, UserProfile, User
from django.core.validators import MaxLengthValidator
from django.shortcuts import get_object_or_404

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


class SupportTicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user.centres.count() == 1:
            self.fields['centre'].initial = user.centres.first()

        if 'category' in self.data:
            category = get_object_or_404(Category, id=self.data['category'])
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category=category)
        else:
            self.fields['subcategory'].queryset = SubCategory.objects.none()

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



class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'date_of_birth']
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'role', 'is_active', 'is_staff', 'centres']
