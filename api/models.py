from django.db import models

class Transaction(models.Model):
    transaction_date = models.DateField()
    business_facility = models.CharField(max_length=100)
    units = models.IntegerField()
    co2_item = models.FloatField()
    class Meta:
        db_table = 'api_transaction'
    def __str__(self):
        return f"Transaction {self.transaction_id} at {self.business_facility}"
class dto(models.Model):
        transaction_date_start = models.DateField()
        transaction_date_end = models.DateField()
        business_facility = models.JSONField()  

 

       
