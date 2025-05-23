# Generated by Django 4.2.20 on 2025-05-12 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0016_rename_date_created_budget_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="expensemanagement",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Approved", "Approved"),
                    ("Rejected", "Rejected"),
                ],
                default="Pending",
                max_length=20,
            ),
        ),
    ]
