from django.urls import path
from . import views
from .views import custom_logout, register
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)



urlpatterns = [
    path('', views.index, name='index'),
    path('search_expenses/', views.search_expenses, name='search_expenses'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('view_expenses/', views.view_expenses, name='view_expenses'),
    path('budget/', views.budget, name='budget'),
    path('add_budget/', views.add_budget, name='add_budget'),
    path('expense_report/', views.expense_report, name='expense_report'),
    path('monthly_expense/', views.monthly_expense_report, name='monthly_expense'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('income_report/', views.income_report, name='income_report'),
    path('profile/', views.user_profile, name='profile'),
    path('income/', views.income, name='income'),
    path('approve-expense/<int:expense_id>/', views.approve_expense, name='approve_expense'),
    path('reject-expense/<int:expense_id>/', views.reject_expense, name='reject_expense'),
    path('login/', views.login, name='login'),    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        extra_context={'hide_navbar': True}
    ), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html',
        extra_context={'hide_navbar': True}
    ), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        extra_context={'hide_navbar': True}
    ), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html',
        extra_context={'hide_navbar': True}
    ), name='password_reset_complete'),
    # path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
#     path('profile/', views.profile, name='profile'),
#     path('settings/', views.settings, name='settings'),

 ]