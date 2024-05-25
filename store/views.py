from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.builder import Builder
from decimal import Decimal
from django.db import models
from django.db.models import Max, Min
from .models.builder import HouseEstimation
from django.views import View
from .forms import HouseRequirementsForm
from .models.orders import Order
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from store.middlewares.auth import auth_middleware
from django.utils.decorators import method_decorator


class Index(View):

    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity == 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1

                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart ', request.session['cart'])

        return redirect('homepage')

    def get(self, request):
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}
        products = None

        categories = Category.get_all_categories()
        categoryID = request.GET.get('category')
        if categoryID:
            products = Product.get_all_products_by_categoryid(categoryID[0])
        else:
            products = Product.get_all_products()
        data = {}
        data['products'] = products
        data['categories'] = categories
        print('you are :  ', request.session.get('email'))
        return render(request, 'index.html', data)


from django.db.models import Max, Min
from decimal import Decimal


def builder_recommendation(request):
    if request.method == 'POST':
        # Normalize the data
        price_cost_weight = Decimal(request.POST.get('price_cost_weight'))
        material_quality_weight = Decimal(request.POST.get('material_quality_weight'))
        design_looks_weight = Decimal(request.POST.get('design_looks_weight'))
        time_weight = Decimal(request.POST.get('time_weight'))
        behaviour_weight = Decimal(request.POST.get('behaviour_weight'))

        # Weightage assignment (by the user)
        weights = {
            'price_cost': price_cost_weight,
            'material_quality': material_quality_weight,
            'design_looks': design_looks_weight,
            'time': time_weight,
            'behaviour': behaviour_weight,
        }

        # Normalize the weights
        total_weight = sum(weights.values())
        if total_weight != 100:
            return render(request, 'builder_form.html', {'error_message': 'Sum of weights should be 100%'})
        else:
            for key in weights:
                weights[key] /= total_weight

        # Calculate min and max values for each field
        min_price_cost = Decimal(Builder.objects.all().aggregate(min_price_cost=Min('price_cost'))['min_price_cost'])
        max_price_cost = Decimal(Builder.objects.all().aggregate(max_price_cost=Max('price_cost'))['max_price_cost'])
        min_material_quality = Decimal(
            Builder.objects.all().aggregate(min_material_quality=Min('material_quality'))['min_material_quality'])
        max_material_quality = Decimal(
            Builder.objects.all().aggregate(max_material_quality=Max('material_quality'))['max_material_quality'])
        min_design_looks = Decimal(
            Builder.objects.all().aggregate(min_design_looks=Min('design_looks'))['min_design_looks'])
        max_design_looks = Decimal(
            Builder.objects.all().aggregate(max_design_looks=Max('design_looks'))['max_design_looks'])
        min_time = Decimal(Builder.objects.all().aggregate(min_time=Min('time'))['min_time'])
        max_time = Decimal(Builder.objects.all().aggregate(max_time=Max('time'))['max_time'])
        min_behaviour = Decimal(Builder.objects.all().aggregate(min_behaviour=Min('behaviour'))['min_behaviour'])
        max_behaviour = Decimal(Builder.objects.all().aggregate(max_behaviour=Max('behaviour'))['max_behaviour'])

        builders = Builder.objects.all()
        rankings = []

        # Aggregation and ranking
        for builder in builders:
            score = (
                    weights['price_cost'] * normalize_price_cost(builder.price_cost, min_price_cost, max_price_cost) +
                    weights['material_quality'] * normalize(builder.material_quality, min_material_quality,
                                                            max_material_quality) +
                    weights['design_looks'] * normalize(builder.design_looks, min_design_looks, max_design_looks) +
                    weights['time'] * normalize(builder.time, min_time, max_time) +
                    weights['behaviour'] * normalize(builder.behaviour, min_behaviour, max_behaviour)
            )
            rankings.append((builder, score))

        rankings.sort(key=lambda x: x[1], reverse=True)

        return render(request, 'recommendation.html', {'rankings': rankings})

    return render(request, 'builder_form.html')


def normalize(value, min_value, max_value):
    if max_value != min_value:
        return (value - min_value) / (max_value - min_value)
    else:
        return Decimal(0)


def normalize_price_cost(price_cost, min_price_cost, max_price_cost):
    if max_price_cost != min_price_cost:
        return Decimal((max_price_cost - price_cost) / (max_price_cost - min_price_cost))
    else:
        return Decimal(0)

class Signup(View):

    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        postData = request.POST
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')

        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password)
        error_message = self.validateCustomer(customer)
        if not error_message:
            print(first_name, last_name, phone, email, password)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'signup.html', data)

    def validateCustomer(self, customer):
        error_message = None  # Initialize error_message variable
        if not customer.first_name:
            error_message = "First name is required"
        elif len(customer.first_name) < 3:
            error_message = 'First name must be at least 3 characters long'
        elif not customer.last_name:
            error_message = "last name required"
        elif len(customer.last_name) < 3:
            error_message = "last name must be 3 characters long"
        elif not customer.phone:
            error_message = "phone number required"
        elif len(customer.phone) < 10:
            error_message = "phone no. must be 10 charater long"
        elif len(customer.password) < 6:
            error_message = " password must be 6 char long"
        elif len(customer.email) < 5:
            error_message = "email must be 5 char long"
        elif customer.isExists():
            error_message = 'email already registered'

        return error_message


