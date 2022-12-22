from django import forms
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ["first_name",'last_name','email','username','password']

    #to handle the mismatched pw error(non feild error which was raised from above custom password fields
    def clean(self):  # django calls clean function whenever a form is triggered , it takes form input & returns cleaned data
        #we will override this clean function 
        cleaned_data = super(UserForm, self).clean()  # super gives ability to override 
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Password does not match'
            )

