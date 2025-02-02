from decimal import Decimal

from django.db import models


class City(models.Model):
    name = models.CharField(verbose_name="City", max_length=50)
    state = models.CharField(verbose_name="State", max_length=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "state"], name="unique_city_state")
        ]


class FuelStation(models.Model):
    opis_id = models.IntegerField(verbose_name="OPIS Truckstop ID", null=False)
    name = models.CharField(verbose_name="Truckstop Name", null=False, max_length=50)
    address = models.CharField(verbose_name="Address", max_length=50)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING)
    rack_id = models.IntegerField(verbose_name="Rack ID")
    gallon_price = models.DecimalField(max_digits=10, decimal_places=9)
    latitude = models.DecimalField(
        max_digits=8, decimal_places=5, default=Decimal(0.00000)
    )
    longitude = models.DecimalField(
        max_digits=8, decimal_places=5, default=Decimal(0.00000)
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["city", "name"], name="unique_fuel_stop")
        ]
