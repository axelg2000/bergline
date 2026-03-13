from django.db import models


class DJSchedule(models.Model):
    STAGES = [
        ("berghain", "Berghain"),
        ("panorama_bar", "Panorama Bar"),
        ("saule", "Säule"),
    ]
    stage = models.CharField(max_length=50, choices=STAGES)
    dj_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.dj_name} @ {self.stage} ({self.start_time} - {self.end_time})"
