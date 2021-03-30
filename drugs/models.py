from django.db import models


# Create your models here.


class Therapeutic(models.Model):
    therapeutic_text = models.CharField(max_length=30)
    pub_date = models.DateTimeField('date Published')
    def __str__(self):
        return self.therapeutic_text


class Indication(models.Model):
    therapeutic = models.ForeignKey(Therapeutic, on_delete=models.CASCADE, null=False, default='Oncology')
    indication_text = models.CharField(max_length=25)
    pub_date = models.DateTimeField('date Published')
    def __str__(self):
        return self.indication_text


class Target(models.Model):
    target_text = models.CharField(max_length=10)
    pub_date = models.DateTimeField('date Published')
    def __str__(self):
        return self.target_text


class Model(models.Model):
    model_text = models.CharField(max_length=20)
    pub_date = models.DateTimeField('date Published')
    def __str__(self):
        return self.model_text


class Compound(models.Model):
    compound_text = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date Published')
    def __str__(self):
        return self.compound_text