class Login(View):
    return_url =None
    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'email or password invalid !!'

        else:
            error_message = 'email or password invalid !!'
        return render(request, 'login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return redirect('login')


class Cart(View):
    def get(self, request):
        ids = (list(request.session.get('cart').keys()))
        products = Product.get_products_by_id(ids)
        print(products)
        return render(request, 'cart.html', {'products': products})


from .templatetags.cart import total_cart_price, multiply



from django.shortcuts import render
from django.views import View
from django.conf import settings
import razorpay

import razorpay
from django.conf import settings
from django.shortcuts import render
from django.views import View

class Checkout(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))

        if not all([address, phone, cart]):
            print("Missing checkout information.")
            return redirect('cart.html')

        # Calculate the total amount using the 'total_cart_price' filter
        total_amount = total_cart_price(products, cart)
        total_amount_paise = multiply(total_amount, 100)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        razorpay_order = client.order.create({
            'amount': total_amount_paise,  # Amount in paise
            'currency': 'INR',
            'receipt': 'order_rcptid_11',
            'payment_capture': '1'
        })

        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': total_amount_paise,
            'currency': 'INR',
            'address': address,
            'phone': phone,
            'products': products,
            'customer': customer
        }

        request.session['address'] = address
        request.session['phone'] = phone
        request.session['customer'] = customer
        request.session['cart'] = cart

        print('address')
        print('phone')
        print(customer)
        print('cart')

        return render(request, 'cart.html', context)




from django.shortcuts import render, redirect

class PaymentSuccess(View):
    def get(self, request):
        payment_id = request.GET.get('payment_id')
        order_id = request.GET.get('order_id')
        signature = request.GET.get('signature')

        address = "j6/30,jaitpura,varanasi"
        phone = "9305748254"
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        for product in products:
            order = Order(
                customer=Customer(id=customer),
                product=product,
                price=product.price,
                address=address,
                phone=phone,
                quantity=cart.get(str(product.id)),
                razorpay_order_id=order_id,
                razorpay_payment_id=payment_id,
                razorpay_payment_signature=signature,
                status=True
            )
            order.save()

        request.session['cart'] = {}
        context = {
            'payment_id': payment_id,
            'order_id': order_id,
        }
        return render(request, 'payment_success.html', context)


class OrderView(View):
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)

        return render(request,'orders.html' , {'orders': orders})


from decimal import Decimal


def estimate_cost(request):
    if request.method == 'POST':
        floors = int(request.POST.get('floors', 0))
        with_material = request.POST.get('with_material', False)
        with_material = bool(with_material)  # Convert to boolean

        # Initialize area per floor list
        area_per_floor_list = []
        for floor_num in range(1, floors + 1):
            area_key = f'area_floor_{floor_num}'
            area_per_floor = Decimal(request.POST.get(area_key, 0))
            area_per_floor_list.append(area_per_floor)

        estimations = []
        for builder in Builder.objects.all():
            # Create HouseEstimation object
            estimation = HouseEstimation(
                builder=builder,
                floors=floors,
                with_material=with_material
            )
            estimation.set_area_per_floor_list(area_per_floor_list)  # Set the area per floor list
            estimation.save()

            # Fetch additional information from the related Builder model
            builder_info = {
                'photo': builder.builder_photo.url,
                'past_experience_years': builder.past_experience_years,
                'number_of_projects_done': builder.number_of_projects_done,
                'contact_no': builder.contact_no
            }

            estimation.builder_info = builder_info
            estimations.append(estimation)

        return render(request, 'estimate_cost.html', {'estimations': estimations})

    return render(request, 'estimate_cost_form.html')





from django.shortcuts import render
from .forms import HouseRequirementsForm

def house_recommendation(request):
    if request.method == 'POST':
        form = HouseRequirementsForm(request.POST)
        if form.is_valid():
            # Retrieve form data
            plot_length = form.cleaned_data['plot_length']
            plot_breadth = form.cleaned_data['plot_breadth']
            plot_view = form.cleaned_data['plot_view']
            no_of_floors = form.cleaned_data['no_of_floors']
            no_of_master_bedroom = form.cleaned_data['no_of_master_bedroom']
            kid_room_required = form.cleaned_data['kid_room_required']
            guest_room_required = form.cleaned_data['guest_room_required']
            kitchen_location = form.cleaned_data['kitchen_location']
            balcony_required = form.cleaned_data['balcony_required']
            parking_facility = form.cleaned_data['parking_facility']
            garden_provision = form.cleaned_data['garden_provision']
            bathroom_size_choice = form.cleaned_data['bathroom_size_choice']
            front_site = form.cleaned_data['front_site']
            back_site = form.cleaned_data['back_site']
            right_site = form.cleaned_data['right_site']
            left_site = form.cleaned_data['left_site']

            # Generate 2D map recommendation based on form data
            map_image_url = generate_map(plot_length, plot_breadth, plot_view, no_of_floors, no_of_master_bedroom,
                                         kid_room_required, guest_room_required, kitchen_location, balcony_required,
                                         parking_facility, garden_provision, bathroom_size_choice,
                                         front_site, back_site, right_site, left_site)

            # Pass form and map image URL to the template
            return render(request, 'house_recommendation.html', {'form': form, 'map_image_url': map_image_url})
    else:
        form = HouseRequirementsForm()
    return render(request, 'house_recommendation.html', {'form': form})



