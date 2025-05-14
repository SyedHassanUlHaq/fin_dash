from django.db import models

# Create your models here.
class Document(models.Model):
    equity_ticker = models.CharField(max_length=20)
    content_type = models.CharField(max_length=100)
    fiscal_year = models.PositiveIntegerField()
    fiscal_quarter = models.CharField(max_length=10, null=True, blank=True)
    published_date = models.DateField()
    is_missing = models.BooleanField(default=False)
    r2_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.equity_ticker} - {self.content_type} ({self.fiscal_year})"