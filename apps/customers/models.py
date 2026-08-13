from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, unique=True)
    city = models.CharField(max_length=50)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email}) from {self.city}"
