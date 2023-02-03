from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from shipper.forms import ShipperForm
from shipper.models import Shipper
from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import  Edge, Node, User, UserProfile, RoadsData, DataStatus

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

#routing
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
import numpy as np
import json
from django.contrib.gis.geos import MultiLineString
from shapely.geometry import LineString
from sklearn.neighbors import KDTree
import math
import networkx as nx


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

def roads_data(request):
    roads = serialize('geojson', RoadsData.objects.all())
    return HttpResponse(roads, content_type='json')#just return httpresponse containing serialized objects of LocalAddress in json format

# Create a nearest neighbor finding function using the KDTree
def nearest_neighbor(source, destination, kdtree):
    source = np.array([[source.x, source.y]])
    destination = np.array([[destination.x, destination.y]])
    distances, indices = kdtree.query(np.concatenate([source, destination]), return_distance=True, k=1)
    return indices[0][0], indices[1][0]

def nearest_neighbor_endpoint(request):
    # Retrieve the source and destination marker coordinates from the request data
    payload = json.loads(request.body)
    source_coords = payload.get('source')
    destination_coords = payload.get('destination')
    print(type(source_coords))
    print(source_coords)
    print(destination_coords)

    #switch lat and long
    source = Point(source_coords[1], source_coords[0])
    destination = Point(destination_coords[1], destination_coords[0])
    kdtree = extractNodes_from_roadsData_and_fitKDTree_toThe_nodes(request)

    # Call the nearest neighbor finding function to get the nearest neighbors in numpy.int64 type
    nearest_source, nearest_destination = nearest_neighbor(source, destination, kdtree)
    print(type(nearest_source))

    # Get the coordinates of the nearest points and convert it to list type
    #the nearest_source and nearest_destination are of type numpy.int64 and JSON responses can only contain serializable data types. 
    #To resolve the issue,convert the nearest_source and nearest_destination to a serializable data type, such as a list or a tuple, before returning it as a JSON response
    nearest_source_coords = list(kdtree.data[nearest_source])
    nearest_destination_coords = list(kdtree.data[nearest_destination])

    #switch lat and long
    nearest_source_coords[0], nearest_source_coords[1] = nearest_source_coords[1], nearest_source_coords[0]
    nearest_destination_coords[0], nearest_destination_coords[1] = nearest_destination_coords[1], nearest_destination_coords[0]
    print(nearest_source_coords)
    print(nearest_destination_coords)

    # Return the nearest neighbors as a JSON response
    return JsonResponse({
        'nearest_source': nearest_source_coords,
        'nearest_destination': nearest_destination_coords
    })

#retrieve the road network graph data from the database and convert it into a suitable data structure(KDTree) that can be used with the routing algorithm
def extractNodes_from_roadsData_and_fitKDTree_toThe_nodes(request):
    # Retrieve road objects from the database
    roads = RoadsData.objects.all()

    # Initialize a list to store the road network nodes
    nodes = []

    print_count=0
    # Loop through each road object in the database
    for road in roads:
        # Extract the MultiLineString geometry from the road object
        road_geom = road.geom
        
        # Check if the geometry is a MultiLineString
        if isinstance(road_geom, MultiLineString):
            # Loop through each line string in the MultiLineString           
            for line_string in road_geom:
                if (print_count<1):                   
                    print('*****************LINE STRING*********************\n')
                    print(line_string)
     
                # Convert the line string into a shapely LineString object
                line = LineString(line_string)
                if (print_count<1):
                    print('****************LINE*********************\n')  #output: LINESTRING (85.3228018 27.638524, 85.3232236 27.6390716, 85.3232812 27.6391001, 85.3233261 27.6391028, 85.323576 27.6389745)NEW
                    print(line.wkt+'NEW\n')          

                # Extract the coordinates of the line string
                coords = np.array(line.coords)
                if (print_count<1):
                    print('****************LINE COORDS*********************\n')
                    print(coords)
                
                # Add the extracted coordinates to the list of nodes
                nodes.append(coords)
            print_count = 2               

    print('****************NODES*********************\n')
    print(nodes[0])

    # Concatenate all the nodes into a single 2D NumPy array
    nodes = np.concatenate(nodes, axis=0)
    print('****************CONCATENATED NODES*********************\n')
    print(nodes[0])  #nodes is the list of nodes extracted from the RoadsData model

    # Create the KDTree and fit it to the data
    kdtree = KDTree(nodes)
    print('****************KDTREE*********************\n')
    print(kdtree)

    #also create nodes and edges from the road data then save them to Node & Edge models inorder to use them to create the road network graph
    nodes, edges = create_nodes_and_edges(roads)

    return kdtree

