from django.db import models

class Transaction(models.Model):
    symbol = models.CharField(max_length=8)
    direction = models.CharField(max_length=5)
    filled_value = models.FloatField()
    filled_price = models.FloatField()
    filled_quantity = models.FloatField()
    fee = models.FloatField()
    timestamp = models.BigIntegerField()
    transaction_id = models.TextField(unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['transaction_id'], name='unique_transaction_id')
        ]
        db_table = 'transactions'