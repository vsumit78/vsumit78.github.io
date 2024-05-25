from django.db import models
from django import forms

class HouseRequirements(models.Model):
    PLOT_VIEW_CHOICES = [
        ('North', 'North'),
        ('South', 'South'),
        ('East', 'East'),
        ('West', 'West'),
    ]

    KITCHEN_POSITION_CHOICES = [
        ('Ground Floor', 'Ground Floor'),
        ('First Floor', 'First Floor'),
        ('All Floors', 'All Floors'),
    ]

    BATHROOM_SIZE_CHOICES = [
        ('Big', 'Big'),
        ('Standard', 'Standard'),
        ('Small', 'Small'),
    ]

    plot_length = models.DecimalField(max_digits=10, decimal_places=2)
    plot_breadth = models.DecimalField(max_digits=10, decimal_places=2)
    plot_view = models.CharField(max_length=100, choices=PLOT_VIEW_CHOICES)
    no_of_floors = models.IntegerField()
    no_of_master_bedroom = models.IntegerField()
    kid_room_required = models.BooleanField(default=False)
    guest_room_required = models.BooleanField(default=False)
    kitchen_location = models.CharField(max_length=100, choices=KITCHEN_POSITION_CHOICES)
    balcony_required = models.BooleanField(default=False)
    parking_facility = models.BooleanField(default=False)
    garden_provision = models.BooleanField(default=False)
    bathroom_size_choice = models.CharField(max_length=100, choices=BATHROOM_SIZE_CHOICES)
    front_site = models.CharField(max_length=100, choices=[('road', 'Road'), ('other', 'Other property')])
    back_site = models.CharField(max_length=100, choices=[('road', 'Road'), ('other', 'Other property')])
    right_site = models.CharField(max_length=100, choices=[('road', 'Road'), ('other', 'Other property')])
    left_site = models.CharField(max_length=100, choices=[('road', 'Road'), ('other', 'Other property')])

    def __str__(self):
        return f"House Requirements: {self.id}"


