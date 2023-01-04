from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor

from menu.models import Category, Product
from menu.forms import CategoryForm
from django.template.defaultfilters import slugify

from .utils import  get_vendor

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


@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories' : categories,
    }
    return render(request, 'vendor/menu_buider.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def products_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    products =Product.objects.filter(vendor=vendor, category= category)
    print(products)
    context = {
        'products' :products,
        'category' :category,
    }
    return render(request, 'vendor/products_by_category.html',context)



def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit = False)  #form is ready to be saved but not yet saved
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)  #slugify generates the slug of category
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context= {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk = pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit = False)  #form is ready to be saved but not yet saved
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)  #slugify generates the slug of category
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context= {
        'form': form,
        'category':category,
    }
    return render(request, 'vendor/edit_category.html',context)


def delete_category(request,pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfully!")
    return redirect('menu_builder')
