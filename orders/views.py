import simplejson as json
from django.shortcuts import redirect, render
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from menu.models import Product
from .forms import OrderForm
from .models import Order, OrderedProduct, Payment

from django.http import HttpResponse, JsonResponse

from .utils import generate_order_number

from accounts.utils import send_notification

from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def place_order(request):
     cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
     cart_count = cart_items.count()
     if cart_count <= 0:
          return redirect('marketplace')

     #render vendor recent orders at vendordashboard using vendor's id. This ids are passed to order model to get the vendors associated with an order
     vendors_ids = []
     for i in cart_items:
          if i.product.vendor.id not in vendors_ids: #get id once for each vendor 
               vendors_ids.append(i.product.vendor.id)    
     print(vendors_ids)

     #orders.views.place_order(order.total_data)->vendorDashboard.html(order.get_total_by_vendor)->orders.models.get_total_by_vendor
     #get subtotal of each vendor for each order. Make json format that stores :
     #{'vendor_id':'subtotal'}
     #loop through cart items and calculate subtotal for unique vendor id in vendors_ids
     subtotal=0
     k={} #dictionary that stores key(v_id):value(subtotal) pair
     total_data ={}
     for i in cart_items:
          product= Product.objects.get(pk=i.product.id, vendor_id__in=vendors_ids)  #bring product whose pk=current item's id and vendor is in vendors_ids list
          print(product, product.vendor.id)
          v_id = product.vendor.id
          if v_id in k:
               subtotal = k[v_id]  #old subtotal
               subtotal += (product.price * i.quantity)
               k[v_id] = subtotal #new subtotal
          else:
               subtotal = (product.price * i.quantity)  #first loop when v_id is not in the k list
               k[v_id] = subtotal  #we cannot append dictionary. Value of key[v_id] is subtotal
          #constract total_data which is passed to total_data field in order model
          total_data.update({product.vendor.id:subtotal})  #json format

     print(k)
     print(total_data)


     subtotal = get_cart_amounts(request)['subtotal']
     grand_total = get_cart_amounts(request)['grand_total']

     if request.method =='POST':
          form = OrderForm(request.POST)
          if form.is_valid():
               order = Order()
               order.first_name = form.cleaned_data['first_name']
               order.last_name = form.cleaned_data['last_name']
               order.phone = form.cleaned_data['phone']
               order.email = form.cleaned_data['email']
               order.address = form.cleaned_data['address']
               order.country = form.cleaned_data['country']
               order.state = form.cleaned_data['state']
               order.city = form.cleaned_data['city']
               order.pin_code = form.cleaned_data['pin_code']

               order.user = request.user
               order.total = grand_total
               order.total_data = json.dumps(total_data)
               order.payment_method = request.POST['payment_method']

               order.save()  #pk/order.id is only created after saving the order
               order.order_number = generate_order_number(order.id)
               order.vendors.add(*vendors_ids)  # '*' adds vendor ids recurcively in order_vendor table to hold manyTomany relation
               order.save() 

               context={
                    'order': order,
                    'cart_items': cart_items,
               }
               
               return render(request, 'orders/place_order.html', context)

          else:
               print(form.errors)

     return render(request, 'orders/place_order.html')



#This payments view will store the TX data into payment model
@login_required(login_url='login')
def payments(request):
     #check if request is ajax
     if request.headers.get('x-requested-with')=='XMLHttpRequest' and request.method == 'POST': #ajax request type is POST

          #store payments data to payments model
          order_number = request.POST.get('order_number')
          transaction_id = request.POST.get( 'transaction_id')
          payment_method = request.POST.get('payment_method')
          status = request.POST.get('status')


          order =Order.objects.get(user=request.user, order_number=order_number)
          payment = Payment(
               user = request.user,
               transaction_id = transaction_id,
               payment_method = payment_method,
               amount = order.total,
               status = status
          )
          payment.save()


          #update order model
          order.payment = payment  #payment field for order model will be transaction_id of payment model becoz str representation of payment model is transaction_id
          order.is_ordered = True
          order.save()         

          #move cart item to orderedProducts model
          cart_items = Cart.objects.filter(user=request.user)
          for item in cart_items:
               ordered_product = OrderedProduct()
               ordered_product.order = order
               ordered_product.payment = payment
               ordered_product.user = request.user
               ordered_product.product = item.product
               ordered_product.quantity = item.quantity
               ordered_product.price = item.product.price
               ordered_product.amount = item.product.price * item.quantity
               ordered_product.save()


          #send order confirmation email to customer
          mail_subject = 'Thankyou for ordering with us.'
          mail_template = 'orders/order_confirmation_email.html'
          context= {
               'user': request.user,
               'order': order,
               'to_email': order.email,
          }
          send_notification(mail_subject, mail_template, context)

          #send order received email to vendor
          mail_subject = 'You have received a new order.'
          mail_template = 'orders/new_order_received.html'
          to_emails = []  #empty list because email can be sent to multiple vendors
          for i in cart_items:
               #loop through each item in cart but also check if the vendor email is already appended to the to_emails list to avoid sending multiple emails for different products sold by same vendor
               if i.product.vendor.user.email not in to_emails:
                    to_emails.append(i.product.vendor.user.email)
          print(to_emails)        
          context= {
               'order': order,
               'to_email': to_emails,
          }
          send_notification(mail_subject, mail_template, context)

          #clear cart if payment is success
          cart_items.delete()

          #return back to ajax with status SUCCESS or FAILURE/ Show order confirmation page after order success
          response = {
               'order_number': order_number,
               'transaction_id':transaction_id,
          }
          return JsonResponse(response)

     return HttpResponse('Payments view')


def order_complete(request):
     #take order_no and transaction_id from url parameter
     order_number = request.GET.get('order_no')
     transaction_id = request.GET.get('trans_id')

     order = Order.objects.get(order_number =order_number, payment__transaction_id=transaction_id, is_ordered =True)
     ordered_product =OrderedProduct.objects.filter(order=order)
         
     try:
          order = Order.objects.get(order_number =order_number, payment__transaction_id=transaction_id, is_ordered =True)
          ordered_product =OrderedProduct.objects.filter(order=order)
         
         
          subtotal = 0
          for item in ordered_product:
               subtotal += (item.price * item.quantity)

          

          context ={
               'order':order,
               'ordered_product':ordered_product,
               'subtotal':subtotal,
          }
          return render(request, 'orders/order_complete.html',context)

     except:
          return redirect('home')

     