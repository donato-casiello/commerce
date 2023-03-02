# Generated by Django 4.1.7 on 2023-03-02 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0004_rename_auctions_auction"),
    ]

    operations = [
        migrations.RemoveField(model_name="auction", name="bid",),
        migrations.AddField(
            model_name="auction",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="auction",
            name="description",
            field=models.TextField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name="auction",
            name="owner",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
