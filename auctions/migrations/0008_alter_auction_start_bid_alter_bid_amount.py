# Generated by Django 4.1.7 on 2023-03-05 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0007_alter_auction_start_bid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auction",
            name="start_bid",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.AlterField(
            model_name="bid",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]