from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import *
from django.db.models import Sum

@receiver(post_save, sender=ExpenseManagement)
def check_budget_exceeded(sender, instance, **kwargs):
    user = instance.user
    category = instance.category
    actual_expenses = ExpenseManagement.objects.filter(
        user=user, category=category
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    budget = Budget.objects.filter(user=user, category=category).first()
    if budget and actual_expenses > budget.budgeted_amount:
        # Send email alert
        send_mail(
            subject='Budget Exceeded Alert',
            message=f'You have exceeded your budget for {category}. '
                    f'Your budgeted amount was {budget.budgeted_amount}, but you have spent {actual_expenses}.',
            from_email='cecibarasa@gmail.com',  # Replace with your email
            recipient_list=[user.email],  # Send to the user's email
            fail_silently=False,
        )