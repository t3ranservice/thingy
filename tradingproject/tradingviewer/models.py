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
        db_table = 'transactions'


class AssetData(models.Model):
    symbol = models.CharField(max_length=8)
    average_buy_price = models.FloatField
    average_sell_price = models.FloatField
    net = models.FloatField


# DELIMITER $$

# CREATE PROCEDURE CalculateAverageBuyPrice()
# BEGIN
#     -- Create a temporary table to store the results
#     CREATE TEMPORARY TABLE IF NOT EXISTS AvgBuyPrices (
#         symbol VARCHAR(8),
#         avg_price FLOAT
#     );

#     -- Clear the temporary table
#     TRUNCATE TABLE AvgBuyPrices;

#     -- Loop through all unique symbols
#     INSERT INTO AvgBuyPrices (symbol, avg_price)
#     SELECT 
#         symbol,
#         AVG(filled_price) AS avg_price
#     FROM 
#         transactions
#     WHERE 
#         direction = 'BUY'
#     GROUP BY 
#         symbol;

#     -- Select the results to show output (optional)
#     SELECT * FROM AvgBuyPrices;
# END$$

# DELIMITER ;
