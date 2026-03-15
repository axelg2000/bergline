from django.db import models

from apps.messages.models import ParsedMessage


class MainQueueSnapshot(models.Model):
    LOCATIONS = [
        ("snake", "Snake"),
        ("concrete_blocks", "Concrete Blocks"),
        ("magic_cube", "Magic Cube"),
        ("kiosk", "Kiosk"),
        ("20m_behind_kiosk", "20m Behind Kiosk"),
        ("wriezener_karree", "Wriezener Karree"),
        ("metro_sign", "Metro Sign"),
    ]
    parsed_message = models.ForeignKey(ParsedMessage, on_delete=models.CASCADE, related_name="main_queue_snapshots")
    location = models.CharField(max_length=50, choices=LOCATIONS)
    confidence_score = models.FloatField()
    recorded_at = models.DateTimeField()

    def __str__(self):
        return f"Main queue at {self.location} ({self.recorded_at})"


class GuestlistSnapshot(models.Model):
    LOCATIONS = [
        ("barriers", "Barriers"),
        ("love_sculpture", "Love Sculpture"),
        ("garten_door", "Garten Door"),
        ("atm", "ATM"),
        ("park", "Park"),
    ]
    parsed_message = models.ForeignKey(ParsedMessage, on_delete=models.CASCADE, related_name="guestlist_snapshots")
    location = models.CharField(max_length=50, choices=LOCATIONS)
    confidence_score = models.FloatField()
    recorded_at = models.DateTimeField()

    def __str__(self):
        return f"Guestlist at {self.location} ({self.recorded_at})"
