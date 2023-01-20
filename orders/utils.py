import datetime

def generate_order_number(pk):
    #srtrf- string format of time
    current_datetime =datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 20230108114533 + pk
    order_number = current_datetime +'id'+str(pk)
    return order_number



def generate_shipping_number(pk):
    #srtrf- string format of time
    current_datetime =datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 20230108114533 + pk
    shipping_number = current_datetime +'S'+str(pk)
    return shipping_number