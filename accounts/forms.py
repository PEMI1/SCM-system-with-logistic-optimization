from django import forms
from .models import User, UserProfile

from .validators import allow_only_images_validator

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



class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing.....', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])

    #make latitude and longitude read only method 1
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))

    class Meta:
        model = UserProfile
        #fields = ['profile_picture','cover_photo','address_line_1','address_line_2','country','state','city','pin_code','latitude','longitude']
        fields = ['profile_picture','cover_photo','address','country','state','city','pin_code','latitude','longitude']


    #method 2
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'




class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']