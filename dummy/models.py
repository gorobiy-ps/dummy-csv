from django.contrib.postgres.fields import IntegerRangeField
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Separator(models.Model):
    value = models.CharField(max_length=1)
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class TextChar(models.Model):
    value = models.CharField(max_length=1)
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Schema(models.Model):
    name = models.CharField(max_length=60)
    modified_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    separator = models.ForeignKey(Separator, on_delete=models.CASCADE)
    text_char = models.ForeignKey(TextChar, on_delete=models.CASCADE)

    def __str__(self):
        return 'Name: ' + self.name + ' - id: ' + str(self.id)


class FieldType(models.Model):
    title = models.CharField(max_length=30)
    extra = models.CharField(max_length=20, null=True)


class SchemaField(models.Model):
    name = models.CharField(max_length=30)
    order = models.IntegerField(null=True)
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    field_type = models.ForeignKey(FieldType, on_delete=models.CASCADE)
    range = IntegerRangeField(null=True)
    mask = models.CharField(max_length=30, null=True)


class DataSet(models.Model):
    status = models.CharField(max_length=30)
    task_id = models.CharField(max_length=60, null=True, default=None)
    created_date = models.DateTimeField(auto_now=True)
    schema = models.ForeignKey(Schema, on_delete=models.SET_DEFAULT, null=True, default=None)
    link_to_file = models.FilePathField(null=True)


class Sample(models.Model):
    text = models.TextField(blank=False)
    type = models.CharField(max_length=20)
