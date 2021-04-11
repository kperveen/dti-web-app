from django.db import models


# Create your models here.
class Therapeutic_areas(models.Model):
    area_name = models.CharField(max_length=50)

    def __str__(self):
        return self.area_name


class Indications(models.Model):
    indication_name = models.CharField(max_length=50, default=None)
    therapeutic_area = models.ForeignKey(Therapeutic_areas, on_delete=models.CASCADE)

    def __str__(self):
        return self.indication_name





















# class Target(models.Model):
#     target_text = models.CharField(max_length=10)
#     pub_date = models.DateTimeField('date Published')
#
#
# class Therapeutic(models.Model):
#     therapeutic_text = models.CharField(max_length=30)
#     pub_date = models.DateTimeField('date Published')
#
#
# class Indication(models.Model):
#     indication_text = models.CharField(max_length=25)
#     pub_date = models.DateTimeField('date Published')
#
#
# class Model(models.Model):
#     model_text = models.CharField(max_length=20)
#     pub_date = models.DateTimeField('date Published')
#
#
# class Compound(models.Model):
#     compound_text = models.CharField(max_length=100)
#     pub_date = models.DateTimeField('date Published')
