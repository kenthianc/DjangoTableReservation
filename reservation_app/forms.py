from django import forms
from django.core.exceptions import ValidationError
from .models import Customer, TableCategory, Table, ReservationStatus, Reservation, Payment

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
        }


class TableCategoryForm(forms.ModelForm):
    class Meta:
        model = TableCategory
        fields = ['name', 'description']
        labels = {
            'name': 'Category Name',
            'description': 'Description',
        }


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_category', 'table_number', 'capacity', 'location', 'is_active']
        labels = {
            'table_category': 'Category',
            'table_number': 'Table Number',
            'capacity': 'Capacity (Seats)',
            'location': 'Location Description',
            'is_active': 'Is Active',
        }
        widgets = {
            'capacity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }


class ReservationStatusForm(forms.ModelForm):
    class Meta:
        model = ReservationStatus
        fields = ['name', 'description', 'is_active']
        labels = {
            'name': 'Status Name',
            'description': 'Description',
            'is_active': 'Is Active',
        }


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['customer', 'table', 'reservation_date', 'start_time', 'end_time', 'guests', 'status', 'notes']
        labels = {
            'customer': 'Customer',
            'table': 'Table',
            'reservation_date': 'Reservation Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'guests': 'Number of Guests',
            'status': 'Status',
            'notes': 'Special Notes',
        }
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'guests': forms.NumberInput(attrs={'min': 1}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_guests(self):
        guests = self.cleaned_data.get('guests')
        if guests is not None and guests <= 0:
            raise ValidationError("The number of guests must be positive.")
        return guests

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        table = cleaned_data.get('table')
        guests = cleaned_data.get('guests')

        # Validate that the reservation end time is later than the start time
        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError({
                    'end_time': "The reservation end time must be later than the start time."
                })

        # Validate that a selected table can accommodate the specified number of guests
        if table and guests:
            if guests > table.capacity:
                raise ValidationError({
                    'guests': f"The selected table (Capacity: {table.capacity}) cannot accommodate {guests} guests."
                })

        # Validate that table is not double-booked (overlapping time intervals on the same date)
        reservation_date = cleaned_data.get('reservation_date')
        if table and reservation_date and start_time and end_time:
            overlapping = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date
            ).exclude(pk=self.instance.pk if self.instance and self.instance.pk else None)
            
            # Check overlap: start_time < existing.end_time and end_time > existing.start_time
            for res in overlapping:
                if start_time < res.end_time and end_time > res.start_time:
                    raise ValidationError({
                        'table': f"The selected table is already reserved during this time ({res.start_time} - {res.end_time})."
                    })

        return cleaned_data


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['reservation', 'amount', 'payment_method', 'payment_status', 'paid_at', 'transaction_ref']
        labels = {
            'reservation': 'Reservation',
            'amount': 'Amount Paid',
            'payment_method': 'Payment Method',
            'payment_status': 'Payment Status',
            'paid_at': 'Payment Date/Time',
            'transaction_ref': 'Transaction Reference',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.00'}),
            'paid_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
