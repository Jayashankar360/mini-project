from django.contrib import admin
from .models import Category, Transaction, Budget, Goal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'description']
    list_filter = ['user']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'transaction_type', 'category', 'user', 'date']
    list_filter = ['transaction_type', 'category', 'user', 'date']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'user', 'start_date', 'end_date']
    list_filter = ['user', 'category']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_amount', 'current_amount', 'user', 'deadline']
    list_filter = ['user', 'deadline']