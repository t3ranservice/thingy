# Generated by Django 5.1.4 on 2024-12-30 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=8)),
                ('direction', models.CharField(max_length=5)),
                ('filled_value', models.FloatField()),
                ('filled_price', models.FloatField()),
                ('filled_quantity', models.FloatField()),
                ('fee', models.FloatField()),
                ('timestamp', models.BigIntegerField()),
                ('transaction_id', models.TextField(unique=True)),
            ],
            options={
                'db_table': 'transactions',
                'constraints': [models.UniqueConstraint(fields=('transaction_id',), name='unique_transaction_id')],
            },
        ),
    ]