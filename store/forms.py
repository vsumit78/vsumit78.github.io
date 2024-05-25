from django import forms
from .models.house import HouseRequirements

class HouseRequirementsForm(forms.ModelForm):
    class Meta:
        model = HouseRequirements
        fields = '__all__'
