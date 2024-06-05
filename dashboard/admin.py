from django.contrib import admin
from .models import Reports, MainCategory, Category

class ReportsAdmin(admin.ModelAdmin):
    list_display = ('date', 'owner', 'payments', 'receipts', 'for_edit', 'is_approved')
    list_filter = ('date', 'owner', 'for_edit', 'is_approved')
    search_fields = ('description',)

admin.site.register(Reports, ReportsAdmin)
admin.site.register(MainCategory)
admin.site.register(Category)