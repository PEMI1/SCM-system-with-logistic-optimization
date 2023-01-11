from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from .forms import ShipperForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Shipper
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_shipper



@login_required(login_url='login')
@user_passes_test(check_role_shipper) 
def sprofile(request):
    #these objects are passed to form inorder to render images into the image box 
    profile = get_object_or_404(UserProfile, user=request.user)  # request.user is the user which is logged in
    shipper = get_object_or_404(Shipper, user=request.user)


    #save the updates made in profile form
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        shipper_form = ShipperForm(request.POST, request.FILES, instance=shipper)
        if profile_form.is_valid() and shipper_form.is_valid():
            profile_form.save()
            shipper_form.save()
            messages.success(request, 'Settings Updated ')
            return redirect('sprofile')
        else:
            print(profile_form.errors)
            print(shipper_form.errors)
    else:
        #else pass the form fields from UserProfile and shipper and show the current instance of shipper profile info in the form fields
        #if instance is not inside the else block, imageField validation error will not appear because after user tries to save file other than image files and click update then that error will be saved in current instance and will be shown when this instance gets loaded next time after the page reloads and the request is not POST
        profile_form = UserProfileForm(instance=profile)
        shipper_form = ShipperForm(instance=shipper)

    context = {
        'profile_form':profile_form,
        'shipper_form':shipper_form,
        'profile':profile,
        'shipper':shipper,
    }
    return render(request, 'shipper/sprofile.html', context)