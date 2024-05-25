from django.urls import path
from .views import Index, Signup, builder_recommendation, estimate_cost, Login, house_recommendation, logout, Cart, Checkout, OrderView, PaymentSuccess
from .middlewares.auth import auth_middleware
urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('signup/', Signup.as_view(), name='signup'),
    path('builder_recommendation', builder_recommendation, name='builder_recommendation'),
    path('estimate_cost', estimate_cost, name='estimate_cost'),
    path('house_recommendation', house_recommendation, name='house_recommendation'),
    path('login', Login.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('cart', auth_middleware(Cart.as_view()), name='cart'),
    path('check-out', Checkout.as_view(), name='checkout'),
    path('orders', auth_middleware(OrderView.as_view()), name='orders'),
    path('payment_success/', PaymentSuccess.as_view(), name='payment_success')
]
