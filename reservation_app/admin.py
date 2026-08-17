from django.contrib import admin
from .models import Customer, TableCategory, Table, ReservationStatus, Reservation, Payment, AuditLog
from .forms import ReservationForm, PaymentForm, TableForm

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email', 'phone')

@admin.register(TableCategory)
class TableCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    form = TableForm
    list_display = ('table_number', 'table_category', 'capacity', 'location', 'is_active')
    list_filter = ('table_category', 'is_active')
    search_fields = ('table_number', 'location')

@admin.register(ReservationStatus)
class ReservationStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    form = ReservationForm
    list_display = ('id', 'customer', 'table', 'reservation_date', 'start_time', 'end_time', 'guests', 'status')
    list_filter = ('status', 'reservation_date', 'table')
    search_fields = ('customer__first_name', 'customer__last_name', 'table__table_number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm
    list_display = ('id', 'reservation', 'amount', 'payment_method', 'payment_status', 'paid_at')
    list_filter = ('payment_status', 'payment_method')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'action', 'performed_by', 'action_time')
    list_filter = ('action', 'action_time')
    readonly_fields = ('reservation', 'action', 'performed_by', 'action_time', 'details')
