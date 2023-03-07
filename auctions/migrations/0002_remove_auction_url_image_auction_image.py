# Generated by Django 4.1.7 on 2023-03-07 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="auction", name="url_image",),
        migrations.AddField(
            model_name="auction",
            name="image",
            field=models.ImageField(blank=True, upload_to="auctions_images/"),
        ),
    ]