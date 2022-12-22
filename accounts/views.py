from django.http import HttpResponse
from django.shortcuts import redirect, render

from vendor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile

#for showing messages popup
from django.contrib import messages

# Create your views here.

def registerUser(request):
    if request.method == "POST":
        #print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            #Create user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)  #false means this form is ready to be saved and what ever data is in the form, it is assigned to 'user'
            # user.set_password(password)
            # user.role=User.CUSTOMER  # we assign role before saving the data
            # user.save()  

            #Create user using create_user method in UserManager class in model
            first_name= form.cleaned_data['first_name']
            last_name= form.cleaned_data['last_name']
            username= form.cleaned_data['username']
            email= form.cleaned_data['email']
            password= form.cleaned_data['password']

            user= User.objects.create_user(first_name=first_name, last_name=last_name,username=username,email=email, password=password, )
            user.role=User.CUSTOMER
            user.save()

            messages.success(request,'Your account has been registered successfully')
            return redirect('registerUser')
        else:
            #field errors will raise if the user tries to enter invalid inputs to the model from the form(eg, user/email already exist errors)
            print('invalid form')
            print(form.errors)
    else:
        form=UserForm()
    context={
        'form':form,
    }
    return render(request,'accounts/registerUser.html',context)


def registerVendor(request):

    if request.method=='POST':
        #store the data and create the user
        form = UserForm(request.POST)  # pass data we are getting from the post into UserForm and store the instance as form
        v_form = VendorForm(request.POST, request.FILES)  # we must also receive the license image so also pass request.files

        if form.is_valid() and v_form.is_valid():
            first_name= form.cleaned_data['first_name']
            last_name= form.cleaned_data['last_name']
            username= form.cleaned_data['username']
            email= form.cleaned_data['email']
            password= form.cleaned_data['password']

            user= User.objects.create_user(first_name=first_name, last_name=last_name,username=username,email=email, password=password, )
            user.role=User.VENDOR
            user.save()

            #save the data(contains name,email...of user also the restaurant name and license of vendor) from the vendor form into vendor object
            vendor = v_form.save(commit=False)  # we need to provide user and userprofile before saving the vendor
            vendor.user = user  # when user.save() is triggered signal post_save() will create the user..this user is what we are getting here
            user_profile = UserProfile.objects.get(user=user)  
            vendor.user_profile = user_profile
            vendor.save()

            messages.success(request,'Your account has been registered successfully! Please wait for the approval.')
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)
   
   
    else:
        form = UserForm()
        v_form = VendorForm()

    context={
        'form':form,
        'v_form':v_form,
    }
    return render(request, 'accounts/registerVendor.html',context)
