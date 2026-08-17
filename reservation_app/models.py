from django.db import models

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TableCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Table Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Table(models.Model):
    table_category = models.ForeignKey(TableCategory, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table_number']

    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats)"


class ReservationStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Reservation Statuses"
        ordering = ['name']

    def __str__(self):
        return self.name


class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reservations')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guests = models.PositiveIntegerField()
    status = models.ForeignKey(ReservationStatus, on_delete=models.PROTECT, related_name='reservations')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reservation_date', '-start_time']

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        old_instance = None
        if not is_create:
            try:
                old_instance = Reservation.objects.get(pk=self.pk)
            except Reservation.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Log the action in AuditLog
        action = 'CREATE' if is_create else 'UPDATE'
        details = []
        if is_create:
            details.append(f"Reservation created for customer '{self.customer}' on Table '{self.table.table_number}' with {self.guests} guests.")
        else:
            if old_instance:
                if old_instance.customer != self.customer:
                    details.append(f"Customer changed from '{old_instance.customer}' to '{self.customer}'.")
                if old_instance.table != self.table:
                    details.append(f"Table changed from '{old_instance.table.table_number}' to '{self.table.table_number}'.")
                if old_instance.reservation_date != self.reservation_date:
                    details.append(f"Date changed from '{old_instance.reservation_date}' to '{self.reservation_date}'.")
                if old_instance.start_time != self.start_time or old_instance.end_time != self.end_time:
                    details.append(f"Time changed from {old_instance.start_time}-{old_instance.end_time} to {self.start_time}-{self.end_time}.")
                if old_instance.guests != self.guests:
                    details.append(f"Guests changed from {old_instance.guests} to {self.guests}.")
                if old_instance.status != self.status:
                    details.append(f"Status changed from '{old_instance.status.name}' to '{self.status.name}'.")
                    if self.status.name.upper() == 'CANCELLED':
                        action = 'CANCEL'
                if old_instance.notes != self.notes:
                    details.append(f"Notes updated.")
            if not details:
                details.append("No changes detected during save.")
        
        AuditLog.objects.create(
            reservation=self,
            action=action,
            performed_by='System/User',
            details="\n".join(details)
        )

    def __str__(self):
        return f"Reservation {self.id} - {self.customer} (Table {self.table.table_number})"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    paid_at = models.DateTimeField(null=True, blank=True)
    transaction_ref = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.payment_status == 'PAID' and not self.paid_at:
            from django.utils import timezone
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id} ({self.amount}) - {self.payment_status}"


class AuditLog(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100)
    performed_by = models.CharField(max_length=100)  # User/Staff
    action_time = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-action_time']

    def __str__(self):
        return f"AuditLog {self.id} - {self.action} on Reservation {self.reservation.id}"
