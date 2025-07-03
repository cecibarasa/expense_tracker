from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

@shared_task(name='expenses.tasks.daily_prompt')
def daily_prompt():
    User = get_user_model()
    for user in User.objects.all():
        if user.email:
            print(f"Sending daily prompt to: {user.email}")  # <-- Add this line
            send_mail(
                subject="Did you spend anything today?",
                message=(
                    f"Hello {user.username},\n\n"
                    "Did you spend anything today? If yes, please log in and record your expenses: "
                    "https://expense-tracker-k4xy.onrender.com/add_expense/\n\n"
                    "Thank you for using Expense Tracker!"
                ),
                from_email="cecibarasa@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )