from django.http import HttpResponse
from django.shortcuts import redirect, render

from shipper.forms import ShipperForm
from shipper.models import Shipper
from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import LocalAddress, User, UserProfile, Counties

from django.template.defaultfilters import slugify

#for showing messages popup
from django.contrib import messages

#login authentication
from django.contrib import auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from django.core.exceptions import PermissionDenied

from .utils import send_verification_email 
#from .utils import send_password_reset_email

from orders.models import Order, ShipOrder

from django.core.serializers import serialize

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


def check_role_shipper(user):
    if user.role ==3:
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


            #send verification email
            #send_verification_email(request,user )
            mail_subject = 'Please activate your account'
            email_template ='accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)


            messages.success(request, 'Your account has been registered successfully')
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


def registerMerchant(request):
    return render(request, 'accounts/registerMerchant.html')


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
            
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            
            user_profile = UserProfile.objects.get(user=user)  
            vendor.user_profile = user_profile
            vendor.save()

            #send verification email
            #send_verification_email(request,user )
            mail_subject = 'Please activate your account'
            email_template ='accounts/emails/account_verification_email.html'
            send_verification_email(request,user,mail_subject,email_template )


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

def registerShipper(request):
    #restrict user from acessing registerShipper page from url if he is already logged in
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in!')
        return redirect('myAccount')

    if request.method=='POST':
        #store the data and create the user
        form = UserForm(request.POST)  # pass data we are getting from the post into UserForm and store the instance as form
        s_form = ShipperForm(request.POST, request.FILES)  # we must also receive the license image so also pass request.files

        if form.is_valid() and s_form.is_valid():
            first_name= form.cleaned_data['first_name']
            last_name= form.cleaned_data['last_name']
            username= form.cleaned_data['username']
            email= form.cleaned_data['email']
            password= form.cleaned_data['password']

            user= User.objects.create_user(first_name=first_name, last_name=last_name,username=username,email=email, password=password, )
            user.role=User.SHIPPER
            user.save()

            #save the data(contains name,email...of user also the restaurant name and license of shipper) from the shipper form into shipper object
            shipper = s_form.save(commit=False)  # we need to provide user and userprofile before saving the shipper
            shipper.user = user  # when user.save() is triggered signal post_save() will create the user..this user is what we are getting here
            
            shipper_name = s_form.cleaned_data['shipper_name']
            shipper.shipper_slug = slugify(shipper_name)+'-'+str(user.id)
            
            user_profile = UserProfile.objects.get(user=user)  
            shipper.user_profile = user_profile
            shipper.save()

            #send verification email
            #send_verification_email(request,user )
            mail_subject = 'Please activate your account'
            email_template ='accounts/emails/account_verification_email.html'
            send_verification_email(request,user,mail_subject,email_template )


            messages.success(request,'Your account has been registered successfully! Please wait for the approval.')
            return redirect('registerShipper')
        else:
            print('invalid form')
            print(form.errors)
   
    else:
        form = UserForm()
        s_form = ShipperForm()

    context={
        'form':form,
        's_form':s_form,
    }
    return render(request, 'accounts/registerShipper.html',context)


def activate(request, uidb64, token):
    #Activate the user by setting the is_active status to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError, User.DoesNotExist):
        user = None  #if we get error than this means user=none

    if user is not None and default_token_generator.check_token(user,token): #now check the created token
        user.is_active =True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('myAccount')

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
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    context= {
        'orders' : orders,
        'orders_count' : orders.count(),
        'recent_orders':recent_orders,
    }
    return render(request, 'accounts/custDashboard.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)  #get current vendor 
    #Since vendors field in Order model is manytomany type, get only  those orders where order.vendors.id = current vendor id.   
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')  
    print(orders)
    recent_orders = orders[:5]

    shiporders = ShipOrder.objects.filter(vendor=vendor)
    print(shiporders)

    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'shiporders':shiporders,
    }
    return render(request, 'accounts/vendorDashboard.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_shipper) 
def shipperDashboard(request):
    shipper = Shipper.objects.get(user=request.user)  #get current shipper 
    #Since shippers field in Order model is manytomany type, get only  those orders where order.shippers.id = current shipper id.   
    orders = Order.objects.filter(shippers__in=[shipper.id], is_ordered=True).order_by('-created_at')  
    print(orders)
    recent_orders = orders[:5]

    shiporders = ShipOrder.objects.filter(shipper=shipper).order_by('-created_at')
    print(shiporders)

    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'shiporders':shiporders,
    }
    
    return render(request, 'accounts/shipperDashboard.html',context)



#first send email to reset pw then validate the uid and token when user clicks the link in email, then show him reset pw form and reset the pw
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists(): #first check if user exists
            user = User.objects.get(email__exact=email)

            #send reset password email
            #send_password_reset_email(request, user)
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request,user ,mail_subject,email_template)

            messages.success(request, 'Password reset link has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')



def reset_password_validate(request,uidb64,token):
    #validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError, User.DoesNotExist):
        user = None  #if we get error than this means user=none

    if user is not None and default_token_generator.check_token(user,token): 
        request.session['uid'] = uid  #store the uid from url to session. Now request has session variable with user's id
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired.')
        return redirect('myAccount')
    

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')  #get the pk of the user from session
            user = User.objects.get(pk = pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successfull')
            return redirect('login')
        else:
            messages.error(request,'Password do not match.')

    return render(request, 'accounts/reset_password.html')



def localAddress_data(request):
    localAddresses = serialize('geojson', LocalAddress.objects.all())
    return HttpResponse(localAddresses, content_type='json')#just return httpresponse containing serialized objects of LocalAddress in json format

def counties_data(request):
    counties = serialize('geojson', Counties.objects.all())
    return HttpResponse(counties, content_type='json')#just return httpresponse containing serialized objects of LocalAddress in json format

