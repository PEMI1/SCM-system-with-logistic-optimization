from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from orders.models import Order, ShipOrder, OrderedProduct

from .forms import ShipperForm, ContainerOptimizationForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Shipper
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_shipper

import math



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


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        shipper = Shipper.objects.get(user=request.user)
        ship_order = ShipOrder.objects.get(order=order, shipper=shipper)
        ordered_product = OrderedProduct.objects.filter(order=order, product__vendor=ship_order.vendor) #get the ordered product whose order number is the order no. passed via url from vendorDashboard.html and also the vendor of the ordered product is current logged in vendor
        
        subtotal = 0
        for item in ordered_product:
            subtotal += (item.price * item.quantity)
            
        context={
            'order':order,
            'ordered_product':ordered_product,
            'ship_order':ship_order,
            'subtotal':subtotal,
            'grand_total':subtotal,

        }
        
        return render(request, 'shipper/order_detail.html',context)
    except:
        return redirect('shipper')


def my_orders(request):
    shipper = Shipper.objects.get(user=request.user)  #get current shipper 
    #Since shippers field in Order model is manytomany type, get only  those orders where order.shippers.id = current shipper id.   
    orders = Order.objects.filter(shippers__in=[shipper.id], is_ordered=True).order_by('-created_at')  
    print(orders)

    shiporders = ShipOrder.objects.filter(shipper=shipper).order_by('-created_at')
    print(shiporders)

    context={
        'orders':orders,
        'shiporders':shiporders,
    }
    
    return render(request, 'shipper/my_orders.html',context)


def optimize_container(request):
    shipper = Shipper.objects.get(user=request.user)
    ship_orders = ShipOrder.objects.filter(shipper=shipper).order_by('-created_at') 

    packages=[]
    priority = 0
    for ship_order in ship_orders:
        shipping_number = ship_order.shipping_number
        package_volume = ship_order.package_volume
        priority += 1  #optimization on basis of profit/pricing gives blunders. 
        
        packages.append({'volume': math.floor(package_volume), 'priority': priority, 'shipping_number':shipping_number})

    sorted_packages = sorted(packages, key=lambda x: x['volume'])
    print(sorted_packages)

    if request.method == 'POST':
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            form = ContainerOptimizationForm(request.POST)
            if form.is_valid():
                container_volume = form.cleaned_data['container_volume']
                # request.session['container_volume'] = container_volume

                result=()
                selected_items = []
                result= knapsack(sorted_packages, container_volume)
                print(result)
                selected_items = result[1]
                print(selected_items)

                selected_shippingNumbers = [t['shipping_number'] for t in selected_items]
                print(selected_shippingNumbers)

                # selected_shipOrders =[]
                # for selected_shippingNumber in selected_shippingNumbers:
                #     shiporder = ShipOrder.objects.get(shipping_number =selected_shippingNumber)
                #     selected_shipOrders.append(shiporder)
                # print(selected_shipOrders)
                
    
                return JsonResponse({ 'container_volume': container_volume})
        
        else:
            form = ContainerOptimizationForm(request.POST)
            if form.is_valid():
                container_volume = form.cleaned_data['container_volume']
                # request.session['container_volume'] = container_volume

                result=()
                selected_items = []
                result= knapsack(sorted_packages, container_volume)
                print(result)
                selected_items = result[1]
                print(selected_items)

                selected_shippingNumbers = [t['shipping_number'] for t in selected_items]
                print(selected_shippingNumbers)

                selected_shipOrders =[]
                for selected_shippingNumber in selected_shippingNumbers:
                    print(selected_shippingNumber)
                    shiporder = ShipOrder.objects.get(shipper=shipper ,shipping_number =selected_shippingNumber)
                    selected_shipOrders.append(shiporder)
                print(selected_shipOrders)
                
                context={
                    'form':form,
                    'selected_shipOrders':selected_shipOrders,
                    'container_volume':container_volume,
                }
                return render(request, 'shipper/optimize_container.html', context)
    else:
        form = ContainerOptimizationForm()
    context= {
        'form': form,
    }

    return render(request, 'shipper/optimize_container.html', context)

def knapsack(packages, max_volume_float):
    max_volume = math.floor(max_volume_float) #type cast to int
    # Initialize a 2D array to store the results
    dp = [[0 for _ in range(max_volume + 1)] for _ in range(len(packages) + 1)]
    # Initialize a 2D array to store the solution 
    keep = [[False for _ in range(max_volume + 1)] for _ in range(len(packages) + 1)]
    
    # Iterate through the packages
    for i in range(1, len(packages) + 1):
        for j in range(1, max_volume + 1):
            if packages[i-1]['volume'] > j:
                dp[i][j] = dp[i-1][j]
            else:
                if dp[i-1][j]> dp[i-1][j-packages[i-1]['volume']] + packages[i-1]['priority']:
                    dp[i][j] = dp[i-1][j]
                else:
                    dp[i][j] = dp[i-1][j-packages[i-1]['volume']] + packages[i-1]['priority']
                    keep[i][j] = True
    selected_items = []
    j = max_volume
    for i in range(len(packages), 0, -1):
        if keep[i][j]:
            selected_items.append(packages[i-1])
            j -= packages[i-1]['volume']
    return dp[len(packages)][max_volume], selected_items
