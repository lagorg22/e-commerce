from django.contrib import admin
from .models import UserProfile, Transaction

# Register UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'is_admin_user')
    search_fields = ('user__username', 'user__email')
    
    def is_admin_user(self, obj):
        return obj.user.is_staff
    is_admin_user.boolean = True
    is_admin_user.short_description = 'Admin'

# Register Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'timestamp', 'description')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'description')
    date_hierarchy = 'timestamp'
