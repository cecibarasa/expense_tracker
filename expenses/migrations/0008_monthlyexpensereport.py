# Generated by Django 4.2.20 on 2025-04-29 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("expenses", "0007_expensemanagement_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="MonthlyExpenseReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("report_date", models.DateField(default=django.utils.timezone.now)),
                (
                    "total_expenses",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("total_income", models.DecimalField(decimal_places=2, max_digits=10)),
                ("net_savings", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
