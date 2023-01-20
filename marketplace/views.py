from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Cart
from menu.models import Category, Product

from django.db.models import Prefetch

from vendor.models import Vendor

from .context_processors import get_cart_counter, get_cart_amounts

from django.contrib.auth.decorators import login_required

from orders.forms import OrderForm
from accounts.models import UserProfile


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)  
    vendor_count = vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request, 'marketplace/listings.html',context)


def vendor_detail(request, vendor_slug):

    #get vendor by slug
    vendor = get_object_or_404(Vendor, vendor_slug = vendor_slug)

    #prefetch looks for product belonging to the category although Category has no foreign key linking to product
    #so categories has categories as well as products belonging to the categories
    #context sends 'categories' and 'category.products'
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'products',
             queryset= Product.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items =None

    context={
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
    }
    return render(request,'marketplace/vendor_detail.html', context)



#we are getting the request and product_id from vendor_detail.html when user clicks add_to_cart. This is controlled by custom.js
def add_to_cart(request, product_id):
    # user must login to access cart
    if request.user.is_authenticated:
        # request must be ajax
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            #check if product exists
            try:
                product = Product.objects.get(id=product_id)
                # check if the user has already added that product to cart. If it is then only increase qty else add the product to cart
                try:
                    chkCart = Cart.objects.get(user=request.user, product=product)  # get the product that is in the cart and its qty needs to increase
                    # if product object exists, increase qty of that product which is being added
                    chkCart.quantity +=1
                    chkCart.save()
                    return JsonResponse({'status':'Success', 'message':'Increased the cart quantity', 'cart_counter':get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount':get_cart_amounts(request)}) #also pass cart_counter/total cart quantity & product qty to Jsonresponse in custom.js
                except:
                    # else create the product to cart with quantity=1
                    chkCart = Cart.objects.create(user=request.user, product=product, quantity=1)
                    return JsonResponse({'status':'Success', 'message':'Added the product to cart', 'cart_counter':get_cart_counter(request), 'qty': chkCart.quantity,  'cart_amount':get_cart_amounts(request)})

            except:
                return JsonResponse({'status':'Failed', 'message':'This product does not exist'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request. Request is not ajax.'})
 
    else:
        return JsonResponse({'status':'login_required', 'message':'Please login to continue'})

   # return HttpResponse(product_id)



def decrease_cart(request, product_id):
    # user must login to access cart
    if request.user.is_authenticated:
        # request must be ajax
       # if request.is_ajax():
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            #check if product exists inorder to decrease
            try:
                product = Product.objects.get(id=product_id)
                # check if the user has already added that product to cart. If it is then  decrease qty else the product is not added in the cart/ qty label=0
                try:
                    chkCart = Cart.objects.get(user=request.user, product=product)# get the product that is in the cart and its qty needs to decrease
                    # if product object exists, decrease qty but check if total cart qty>1
                    if chkCart.quantity > 1:
                        chkCart.quantity -=1
                        chkCart.save()
                    else:
                        chkCart.delete() #delete the product from the cart if qty=1
                        chkCart.quantity = 0  #now that product qty has to be 0 
                    return JsonResponse({'status':'Success', 'cart_counter':get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount':get_cart_amounts(request)}) #pass the decreased cart_counter and  decreased/0 product qty
                except:
                   
                    return JsonResponse({'status':'Failed', 'message':'You do not have this item in your cart!'})

            except:
                return JsonResponse({'status':'Failed', 'message':'This product does not exist'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request. Request is not ajax.'})
 
    else:
        return JsonResponse({'status':'login_required', 'message':'Please login to continue'})


@login_required(login_url='login')
def cart(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items':cart_items,
    }
    return render(request,'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            try:
                #check if cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success', 'message':'Cart item has been deleted.','cart_counter':get_cart_counter(request), 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed', 'message':'Cart item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request. Request is not ajax.'})


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
         return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    # form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)
