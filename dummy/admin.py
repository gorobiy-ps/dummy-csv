from django.contrib import admin
from .models import User, Separator, TextChar, DataSet
import hashlib


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    def save_model(self, request, obj, form, change):
        hash_object = hashlib.sha1(obj.password.encode())
        obj.password = hash_object.hexdigest()
        obj.save()


admin.site.register(Separator)
admin.site.register(TextChar)

@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    list_display = ('status', 'task_id', 'link_to_file')
