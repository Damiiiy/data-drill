from django.contrib import admin
from .models import Simulation, SimulationEvent, SimulationResponse


# Register your models here.

admin.site.register(Simulation)
admin.site.register(SimulationEvent)
admin.site.register(SimulationResponse)


