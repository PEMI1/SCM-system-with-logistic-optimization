// let autocomplete;

// function initAutoComplete(){
// autocomplete = new google.maps.places.Autocomplete(
//     document.getElementById('id_address'),
//     {
//         types: ['geocode', 'establishment'],
//         //default in this app is "IN" - add your country code
//         componentRestrictions: {'country': ['in']},
//     })
// // function to specify what should happen when the prediction is clicked
// autocomplete.addListener('place_changed', onPlaceChanged);
// }

// function onPlaceChanged (){
//     var place = autocomplete.getPlace();

//     // User did not select the prediction. Reset the input field or alert()
//     if (!place.geometry){
//         document.getElementById('id_address').placeholder = "Start tooo typing...";
//     }
//     else{
//         console.log('place name=>', place.name)
//     }
//     // get the address components and assign them to the fields
// }



//on clicking add_to_cart class button ajax request gets sent
//ajax request takes type, url, data and success function
//taking product_id and url from attributes 'data-id' & 'data-url' at vendor_detail.html
//on success we call the add_to_cart function at views which takes ajax request(with product_id) & returns HttpResponse ie.for html element with id='cart_counter' in navbar.html, render its value with the cart_count got from response
$(document).ready(function(){
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        

        product_id = $(this).attr('data-id');
        url =  $(this).attr('data-url');
        // data = {
        //     product_id:product_id,
        // }
        //no need to pass 'data' because product_id is in(passed by) url, but we need 'peoduct_id' because we are using it at $('#qty-'+product_id).html(response.qty)
       
        $.ajax({
            type: 'GET',
            url: url,
            //data: data,
            success:function(response){
                console.log(response)
                if(response.status=='login_required'){
                   swal(response.message, '', 'info').then(function(){
                    window.location = '/login';
                   })
                }
                else if (response.status=='Failed'){
                    swal(response.message, '', 'error')
                }
                else{
                     //for cart count badge
                    $('#cart_counter').html(response.cart_counter['cart_count']); //render id="cart_counter" in navbar.html
                    //for qty label
                    $('#qty-'+product_id).html(response.qty);//render id ="qty-{{item.product.id}}" in vendor_detail.html         


                    //handle price total in cart
                    //views.add_to_cart (cart_amount <- context_processors.get_cart_amounts) -> custom.js.add_to_cart.applyCartAmounts -> function applyCartAmounts()
                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']

                    )
                    
                }
            }
        })
    })

    
    //place the cart item quantity at qty label on vendor_details page
    //look through each item in cart (from .item_qty class in vendor_detail.html)
    //the_id ="qty-{{item.product.id}}"= "qty-id of each product in the cart"(ids are dynamically created at vendor_detail.html)
    //taking ids and qty from attributes 'id' & 'data-qty' at vendor_detail.html
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty =$(this).attr('data-qty')
        console.log(qty)
        $('#'+the_id).html(qty) //render id ="qty-{{item.product.id}}" in vendor_detail.html
    })

  

    //Drecrease Cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        

        product_id = $(this).attr('data-id');
        url =  $(this).attr('data-url');

        cart_id = $(this).attr('id');


        
        $.ajax({
            type: 'GET',
            url: url,
            
            success:function(response){
                console.log(response)
                if(response.status=='login_required'){
                    swal(response.message, '', 'info').then(function(){
                     window.location = '/login';
                    })
                 }
                else if(response.status=='Failed'){
                    swal(response.message, '', 'error')
                }
                else{
                     //for cart count badge
                    $('#cart_counter').html(response.cart_counter['cart_count']); //render id="cart_counter" in navbar.html
                    //for qty label
                    $('#qty-'+product_id).html(response.qty);//render id ="qty-{{item.product.id}}" in vendor_detail.html         


                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']

                    )
                    if(window.location.pathname =='/cart/'){

                        //delete item if qty=0 at cart page
                        removeCartItem(response.qty, cart_id)
                        checkEmptyCart()
                    }
                }
               
            }
        })
    })


    //place the cart item quantity at qty label on cart page

    $('.product_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty =$(this).attr('data-qty')
        console.log(qty)
        $('#'+the_id).html(qty) //render id ="qty-{{item.product.id}}" in vendor_detail.html
    })

     //Delete item from Cart
     $('.delete_cart').on('click', function(e){
        e.preventDefault();
        
        cart_id = $(this).attr('data-id');
        url =  $(this).attr('data-url');


        
        $.ajax({
            type: 'GET',
            url: url,
            
            success:function(response){
                console.log(response)
                if(response.status=='Failed'){
                    swal(response.message, '', 'error')
                }
                else{
                     //for cart count badge
                    $('#cart_counter').html(response.cart_counter['cart_count']); //render id="cart_counter" in navbar.html
                    swal(response.status, response.message, 'success')

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']

                    )

                    removeCartItem(0, cart_id)
                    checkEmptyCart();
                }
               
            }
        })
    })



    //delete the cart html element if the qty is 0(helper function to remove item when delete button is pressed)
    function removeCartItem(cartItemQty, cart_id){  
            if (cartItemQty <=0){
                ///delete the cart html element
                document.getElementById("cart-item-"+cart_id).remove()
            }   
    }

    //check if the cart is empty after deleting an item from cart
    //we will find if cart is empty from cart_counter value
    function checkEmptyCart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if (cart_counter==0){
            document.getElementById("empty-cart").style.display="block";
        }
    }

    //apply cart amounts
    function applyCartAmounts(subtotal, tax, grand_total){
        //total should be applied only when user is inside cart page
        if  (window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(grand_total)    
        }
       
    }


    

    
        
});



