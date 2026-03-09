from django.db import models
from django.utils import timezone

class Simulation(models.Model):
    STATUS_CHOICES = [
        ('READY', 'Ready'),
        ('RUNNING', 'Running'),
        ('PAUSED', 'Paused'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='READY')
    start_time = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    accumulated_time_ms = models.BigIntegerField(default=0) 

    def current_sim_time_ms(self):
        if self.status == 'RUNNING':
            now = timezone.now()
            if self.paused_at:
                delta = now - self.paused_at
            else:
                delta = now - self.start_time
            return self.accumulated_time_ms + int(delta.total_seconds() * 1000)
        return self.accumulated_time_ms

    def __str__(self):
        return f"Simulation - {self.status}"






class SimulationEvent(models.Model):
    ROLE_CHOICES = [
        ('IT', 'IT Manager'),
        ('LEGAL', 'Legal Counsel'),
        ('CEO', 'CEO'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    trigger_time_ms = models.BigIntegerField()
    message = models.TextField()
    decision_prompt = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.role} @ {self.trigger_time_ms/60000} min"






class SimulationResponse(models.Model):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    event = models.ForeignKey(SimulationEvent, on_delete=models.CASCADE)
    choice = models.BooleanField(null=True, blank=True)
    responded_at_ms = models.BigIntegerField(null=True, blank=True)
    is_missed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event.role} response: {self.choice}"
