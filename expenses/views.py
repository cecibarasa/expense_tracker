from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *  # Import all models
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from datetime import date
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from datetime import datetime
import random
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth.models import Group
import random
import string
from django.core.mail import send_mail
from decimal import Decimal




def generate_random_password(length=12):
    """Generate a strong random password."""
    chars = string.ascii_letters + string.digits + string.punctuation
    # Ensure at least one lowercase, one uppercase, one digit, and one punctuation
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]
    password += [random.choice(chars) for _ in range(length - 4)]
    random.shuffle(password)
    return ''.join(password)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # Redirect to the homepage after successful login
        else:
            # Pass an error message to the template
            return render(request, 'login.html', {
                'error': 'Invalid username or password. Please try again.',
                'hide_navbar': True
            })

    return render(request, 'login.html', {'hide_navbar': True})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists. Please choose a different username.',
                'hide_navbar': True
            })

        # Create a regular user (not a superuser)
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return redirect('login')  # Redirect to the login page after successful registration

    return render(request, 'register.html', {'hide_navbar': True})

def custom_logout(request):
    logout(request)  # Log out the user
    return render(request, 'logout.html', {'hide_navbar': True})  # Render the logout page with the message

@login_required
def index(request):
    if request.method == 'POST':
        # Handle form submission
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        CURRENCY_CHOICES = ['USD', 'KES', 'EUR', 'GBP', 'INR']
        currency = request.POST.get('currency')
        # Validate currency
        if currency not in CURRENCY_CHOICES:
            return render(request, 'index.html', {
                'error': 'Invalid currency selected.',
                'budgets': Budget.objects.filter(user=request.user),
            })
        # Validate amount

        # Save the expense to the database
        expense = ExpenseManagement(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            date=date,
            description=description,
            currency=currency
            
        )
        expense.save()
        return redirect('index')  # Redirect to refresh the page
    
    user = request.user
    today = timezone.now().date()
    expenses_today = ExpenseManagement.objects.filter(user=user, date=today)
    total_spent = expenses_today.aggregate(total=models.Sum('amount'))['total'] or 0

    has_expenses_today = total_spent > 0

    # Only send if user has spent today (email logic)
    if has_expenses_today:
        expense_list = "\n".join(
            f"{expense.title}: {intcomma(expense.amount)} ({expense.category})"
            for expense in expenses_today
        )
        send_mail(
            subject="Your Daily Expense Summary",
            message=(
                f"Hello {user.username},\n\n"
                f"Here is your expense summary for today ({today}):\n\n"
                f"{expense_list}\n\n"
                f"Total spent today: {intcomma(total_spent)}\n\n"
                f"Keep tracking your expenses!\n\n"
                f"Expense Tracker Team"
            ),
            from_email="cecibarasa@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )


    # Fetch the most recent expense
    current_expense = ExpenseManagement.objects.filter(user=request.user).order_by('-timestamp').first()

    # Calculate total expenses
    total_expenses = ExpenseManagement.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch all income for the logged-in user
    total_income = IncomeManagement.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate net savings
    net_savings = total_income - total_expenses
    
    # Fetch all budgets for the logged-in user
    budgets = Budget.objects.filter(user=request.user)
    for budget in budgets:
        actual_expenses = ExpenseManagement.objects.filter(
            user=request.user, category=budget.category
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        budget.actual_amount = actual_expenses
        budget.remaining_budget = budget.budgeted_amount - actual_expenses

        # 50% alert logic (fix: use Decimal('0.5'))
        if not budget.half_alert_sent and Decimal(actual_expenses) >= Decimal('0.5') * budget.budgeted_amount:
            send_mail(
                subject='Budget 50% Reached Alert',
                message=(
                    f'Dear {request.user.username},\n\n'
                    f'You have used 50% of your budget for "{budget.category}".\n'
                    f'Your budgeted amount is {intcomma(budget.budgeted_amount)}, and you have spent {intcomma(actual_expenses)}.\n\n'
                    f'Please review your expenses to stay on track.\n\n'
                    f'Thank you,\nExpense Tracker Team'
                ),
                from_email='cecibarasa@gmail.com',
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            budget.half_alert_sent = True
            budget.save()
    
    # Fetch monthly expenses grouped by title
    today = now().date()
    selected_month = now().date().month
    selected_month_name = today.strftime('%B')
    selected_year = today.year
    
    # Fetch expenses for the selected month
    monthly_expenses = (
        ExpenseManagement.objects.filter(user=request.user, date__month=selected_month)
        .annotate(month=ExtractMonth('date'))
        .values('title')
        .annotate(total_amount=Sum('amount'))
        .order_by('title')
    )

    # Debugging output
    # print(f"Selected Month: {selected_month}")
    # print(f"Monthly Expenses: {monthly_expenses}")

    # Prepare data for the bar graph
    categories = list(set(expense['title'] for expense in monthly_expenses))  # Unique categories
    category_data = {category: 0 for category in categories}  # Initialize data for each category

    # Calculate total amount for each category
    total_amount = 0
    for expense in monthly_expenses:
        category = expense['title']
        total_amount += float(expense['total_amount'])  # Convert Decimal to float and accumulate
        category_data[category] = float(expense['total_amount'])  # Convert Decimal to float

    # Generate random colors for each category
    category_colors = {
        category: {
            'background': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.5)',
            # 'border': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)'
        }
        for category in categories
    }

    income = IncomeManagement.objects.filter(user=request.user)

    total_income = income.aggregate(Sum('amount'))['amount__sum'] or 0
    # Calculate net savings
    net_savings = total_income - total_expenses
    # Fetch all budgets for the logged-in user

    return render(request, 'index.html', {
        'current_expense': current_expense,
        'has_expenses_today': has_expenses_today,
        'selected_month_name': selected_month_name,
        'categories': json.dumps(categories),  # Serialize categories
        'category_data': json.dumps(category_data),  # Serialize category data
        'category_colors': json.dumps(category_colors),  # Serialize category colors
        'monthly_expenses': monthly_expenses,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_savings': net_savings,
        'budgets': budgets,
        'income': income,
    })

def search_expenses(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Filter by title and date range
        expenses = ExpenseManagement.objects.filter(
            title__icontains=search_query,
            user=request.user,
            date__range=[start_date, end_date]
        )
    else:
        expenses = ExpenseManagement.objects.filter(user=request.user)
    return render(request, 'index.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount').replace(',', '') 
        category = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')

        # Save the expense to the database
        expenses = ExpenseManagement(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            date=date,
            description=description
        )
        expenses.save()
        return redirect('index')  # Added redirect to refresh the page

    return render(request, 'add_expense.html')

@login_required
def view_expenses(request):
    user = request.user

    # Fetch all expenses for the logged-in user
    expenses = ExpenseManagement.objects.filter(user=request.user).order_by('-date')

    # Calculate total expenses
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    #display year
    current_year = datetime.now().year  # Get the current year

    return render(request, 'view_expenses.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'year': current_year,  # Pass the year to the template
    })

@login_required
def approve_expense(request, expense_id):
    expense = get_object_or_404(ExpenseManagement, id=expense_id, user=request.user)
    expense.status = 'Approved'
    expense.save()
    return redirect('view_expenses')

@login_required
def reject_expense(request, expense_id):
    expense = get_object_or_404(ExpenseManagement, id=expense_id, user=request.user)
    expense.status = 'Rejected'
    expense.save()
    return redirect('view_expenses')

@login_required
def expense_report(request):
    user = request.user
    selected_month = None
    selected_year = None
    expenses_by_category = {}

    if request.method == 'POST':
        selected_month = int(request.POST.get('month'))
        selected_year = int(request.POST.get('year'))

        # Filter expenses by the selected month and year
        expenses = ExpenseManagement.objects.filter(
            user=user,
            date__month=selected_month,
            date__year=selected_year
        ).order_by('-date')

        # Group expenses by category and calculate the total for each category
        expenses_by_category = (
            expenses.values('category')
            .annotate(total_amount=Sum('amount'))
            .order_by('category')
        )
        print({'expenses_by_category': expenses_by_category})
        # Calculate total expenses for the selected month
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        # Get the selected month's name
        selected_month_name = datetime(2025, selected_month, 1).strftime('%B')
        print({'selected_month_name': selected_month_name})
        return render(request, 'expense_report.html', {
            'expenses': expenses,
            'total_expenses': total_expenses,
            'selected_month': selected_month,
            'selected_month_name': selected_month_name,
            'selected_year': selected_year,
            'expenses_by_category': expenses_by_category,
        })


def user_profile(request):
    if request.method == 'POST':
        user = request.user
        profile_picture = request.FILES.get('profile_picture')
        bio = request.POST.get('bio')
        date_of_birth = request.POST.get('date_of_birth')

        profile = UserProfile(
            user=user,
            profile_picture=profile_picture,
            bio=bio,
            date_of_birth=date_of_birth
        )
        profile.save()
        return redirect('index')  # Added redirect to refresh the page

    return render(request, 'profile.html')

@login_required
def income(request):
    if request.method == 'POST':
        source = request.POST.get('source')  # Correctly retrieve the source
        amount = request.POST.get('amount')
        date = request.POST.get('date')

        if not source:
            return render(request, 'income.html', {
                'error': 'Source is required.',
                'income': IncomeManagement.objects.filter(user=request.user),
                'total_income': IncomeManagement.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0,
            })

        # Save the income
        IncomeManagement.objects.create(
            user=request.user,
            source=source,
            amount=amount,
            date=date
        )
        return redirect('income')

    # Fetch all incomes for the logged-in user
    income = IncomeManagement.objects.filter(user=request.user)
    total_income = income.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'income.html', {
        'income': income,
        'total_income': total_income,
    })

@login_required
def add_budget(request):
    if request.method == 'POST':
        category = request.POST.get('category')  # Correctly retrieve the category
        budgeted_amount = request.POST.get('budgeted_amount')
        currency = request.POST.get('currency')

        # Validate currency
        valid_currencies = ['USD', 'KES', 'EUR', 'GBP', 'INR']
        if currency not in valid_currencies:
            return render(request, 'budget.html', {
                'error': 'Invalid currency selected.',
                'budgets': Budget.objects.filter(user=request.user),
            })

        # Save the budget
        Budget.objects.create(
            user=request.user,
            category=category,
            budgeted_amount=budgeted_amount,
            currency=currency
        )
        return redirect('budget')
    
    return render(request, 'add_budget.html')

@login_required
def budget(request):
    # Fetch budgets and calculate actual expenses
    budgets = Budget.objects.filter(user=request.user)
    for budget in budgets:
        actual_expenses = ExpenseManagement.objects.filter(
            user=request.user, category=budget.category
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        budget.actual_amount = actual_expenses
        budget.remaining_budget = budget.budgeted_amount - actual_expenses

    return render(request, 'budget.html', {'budgets': budgets})

@login_required
def monthly_expense_report(request):
    user = request.user
    selected_month = None
    selected_month_name = None
    total_amount = 0
    categories = []
    category_data = {}
    category_colors = {}

    if request.method == 'POST':
        selected_month = int(request.POST.get('month'))
        selected_month_name = datetime(2025, selected_month, 1).strftime('%B')

        # Fetch expenses for the selected month
        monthly_expenses = (
            ExpenseManagement.objects.filter(user=user, date__month=selected_month)
            .annotate(month=ExtractMonth('date'))
            .values('title')
            .annotate(total_amount=Sum('amount'))
            .order_by('title')
        )

        # Debugging output
        # print(f"Selected Month: {selected_month}")
        # print(f"Monthly Expenses: {monthly_expenses}")

        # Prepare data for the bar graph
        categories = list(set(expense['title'] for expense in monthly_expenses))  # Unique categories
        category_data = {category: 0 for category in categories}  # Initialize data for each category

        # Calculate total amount for each category
        total_amount = 0
        for expense in monthly_expenses:
            category = expense['title']
            total_amount += float(expense['total_amount'])  # Convert Decimal to float and accumulate
            category_data[category] = float(expense['total_amount'])  # Convert Decimal to float

        # Generate random colors for each category
        category_colors = {
            category: {
                'background': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.2)',
                'border': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)'
            }
            for category in categories
        }

        return render(request, 'monthly_expense.html', {
            'monthly_expenses': monthly_expenses,
            'total_amount': total_amount,
            'selected_month_name': selected_month_name,
            'categories': json.dumps(categories),  # Serialize categories
            'category_data': json.dumps(category_data),  # Serialize category data
            'category_colors': json.dumps(category_colors),  # Serialize category colors
        })

    # Default response for GET requests
    return render(request, 'monthly_expense.html', {
        'monthly_expenses': [],
        'total_amount': 0,
        'selected_month_name': None,
        'categories': json.dumps([]),  # Empty categories
        'category_data': json.dumps({}),  # Empty category data
        'category_colors': json.dumps({}),  # Empty category colors
    })

@login_required
def income_report(request):
    user = request.user
    selected_month = None
    selected_month_name = None
    total_income = 0
    income_by_source = {}

    if request.method == 'POST':
        # Get the selected month from the form
        selected_month = int(request.POST.get('month'))
        selected_month_name = datetime(2025, selected_month, 1).strftime('%B')

        # Fetch income for the selected month
        income = IncomeManagement.objects.filter(user=user, date__month=selected_month).order_by('-date')

        # Group income by source and calculate the total for each source
        income_by_source = (
            income.values('source')
            .annotate(total_amount=Sum('amount'))
            .order_by('source')
        )

        # Calculate total income for the selected month
        total_income = income.aggregate(Sum('amount'))['amount__sum'] or 0

        return render(request, 'income_report.html', {
            'income': income,
            'total_income': total_income,
            'selected_month': selected_month,
            'selected_month_name': selected_month_name,
            'income_by_source': income_by_source,
        })

    # Default response for GET requests
    return render(request, 'income_report.html', {
        'income': [],
        'total_income': 0,
        'selected_month': None,
        'selected_month_name': None,
        'income_by_source': {},
    })