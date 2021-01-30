from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Review


class CityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        cities = kwargs.pop("City")
        super(CityForm, self).__init__(*args, **kwargs)
        self.fields["City"] = forms.ChoiceField(choices=cities, label='Click this to select a city',
                                                widget=forms.Select(attrs={'onchange': 'submit();'}))


class BusinessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        business = kwargs.pop("Business")
        super(BusinessForm, self).__init__(*args, **kwargs)
        self.fields["Business"] = forms.ChoiceField(choices=business, label='Click this to select a Business',
                                                    widget=forms.Select())


class CategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("Category")
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["Category"] = forms.MultipleChoiceField(choices=categories, label='Click this to select categories')
        # widget=forms.CheckboxSelectMultiple())


class VechileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(VechileForm, self).__init__(*args, **kwargs)
        choices = [(0, 'Car'), (1, 'Foot')]
        self.fields["Vechile"] = forms.CharField(label='Vechile type', widget=forms.RadioSelect(choices=choices),
                                                 initial=0)
        self.fields["Location"] = forms.CharField()


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'preference')


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True

    class Meta(forms.ModelForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'preference')


class SignInForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content', 'stars']
        widgets = {
            'stars': forms.NumberInput(attrs={'step': 1, 'min': 1, 'max': 5}),
        }
