from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

CURRENCY_CHOICES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('KES', 'Kenyan Shilling'),
    ('GBP', 'British Pound'),
    ('INR', 'Indian Rupee'),
    ('JPY', 'Japanese Yen'),
    ('AUD', 'Australian Dollar'),
    ('CAD', 'Canadian Dollar'),
    ('CHF', 'Swiss Franc'),
    ('CNY', 'Chinese Yuan'),
    ('NZD', 'New Zealand Dollar'),
    ('ZAR', 'South African Rand'),
    ('SGD', 'Singapore Dollar'),
    ('HKD', 'Hong Kong Dollar'),
    ('SEK', 'Swedish Krona'),
    ('NOK', 'Norwegian Krone'),
    ('DKK', 'Danish Krone'),
    ('MXN', 'Mexican Peso'),
    ]

class ExpenseManagement(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('TRANSPORT', 'Transport'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('RENT', 'Rent'),
        ('UTILITIES', 'Utilities'),
        ('HEALTH', 'Health'),
        ('OTHER', 'Other'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # Ensure this field is not nullable
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )

    def __str__(self):
        return f"{self.title} - {self.amount}"

class UserAuthentication(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class IncomeManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='KES')  # Added currency field
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class ExpenseReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateField(default=timezone.now)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    net_savings = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Report for {self.user.username} on {self.report_date}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    budgeted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    half_alert_sent = models.BooleanField(default=False) # alert showing if the user has finished 50%
    alert_sent = models.BooleanField(default=False)  # New field to track email alert status
    
    def __str__(self):
        return f"{self.category} - {self.budgeted_amount} {self.currency}"

class MonthlyExpenseReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateField(default=timezone.now)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    net_savings = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Monthly Report for {self.user.username} on {self.report_date}"
    # Get today's date
    today = timezone.now().date()
    # Filter expenses for today
    expenses_today = ExpenseManagement.objects.filter(date=today)