def create_nodes_and_edges(roads):
    #Check if nodes and edges are already created and saved to avoid saving them again in the database
    data_status = DataStatus.objects.first()
    if not data_status or not data_status.nodes_and_edges_created:  #If no dataStatus model's record exist or if it exist but the record's nodes_and_edges_created field is False
        nodes = []
        edges = []
        node_index = 0

        for road in roads:
            road_geom = road.geom
            if isinstance(road_geom, MultiLineString):
                for line_string in road_geom:
                    line = LineString(line_string)
                    coords = np.array(line.coords)
                    start_index = node_index
                    for coord in coords:
                        node = Node(latitude=coord[0], longitude=coord[1])
                        node.save()
                        nodes.append(node)
                        end_index = node_index
                        if start_index != end_index:
                            cost = calculate_cost(nodes[start_index], nodes[end_index])
                            edge = Edge(start_node=nodes[start_index], end_node=nodes[end_index], cost=cost)
                            edge.save()
                            edges.append(edge)
                            start_index = end_index
                        node_index += 1

        if not data_status:
            data_status = DataStatus.objects.create(nodes_and_edges_created=True) #If no dataStatus model's record exist, created one with nodes_and_edges_created=True
        else:
            data_status.nodes_and_edges_created = True  #if it exist but the record's nodes_and_edges_created field is False then set it to True now
            data_status.save()
    else:
        nodes = Node.objects.all()
        edges = Edge.objects.all()

    #Create graph from nodes and edges
    graph = create_graph(nodes, edges)

    #Create adjacent list from nodes and edges
    adjacency_list = create_adjacency_list(nodes, edges)

    return nodes, edges

def calculate_cost(start, end):
    # Extract the latitude and longitude of the start node
    start_lat = start.latitude
    start_lon = start.longitude 
    # Extract the latitude and longitude of the end node
    end_lat = end.latitude
    end_lon = end.longitude

    # Convert the latitudes and longitudes to radians
    start_lat, start_lon = math.radians(start_lat), math.radians(start_lon)
    end_lat, end_lon = math.radians(end_lat), math.radians(end_lon)

    # Calculate the difference in latitudes and longitudes
    lat_diff = end_lat - start_lat
    lon_diff = end_lon - start_lon

    # Apply the spherical law of cosines formula
    a = math.sin(lat_diff / 2)**2 + math.cos(start_lat) * math.cos(end_lat) * math.sin(lon_diff / 2)**2 #square of the sine of half the latitude difference and the product of the cosines of the two latitudes and the square of the sine of half the longitude difference
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) #inverse tangent of the square root of 'a' and the square root of one minus 'a' is calculated and multiplied by two to get the central angle between the two points
    earth_radius = 6371  # Approximate radius of the earth in kilometers
    distance = earth_radius * c

    # Return the calculated distance as the cost
    return distance

def create_graph(nodes, edges):
    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node)
    for edge in edges:
        start_node = edge.start_node
        end_node = edge.end_node
        graph.add_edge(start_node, end_node, weight=edge.cost)
    return graph

def create_adjacency_list(nodes, edges):
    adjacency_list = {}
    for node in nodes:
        adjacency_list[node] = [] # create an empty list for each node in the adjacency_list dictionary
    for edge in edges:
        start = edge.start_node
        end = edge.end_node
        cost = edge.cost
        adjacency_list[start].append((end, cost)) #append a tuple (end, cost) to represent the connected end node (conencted with the start node) and the cost of the edge between the start node and the end node.
        #ie. each key of adjacency_list dictionary represent start node of an edge and the value represent list of tuples where each tuple contains endnode of the edge(connected with the startnode) along with the cost of the edge
    return adjacency_list