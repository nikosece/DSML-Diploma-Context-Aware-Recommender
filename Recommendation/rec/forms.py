from django import forms


class CityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        cities = kwargs.pop("City")
        super(CityForm, self).__init__(*args, **kwargs)
        self.fields["City"] = forms.ChoiceField(choices=cities, label='Click this to select a city',
                                                widget=forms.Select(attrs={'onchange': 'submit();'}))


class CategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("Category")
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["Category"] = forms.MultipleChoiceField(choices=categories, label='Click this to select categories')
        # widget=forms.CheckboxSelectMultiple())


class ChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChoiceForm, self).__init__(*args, **kwargs)
        choices = [(0, 'Pure'), (1, 'LightFm'), (2, 'Both')]
        self.fields["Filter"] = forms.CharField(label='Filter type', widget=forms.RadioSelect(choices=choices))
