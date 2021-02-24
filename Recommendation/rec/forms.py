from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Review


class CityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        cities = kwargs.pop("City")
        super(CityForm, self).__init__(*args, **kwargs)
        self.fields["City"] = forms.ChoiceField(choices=cities, label='Επιλέξτε περιοχή',
                                                widget=forms.Select(attrs={'onchange': 'submit();'}))


class BusinessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        business = kwargs.pop("Business")
        super(BusinessForm, self).__init__(*args, **kwargs)
        self.fields["Business"] = forms.ChoiceField(choices=business,
                                                    label='Επιλέξτε επιχείριση',
                                                    widget=forms.Select())


class CategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("Category")
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["Category"] = forms.MultipleChoiceField(choices=categories,
                                                            label='Επιλέξτε κατηγορία')
        # widget=forms.CheckboxSelectMultiple())


class VechileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(VechileForm, self).__init__(*args, **kwargs)
        choices = [(0, 'Αυτοκίνητο'), (1, 'Πόδια')]
        self.fields["Vechile"] = forms.CharField(label='Μέσο μεταφοράς', widget=forms.RadioSelect(choices=choices),
                                                 initial=0)
        self.fields["Location"] = forms.CharField(label='Τοποθεσία')
        # self.fields['Location'].widget.attrs['readonly'] = True
        self.fields["Location"].widget = forms.HiddenInput()


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'preference')
        labels = {
            "email": "Email",
            "first_name": "Όνομα",
            "last_name": "Επώνυμο",
            "preference": "Κατηγορίες"
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # self.fields['password1'].help_text = 'Something that doesnt look awful'
        self.fields['password2'].help_text = ''
        self.fields['password1'].label = 'Κωδικός'
        self.fields['password2'].label = 'Επιβεβαίωση κωδικού'


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True

    class Meta(forms.ModelForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'preference')
        labels = {
            "email": "Email",
            "first_name": "Όνομα",
            "last_name": "Επώνυμο",
            "preference": "Κατηγορίες"
        }


class SignInForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)
        labels = {
            "email": "Email",
            "password": "Κωδικός",
        }


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields["stars"].widget = forms.HiddenInput()

    class Meta:
        model = Review
        fields = ['title', 'content', 'stars']
        labels = {
            "title": "Τίτλος",
            "content": "Κριτική",
            "stars": "Βαθμολογία"
        }
        widgets = {
            'stars': forms.NumberInput(attrs={'step': 1, 'min': 1, 'max': 5}),
        }
