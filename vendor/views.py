from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from orders.models import Order, OrderedProduct, ShipOrder
from orders.utils import generate_shipping_number

from .forms import VendorForm, PackageVolumeForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor

from menu.models import Category, Product
from menu.forms import CategoryForm, ProductForm
from django.template.defaultfilters import slugify

from .utils import  get_vendor

from shipper.models import Shipper
from django.urls import reverse
from decimal import Decimal

from django.contrib.gis.geos import Point

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
            # address = profile_form.cleaned_data['address']
            # print(address)
            # # Use geos to query the OSM data and get the location
            # point = Point(x, y)
            # profile_form.location = point

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


@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
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


@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
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


@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def delete_category(request,pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfully!")
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_title = form.cleaned_data['product_title']
            product = form.save(commit = False)  #form is ready to be saved but not yet saved
            product.vendor = get_vendor(request)
            product.slug = slugify(product_title)  #slugify generates the slug of category
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('products_by_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = ProductForm()
        # modify this form to show only associated categories to the vendor
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form':form
    }

    return render(request, 'vendor/add_product.html',context)




@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def edit_product(request, pk=None):
    product = get_object_or_404(Product, pk = pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product_title = form.cleaned_data['product_title']
            product = form.save(commit = False)  #form is ready to be saved but not yet saved
            product.vendor = get_vendor(request)
            product.slug = slugify(product_title)  #slugify generates the slug of category
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('products_by_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = ProductForm(instance=product)
        # modify this form to show only associated categories to the vendor
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context= {
        'form': form,
        'product':product,
    }
    return render(request, 'vendor/edit_product.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor) 
def delete_product(request,pk=None):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product has been deleted successfully!")
    return redirect('products_by_category', product.category.id)


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_product = OrderedProduct.objects.filter(order=order, product__vendor=get_vendor(request)) #get the ordered product whose order number is the order no. passed via url from vendorDashboard.html and also the vendor of the ordered product is current logged in vendor
        context={
            'order':order,
            'ordered_product':ordered_product,
            'subtotal':order.get_total_by_vendor()['subtotal'],
            'grand_total':order.get_total_by_vendor()['grand_total'],

        }
    except:
        return redirect('vendor')
    return render(request, 'vendor/order_detail.html',context)


def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)  #get current vendor 
    #Since vendors field in Order model is manytomany type, get only get those orders where order.vendors.id = current vendor id.   
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')  
    context={
        'orders':orders,
    }
    return render(request, 'vendor/my_orders.html',context)

def assign_shipper(request, order_number):
    shippers = Shipper.objects.filter(is_approved=True, user__is_active=True)  
    shipper_count = shippers.count()
   
    context={
        'shippers':shippers,
        'shipper_count':shipper_count,
        'order_number':order_number,
       
    }
    return render(request, 'vendor/assign_shipper.html', context)


@login_required(login_url='login')
def load_package_volume(request, shipper_id, order_number):
    shipper=Shipper.objects.get(id=shipper_id)
    if request.method =='POST':
        form = PackageVolumeForm(request.POST)
        if form.is_valid():
            # Store the volume in a temporary variable
            volume = form.cleaned_data['volume']
            request.session['volume'] = volume
            url = reverse('confirm_shipper', kwargs={'shipper_id': shipper_id, 'order_number': order_number, 'volume':volume})
            return redirect(url)

        else:
            print(form.errors)
    else:
        form = PackageVolumeForm()
    context= {
        'form': form,
        'shipper':shipper,
        'order_number':order_number,

    }

    return render(request, 'vendor/load_package_volume.html', context)


#we are getting the request and shipper_id from assign_shipper.html when user clicks select. This is controlled by custom.js
def confirm_shipper(request,  shipper_id, order_number, volume):
    vendor = Vendor.objects.get(user=request.user)  #get current vendor 
    order =Order.objects.get(order_number=order_number, vendors= vendor)
    shipper=Shipper.objects.get(id=shipper_id)
    # volume = request.session.pop('volume', None)
    volume = float(volume)
    print(volume)
   
    if  request.headers.get('x-requested-with')=='XMLHttpRequest' and request.method == 'POST': 
        # Retrieve the volume from the temporary variable
        
        # return HttpResponse(volume)  
        if volume:
            # Create the ShipOrder model and assign the volume          
            #update order model         
            order.shippers.add(shipper)          
            order.save()      
            

            #create ShipOrder
            ship_order = ShipOrder(
                order = order,
                vendor = vendor,
                shipper = shipper,
                package_volume = volume,
                            
            )
            ship_order.save()
            ship_order.shipping_number = generate_shipping_number(ship_order.id)
            ship_order.save()

            # return HttpResponse('Shipper added') 
            print('shipper added')
            return JsonResponse({'status':'Success', 'message':'Shipper Assigned Successfully!'}) 
           
           
        else:
            return redirect('load_package_volume')   

    else:
        context={
            'order': order,
            'order_number':order_number,
            'vendor': vendor,
            'shipper_id':shipper_id,
            'volume':volume,
            
        }
        
        return render(request, 'vendor/confirm_shipper.html', context)


   


    
