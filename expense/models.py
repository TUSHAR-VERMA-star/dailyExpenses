from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, related_name='expenses', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_method = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"
