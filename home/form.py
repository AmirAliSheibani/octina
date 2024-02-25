from django import forms
from .models import EmailSend

class EmailSendingForm(forms.ModelForm):
    class Meta:
        model = EmailSend
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'placeholder': 'ایمیل را وارد کنید',
            'class': 'form-control'
        })