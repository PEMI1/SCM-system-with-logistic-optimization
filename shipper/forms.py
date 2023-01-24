from django import forms

from .models import Shipper 
from accounts.validators import allow_only_images_validator



class ShipperForm(forms.ModelForm):
    shipper_license = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])

    class Meta:
        model= Shipper
        fields = ['shipper_name', 'shipper_license']

class ContainerOptimizationForm(forms.Form):
    container_volume = forms.FloatField()


        