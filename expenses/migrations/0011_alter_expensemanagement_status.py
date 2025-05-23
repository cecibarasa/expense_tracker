# Generated by Django 4.2.20 on 2025-04-30 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0010_expensemanagement_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expensemanagement",
            name="status",
            field=models.CharField(
                choices=[("PENDING", "Pending"), ("PAID", "Paid")],
                default="PAID",
                max_length=20,
            ),
        ),
    ]
