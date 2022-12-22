from django.http import HttpResponse
from django.shortcuts import redirect, render

from vendor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile

#for showing messages popup
from django.contrib import messages

#login authentication
from django.contrib import auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role ==1:
        return True
    else:
        raise PermissionDenied  # from PermissionDenied - raises http 403 Forbidden error(user is unathorized to access the page)


#Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role ==2:
        return True
    else:
        raise PermissionDenied 



def registerUser(request):
    #restrict user from acessing registerUser page from url if he is already logged in
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in!')
        return redirect('myAccount')
    elif request.method == "POST":
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
    #restrict user from acessing registerVendor page from url if he is already logged in
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in!')
        return redirect('myAccount')

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


def login(request):
    #restrict user from acessing login page from url if he is already logged in
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in!')
        return redirect('myAccount')
    #if he is no logged in then proceed with login form validation
    elif request.method =='POST':
        email = request.POST['email']  # this 'email' is from the name of the input field in login.html
        password = request.POST['password']

        #use django authenticate function to check if email and password belongs to a user
        user = auth.authenticate(email=email, password= password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')

        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request,'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request,'You are logged out.')
    return redirect('login')

#custom function that direct logged in user to their respective dashboard
#After login is authenticated, user rediredcts to myAccount, then 'myAccount' function in views.py will pass this requesting user to 'detectUser' function in utils.py
# the 'detectUser' function will check user role and accordingly returns redirecturl 
# then user get redirected to the respective url:custDashboard or vendorDashboard
# Again custDashboard/vendorDashboard function in views will receive the request and then finally renders the dashboard.html
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirecturl = detectUser(user)
    return redirect(redirecturl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)  #this decorator ensures that 'check_role_customer' function is checked(returns true) before allowing the user to access the customer dashboard
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')