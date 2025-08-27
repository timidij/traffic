
from django.db import models

class TrafficLight(models.Model):
    RED = 'R'
    YELLOW = 'Y'
    GREEN = 'G'
    STATE_CHOICES = [
        (RED, 'Red'),
        (YELLOW, 'Yellow'),
        (GREEN, 'Green'),
    ]

    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=RED)
    last_changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_state_display()
