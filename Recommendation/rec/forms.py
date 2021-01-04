from django import forms


class CityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        cities = kwargs.pop("City")
        super(CityForm, self).__init__(*args, **kwargs)
        self.fields["City"] = forms.ChoiceField(choices=cities, label='City name        ',
                                                widget=forms.Select(attrs={'onchange': 'submit();'}))


class CategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("Category")
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["Category"] = forms.MultipleChoiceField(choices=categories, label='Categories')
        # widget=forms.CheckboxSelectMultiple())
