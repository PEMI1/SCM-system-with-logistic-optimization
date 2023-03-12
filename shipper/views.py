from django.http import JsonResponse, HttpResponse
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

from accounts.models import  Road, Node, Edge, DataStatus
#routing
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
import numpy as np
import json
from django.contrib.gis.geos import MultiLineString
from shapely.geometry import LineString
from sklearn.neighbors import KDTree

import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt


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


def dispatch_container(request):
    return render(request, 'shipper/route_road.html')

def route_road(request):
    road = serialize('geojson', Road.objects.all())
    return HttpResponse(road, content_type='json')#just return httpresponse containing serialized objects of LocalAddress in json format

# Create a nearest neighbor finding function using the KDTree
def nearest_neighbor(source, destination, kdtree):
    source = np.array([[source.x, source.y]])
    destination = np.array([[destination.x, destination.y]])
    distances, indices = kdtree.query(np.concatenate([source, destination]), return_distance=True, k=1)
    return indices[0][0], indices[1][0]

def nearest_neighbor_endpoint(request):
    # Retrieve the source and destination marker coordinates from the request data***************************************************************************
    payload = json.loads(request.body)
    source_coords = payload.get('source')
    destination_coords = payload.get('destination')
    print(type(source_coords))
    print(source_coords)
    print(destination_coords)

    #Convert coordinates to point form
    source = Point(source_coords[0], source_coords[1])
    destination = Point(destination_coords[0], destination_coords[1])

    # Contruct road graph*************************************************************************************************************************************
    segments = gpd.read_file('C:\\Users\\hp\\Desktop\\segment-intersection.shp')

    G = nx.Graph()

    for index, row in segments.iterrows():
        # Add nodes for each endpoint of the line segment
        node1 = (row['lat_n1'], row['long_n1'])
        node2 = (row['lat_n2'], row['long_n2'])
        G.add_node(node1)
        G.add_node(node2)

        # Add an edge between the two nodes
        G.add_edge(node1, node2, weight=row['length_m'])

    # Draw the graph and label the nodes and edges
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # Show the plot
    #plt.show()

    # Nearest neighbor node search*******************************************************************************************************************************
    # Get all the nodes in G and pass them to fitKDTree_toThe_DatabaseNodes()
    all_nodes = list(G.nodes())  
    #create KDTree from the nodes of the graph G
    kdtree = fitKDTree_toThe_DatabaseNodes(all_nodes)
    print(type(kdtree))

    # Call the nearest neighbor finding function to get the nearest neighbors in numpy.int64 type
    nearest_source, nearest_destination = nearest_neighbor(source, destination, kdtree)
    print(type(nearest_source))

    # Get the coordinates of the nearest points and convert it to list type
    #the nearest_source and nearest_destination are of type numpy.int64 and JSON responses can only contain serializable data types. 
    #To resolve the issue,convert the nearest_source and nearest_destination to a serializable data type, such as a list or a tuple, before returning it as a JSON response
    nearest_source_coords = list(kdtree.data[nearest_source])
    nearest_destination_coords = list(kdtree.data[nearest_destination])

    print(nearest_source_coords)
    print(nearest_destination_coords)

    #perform floyd warshall algorithm********************************************************************************************************************************
    predecessor, distance = floyd_warshall_predecessor_and_distance(G, "weight")
    for i, (key, value) in enumerate(predecessor.items()):
        print(key, value)
        if i == 1:
            break
    first_key1, first_value1 = next(iter(distance.items()))
    print(first_key1, first_value1)

    path = reconstruct_path(tuple(nearest_source_coords,),tuple(nearest_destination_coords,), predecessor)
    print(path)

    #convert path from tuple to list
    path_coords = [[point[0], point[1]] for point in path]

    all_nodes = []

    for i in range(len(path_coords)-1):
        u, v = path_coords[i], path_coords[i+1]
        u_x, u_y = u[0], u[1]
        v_x, v_y = v[0], v[1]

        roads = Road.objects.filter(lat_n1__in=[u_x, v_x], lat_n2__in=[u_x, v_x], long_n1__in=[u_y, v_y], long_n2__in=[u_y, v_y])
        print(roads)

        for road in roads:
            if isinstance(road.geom, MultiLineString):
                for line_string in road.geom:
                    line = LineString(line_string)
                    coords = line.coords

                    temp = []
                    for coord in coords:
                        temp.append(coord)
                    if all_nodes and len(temp) > 0 and all_nodes[-1] != temp[0]:
                        temp = temp[::-1]
                    for t in temp:
                        all_nodes.append(t)
            # elif isinstance(road.geom, LineString):
            #     coords = np.array(road.geom.coords)
            #     for coord in coords:
            #         all_nodes.append(coord)
            print(all_nodes)
            print("@@@@@@@@@@@@@@@@")

    all_nodes = [(lat, lng) for lng, lat in all_nodes]
    print(all_nodes)

    # Return the nearest neighbors & shortest path as a JSON response
    return JsonResponse({
        'nearest_source': nearest_source_coords,
        'nearest_destination': nearest_destination_coords,
        'path': all_nodes,
    })


#convert the nodes into a suitable data structure(KDTree) that can be used to find nearest road network node from the selected source and destination coordinates
def fitKDTree_toThe_DatabaseNodes(nodes):
    nodes_array = np.array([[node[0], node[1]] for node in nodes]) #The KDTree expects an np.array input. So put all the nodes's coordinates into an np.array ie.np.array wil be an array of coordinates of float type
    kdtree = KDTree(nodes_array) # Create the KDTree and fit it to the nodes
    print('****************KDTREE*********************\n')
    print(kdtree)
    return kdtree

def floyd_warshall_predecessor_and_distance(G, weight="weight"):
    from collections import defaultdict

    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    dist = defaultdict(lambda: defaultdict(lambda: float("inf")))
    for u in G:
        dist[u][u] = 0
    pred = defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not G.is_directed()
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = u
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = v
    for w in G:
        dist_w = dist[w]  # save recomputation
        for u in G:
            dist_u = dist[u]  # save recomputation
            for v in G:
                d = dist_u[w] + dist_w[v]
                if dist_u[v] > d:
                    dist_u[v] = d
                    pred[u][v] = pred[w][v]
    return dict(pred), dict(dist)

def reconstruct_path(source, target, predecessors):
    if source == target:
        return []
    prev = predecessors[source]
    curr = prev[target]
    path = [target, curr]
    while curr != source:
        curr = prev[curr]
        path.append(curr)
    return list(reversed(path))
