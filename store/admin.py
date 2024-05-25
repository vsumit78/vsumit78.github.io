from django.contrib import admin
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.builder import Builder
from .models.builder import Project
from .models.orders import Order



class Order_admin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'price', 'address', 'phone', 'date', 'status')



# Register your models here.
class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']


class AdminCategory(admin.ModelAdmin):
    list_display = ['name',]

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
class BuilderAdmin(admin.ModelAdmin):
    inlines = [ProjectInline]
    list_display = ['name', 'price_cost', 'price_cost_without_material', 'material_quality', 'design_looks', 'time', 'behaviour', 'past_experience_years', 'number_of_projects_done',
                    'cement_company', 'paint', 'tmt_bar', 'sanitary_ware', 'bathware', 'contact_no']



admin.site.register(Product, AdminProduct)
admin.site.register(Category , AdminCategory)
admin.site.register(Customer)
admin.site.register(Builder, BuilderAdmin)
admin.site.register(Order,Order_admin)
