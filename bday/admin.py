from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from .models import Bday

@admin.register(Bday)
class Bday_admin(ImportExportActionModelAdmin):
    pass
