from django import forms

from pricing.models import Positions

class PositionForm(forms.Form):
    positions = forms.ModelChoiceField(queryset=Positions.objects.all())