import matplotlib.pyplot as plt


import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_map(plot_length, plot_breadth, plot_view, no_of_floors, no_of_master_bedroom,
                 kid_room_required, guest_room_required, kitchen_location, balcony_required,
                 parking_facility, garden_provision, bathroom_size_choice,
                 front_site, back_site, right_site, left_site):

    plot_length = float(plot_length)
    plot_breadth = float(plot_breadth)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(plot_breadth / 2, plot_length / 2))

    # Set the limits based on plot size
    ax.set_xlim(0, plot_breadth)
    ax.set_ylim(0, plot_length)

    # Plot the boundary of the plot
    ax.add_patch(patches.Rectangle((0, 0), plot_breadth, plot_length, edgecolor='black', facecolor='none'))

    # Define positions and sizes based on user inputs (simple example)
    offset = 2  # Offset for internal structures

    if parking_facility:
        # Add parking area
        ax.add_patch(patches.Rectangle((offset, offset), plot_breadth * 0.3, plot_length * 0.1, edgecolor='black', facecolor='gray', label='Parking'))
        offset += plot_length * 0.1 + 2

    if garden_provision:
        # Add garden area
        ax.add_patch(patches.Rectangle((plot_breadth * 0.7, plot_length - offset), plot_breadth * 0.3, plot_length * 0.1, edgecolor='black', facecolor='green', label='Garden'))
        offset += plot_length * 0.1 + 2

    if no_of_master_bedroom > 0:
        # Add master bedrooms
        for i in range(no_of_master_bedroom):
            ax.add_patch(patches.Rectangle((offset, plot_length - offset), plot_breadth * 0.3, plot_length * 0.2, edgecolor='black', facecolor='lightblue', label='Master Bedroom'))
            offset += plot_length * 0.2 + 2

    if kid_room_required:
        # Add kid room
        ax.add_patch(patches.Rectangle((offset, plot_length - offset), plot_breadth * 0.3, plot_length * 0.15, edgecolor='black', facecolor='pink', label='Kid Room'))
        offset += plot_length * 0.15 + 2

    if guest_room_required:
        # Add guest room
        ax.add_patch(patches.Rectangle((offset, plot_length - offset), plot_breadth * 0.3, plot_length * 0.15, edgecolor='black', facecolor='lightgreen', label='Guest Room'))
        offset += plot_length * 0.15 + 2

    # Add kitchen
    kitchen_height = plot_length * 0.1
    kitchen_y = offset if kitchen_location == 'Ground Floor' else plot_length - offset - kitchen_height
    ax.add_patch(patches.Rectangle((offset, kitchen_y), plot_breadth * 0.3, kitchen_height, edgecolor='black', facecolor='orange', label='Kitchen'))

    # Add other features (balcony, bathrooms, etc.)
    if balcony_required:
        # Add balconies to bedrooms
        for i in range(no_of_master_bedroom):
            balcony_x = offset + plot_breadth * 0.3 + 2
            balcony_y = plot_length - offset - (i * (plot_length * 0.2 + 2))
            ax.add_patch(patches.Rectangle((balcony_x, balcony_y), plot_breadth * 0.1, plot_length * 0.05, edgecolor='black', facecolor='purple', label='Balcony'))

    # Add bathroom
    # Ensure the bathroom_size_choice is in lowercase to match the dictionary keys
    bathroom_size_choice = bathroom_size_choice.lower()

    bathroom_size = {'big': 0.15, 'standard': 0.1, 'small': 0.05}
    bathroom_height = plot_length * bathroom_size[bathroom_size_choice]
    ax.add_patch(patches.Rectangle((offset, offset), plot_breadth * 0.2, bathroom_height, edgecolor='black', facecolor='cyan', label='Bathroom'))


    # Set labels and title
    ax.set_title('House Map')
    ax.set_xlabel('Width (ft)')
    ax.set_ylabel('Length (ft)')

    # Save the figure
    map_filename = 'static/2d_map.png'
    plt.savefig(map_filename)
    plt.close(fig)

    return map_filename



'''
in this django app can you  make a feature to provide recommended 2d map of house 
which is based on user requirement that is 
1. Your plot view
2. your plot depth
3. reuired no. of floor
4. no. of master  bedroom required in the house
5.dou you required kid separate room
6.dou you required extra guest room
7.kitchen should be on (ground floor/first floor/ all floors)
8.required balcony in bedrooms
9.parking facility in the house
10.garden provision in the house
11. bathroom space choice(big,standard,small)
12.site details a. front (road/other property) b.back(road/other property) c. right(road/other property) d.left(road/other property)'''
