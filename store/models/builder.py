from django.db import models

from django.db import models

from django.db import models
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal
import json


class Builder(models.Model):
    name = models.CharField(max_length=100)
    price_cost = models.DecimalField(max_digits=10, decimal_places=2)
    price_cost_without_material = models.DecimalField(max_digits=10, decimal_places=2)
    material_quality = models.IntegerField(choices=[(1, 'Bad'), (2, 'Below Average'), (3, 'Average'), (4, 'Good'), (5, 'Best')])
    design_looks = models.IntegerField(choices=[(1, 'Bad'), (2, 'Below Average'), (3, 'Average'), (4, 'Good'), (5, 'Best')])
    time = models.IntegerField(choices=[(1, 'Too Late'), (2, 'Late'), (3, 'some late'), (4, 'On Time'), (5, 'Before Time')])
    behaviour = models.IntegerField(choices=[(1, 'Very Bad'), (2, 'Bad'), (3, 'Average'), (4, 'Good'), (5, 'Very Good')])
    builder_photo = models.ImageField(upload_to='builder_photos', null=True, blank=True)
    past_experience_years = models.IntegerField()
    number_of_projects_done = models.IntegerField(default=0)
    cement_company = models.CharField(max_length=100,default='Unknown')
    paint = models.CharField(max_length=100,default='Unknown')
    tmt_bar = models.CharField(max_length=100,default='Unknown')
    sanitary_ware = models.CharField(max_length=100,default='Unknown')
    bathware = models.CharField(max_length=100, default='Unknown')
    contact_no = models.CharField(max_length=15)


    def __str__(self):
        return self.name


class Project(models.Model):
    builder = models.ForeignKey(Builder, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='project_photos/', default='default_photo.jpg')



class HouseEstimation(models.Model):
    builder = models.ForeignKey('Builder', on_delete=models.CASCADE)
    floors = models.IntegerField()
    area_per_floor_list = models.CharField(max_length=1000)  # Store as string
    with_material = models.BooleanField(default=True)

    def set_area_per_floor_list(self, data):
        area_per_floor_list = [str(area) for area in data]
        self.area_per_floor_list = json.dumps(area_per_floor_list)

    def get_area_per_floor_list(self):
        return [int(area) for area in json.loads(self.area_per_floor_list)]


    def total_cost(self):
        total_area = sum(self.get_area_per_floor_list())
        base_price = self.builder.price_cost  # Initial price cost for the ground floor
        total_price = Decimal(0)

        for floor_num in range(self.floors):
            price_multiplier = Decimal(1.2) ** floor_num  # Increase price by 20% for each above floor
            if self.with_material:
                total_price += base_price * price_multiplier * self.get_area_per_floor_list()[floor_num]
            else:
                total_price += self.builder.price_cost_without_material * price_multiplier * self.get_area_per_floor_list()[floor_num]

        return total_price

    def __str__(self):
        return f"Estimation for {self.builder.name}: {self.total_cost()}"
