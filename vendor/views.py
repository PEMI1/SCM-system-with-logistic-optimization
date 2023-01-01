from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor



@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def vprofile(request):
    #these objects are passed to form inorder to render images into the image box 
    profile = get_object_or_404(UserProfile, user=request.user)  # request.user is the user which is logged in
    vendor = get_object_or_404(Vendor, user=request.user)


    #save the updates made in profile form
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings Updated ')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        #else pass the form fields from UserProfile and Vendor and show the current instance of vendor profile info in the form fields
        #if instance is not inside the else block, imageField validation error will not appear because after user tries to save file other than image files and click update then that error will be saved in current instance and will be shown when this instance gets loaded next time after the page reloads and the request is not POST
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form':profile_form,
        'vendor_form':vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    return render(request, 'vendor/vprofile.html', context)