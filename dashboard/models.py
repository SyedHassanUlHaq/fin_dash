from django.db import models

# Create your models here.
class Document(models.Model):
    equity_ticker = models.CharField(max_length=20)
    geography = models.CharField(max_length=10, null=True, blank=True)
    content_name = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=10, null=True, blank=True)
    content_type = models.CharField(max_length=100)
    published_date = models.DateField()
    fiscal_date = models.DateField(null=True, blank=True)
    fiscal_year = models.PositiveIntegerField(null=True, blank=True)
    fiscal_quarter = models.CharField(max_length=10, null=True, blank=True)
    periodicity = models.CharField(max_length=20, null=True, blank=True)
    is_missing = models.BooleanField(default=False)
    r2_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.equity_ticker} - {self.content_type} ({self.fiscal_year})"
