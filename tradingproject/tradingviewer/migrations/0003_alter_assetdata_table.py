# Generated by Django 5.1.4 on 2025-01-02 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tradingviewer', '0002_assetdata_remove_transaction_unique_transaction_id'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='assetdata',
            table='asset_data',
        ),
    ]
