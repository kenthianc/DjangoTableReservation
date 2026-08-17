import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Customer, TableCategory, Table, ReservationStatus, Reservation, Payment, AuditLog
from .forms import (
    CustomerForm, TableCategoryForm, TableForm, 
    ReservationStatusForm, ReservationForm, PaymentForm
)

def wants_json(request):
    return (
        request.headers.get('Accept') == 'application/json' or
        request.GET.get('format') == 'json' or
        request.content_type == 'application/json'
    )

def get_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body)
        except Exception:
            return {}
    return request.POST.dict() or request.GET.dict()

@method_decorator(csrf_exempt, name='dispatch')
class CustomerListView(View):
    def get(self, request):
        customers = Customer.objects.all()
        if wants_json(request):
            data = [{
                'id': c.id, 'first_name': c.first_name, 'last_name': c.last_name, 
                'email': c.email, 'phone': c.phone, 
                'created_at': c.created_at.isoformat(), 'updated_at': c.updated_at.isoformat()
            } for c in customers]
            return JsonResponse(data, safe=False)
            
        # HTML rendering
        items = []
        for c in customers:
            items.append({
                'id': c.id,
                'name': f"{c.first_name} {c.last_name}",
                'email': c.email,
                'phone': c.phone,
                'detail_url': reverse('reservation_app:customer_detail', args=[c.id]),
                'edit_url': reverse('reservation_app:customer_update', args=[c.id]),
                'delete_url': reverse('reservation_app:customer_delete', args=[c.id])
            })
        context = {
            'title': 'Customers',
            'headers': ['ID', 'Name', 'Email', 'Phone'],
            'items': items,
            'add_url': reverse('reservation_app:customer_create')
        }
        return render(request, 'reservation_app/list.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class CustomerCreateView(View):
    def get(self, request):
        if wants_json(request):
            return JsonResponse({'message': 'Submit first_name, last_name, email, phone via POST.'})
        form = CustomerForm()
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Customer',
            'form': form,
            'list_url': reverse('reservation_app:customer_list')
        })

    def post(self, request):
        data = get_request_data(request)
        form = CustomerForm(data)
        if form.is_valid():
            customer = form.save()
            if wants_json(request):
                return JsonResponse({
                    'status': 'success',
                    'message': 'Customer created successfully',
                    'customer': {'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name}
                }, status=21)
            return redirect('reservation_app:customer_list')
            
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Customer',
            'form': form,
            'list_url': reverse('reservation_app:customer_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class CustomerDetailView(View):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        if wants_json(request):
            return JsonResponse({
                'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name,
                'email': customer.email, 'phone': customer.phone,
                'created_at': customer.created_at.isoformat(), 'updated_at': customer.updated_at.isoformat()
            })
            
        fields = {
            'ID': customer.id,
            'First Name': customer.first_name,
            'Last Name': customer.last_name,
            'Email': customer.email,
            'Phone': customer.phone,
            'Created At': customer.created_at,
            'Updated At': customer.updated_at
        }
        return render(request, 'reservation_app/detail.html', {
            'title': f"Customer: {customer.first_name} {customer.last_name}",
            'fields': fields,
            'edit_url': reverse('reservation_app:customer_update', args=[customer.id]),
            'delete_url': reverse('reservation_app:customer_delete', args=[customer.id]),
            'list_url': reverse('reservation_app:customer_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class CustomerUpdateView(View):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name})
        form = CustomerForm(instance=customer)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Customer: {customer.first_name}',
            'form': form,
            'list_url': reverse('reservation_app:customer_list')
        })

    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        data = get_request_data(request)
        form = CustomerForm(data, instance=customer)
        if form.is_valid():
            customer = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success', 'message': 'Customer updated successfully'})
            return redirect('reservation_app:customer_list')
            
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Customer: {customer.first_name}',
            'form': form,
            'list_url': reverse('reservation_app:customer_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class CustomerDeleteView(View):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        if wants_json(request):
            return JsonResponse({'message': 'Confirm delete customer.'})
        return render(request, 'reservation_app/confirm_delete.html', {
            'object_name': f"{customer.first_name} {customer.last_name}",
            'list_url': reverse('reservation_app:customer_list')
        })

    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        if wants_json(request):
            return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})
        return redirect('reservation_app:customer_list')


# --- TABLE CATEGORY VIEWS ---

@method_decorator(csrf_exempt, name='dispatch')
class TableCategoryListView(View):
    def get(self, request):
        categories = TableCategory.objects.all()
        if wants_json(request):
            data = [{'id': tc.id, 'name': tc.name, 'description': tc.description} for tc in categories]
            return JsonResponse(data, safe=False)
            
        items = [{
            'id': tc.id, 'name': tc.name, 'description': tc.description,
            'detail_url': reverse('reservation_app:table_category_detail', args=[tc.id]),
            'edit_url': reverse('reservation_app:table_category_update', args=[tc.id]),
            'delete_url': reverse('reservation_app:table_category_delete', args=[tc.id])
        } for tc in categories]
        return render(request, 'reservation_app/list.html', {
            'title': 'Table Categories',
            'headers': ['ID', 'Name', 'Description'],
            'items': items,
            'add_url': reverse('reservation_app:table_category_create')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableCategoryCreateView(View):
    def get(self, request):
        if wants_json(request):
            return JsonResponse({'message': 'Submit name, description via POST.'})
        form = TableCategoryForm()
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Table Category',
            'form': form,
            'list_url': reverse('reservation_app:table_category_list')
        })

    def post(self, request):
        data = get_request_data(request)
        form = TableCategoryForm(data)
        if form.is_valid():
            category = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success', 'id': category.id}, status=21)
            return redirect('reservation_app:table_category_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Table Category', 'form': form, 'list_url': reverse('reservation_app:table_category_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableCategoryDetailView(View):
    def get(self, request, pk):
        category = get_object_or_404(TableCategory, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': category.id, 'name': category.name, 'description': category.description})
        return render(request, 'reservation_app/detail.html', {
            'title': f"Category: {category.name}",
            'fields': {'ID': category.id, 'Name': category.name, 'Description': category.description},
            'edit_url': reverse('reservation_app:table_category_update', args=[category.id]),
            'delete_url': reverse('reservation_app:table_category_delete', args=[category.id]),
            'list_url': reverse('reservation_app:table_category_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableCategoryUpdateView(View):
    def get(self, request, pk):
        category = get_object_or_404(TableCategory, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': category.id, 'name': category.name})
        form = TableCategoryForm(instance=category)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Category: {category.name}', 'form': form, 'list_url': reverse('reservation_app:table_category_list')
        })

    def post(self, request, pk):
        category = get_object_or_404(TableCategory, pk=pk)
        data = get_request_data(request)
        form = TableCategoryForm(data, instance=category)
        if form.is_valid():
            category = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success'})
            return redirect('reservation_app:table_category_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Category: {category.name}', 'form': form, 'list_url': reverse('reservation_app:table_category_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableCategoryDeleteView(View):
    def get(self, request, pk):
        category = get_object_or_404(TableCategory, pk=pk)
        if wants_json(request):
            return JsonResponse({'message': 'Confirm delete.'})
        return render(request, 'reservation_app/confirm_delete.html', {
            'object_name': category.name, 'list_url': reverse('reservation_app:table_category_list')
        })

    def post(self, request, pk):
        category = get_object_or_404(TableCategory, pk=pk)
        category.delete()
        if wants_json(request):
            return JsonResponse({'status': 'success'})
        return redirect('reservation_app:table_category_list')


# --- TABLE VIEWS ---

@method_decorator(csrf_exempt, name='dispatch')
class TableListView(View):
    def get(self, request):
        tables = Table.objects.all()
        if wants_json(request):
            data = [{'id': t.id, 'table_number': t.table_number, 'capacity': t.capacity, 'location': t.location} for t in tables]
            return JsonResponse(data, safe=False)
            
        items = [{
            'id': t.id, 'table_number': t.table_number, 'category': t.table_category.name,
            'capacity': t.capacity, 'location': t.location,
            'detail_url': reverse('reservation_app:table_detail', args=[t.id]),
            'edit_url': reverse('reservation_app:table_update', args=[t.id]),
            'delete_url': reverse('reservation_app:table_delete', args=[t.id])
        } for t in tables]
        return render(request, 'reservation_app/list.html', {
            'title': 'Tables',
            'headers': ['ID', 'Table Number', 'Category', 'Capacity', 'Location'],
            'items': items,
            'add_url': reverse('reservation_app:table_create')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableCreateView(View):
    def get(self, request):
        if wants_json(request):
            return JsonResponse({'message': 'Submit table data.'})
        form = TableForm()
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Table', 'form': form, 'list_url': reverse('reservation_app:table_list')
        })

    def post(self, request):
        data = get_request_data(request)
        form = TableForm(data)
        if form.is_valid():
            table = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success', 'id': table.id}, status=21)
            return redirect('reservation_app:table_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Table', 'form': form, 'list_url': reverse('reservation_app:table_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableDetailView(View):
    def get(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': table.id, 'table_number': table.table_number})
        return render(request, 'reservation_app/detail.html', {
            'title': f"Table: {table.table_number}",
            'fields': {'ID': table.id, 'Table Number': table.table_number, 'Category': table.table_category.name, 'Capacity': table.capacity, 'Location': table.location, 'Active': table.is_active},
            'edit_url': reverse('reservation_app:table_update', args=[table.id]),
            'delete_url': reverse('reservation_app:table_delete', args=[table.id]),
            'list_url': reverse('reservation_app:table_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableUpdateView(View):
    def get(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': table.id})
        form = TableForm(instance=table)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Table: {table.table_number}', 'form': form, 'list_url': reverse('reservation_app:table_list')
        })

    def post(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        data = get_request_data(request)
        form = TableForm(data, instance=table)
        if form.is_valid():
            table = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success'})
            return redirect('reservation_app:table_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Table: {table.table_number}', 'form': form, 'list_url': reverse('reservation_app:table_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class TableDeleteView(View):
    def get(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        if wants_json(request):
            return JsonResponse({'message': 'Confirm delete.'})
        return render(request, 'reservation_app/confirm_delete.html', {
            'object_name': table.table_number, 'list_url': reverse('reservation_app:table_list')
        })

    def post(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        table.delete()
        if wants_json(request):
            return JsonResponse({'status': 'success'})
        return redirect('reservation_app:table_list')


# --- RESERVATION STATUS VIEWS ---

@method_decorator(csrf_exempt, name='dispatch')
class ReservationStatusListView(View):
    def get(self, request):
        statuses = ReservationStatus.objects.all()
        if wants_json(request):
            data = [{'id': s.id, 'name': s.name} for s in statuses]
            return JsonResponse(data, safe=False)
            
        items = [{
            'id': s.id, 'name': s.name, 'description': s.description, 'active': s.is_active,
            'edit_url': reverse('reservation_app:reservation_status_update', args=[s.id]),
            'delete_url': reverse('reservation_app:reservation_status_delete', args=[s.id])
        } for s in statuses]
        return render(request, 'reservation_app/list.html', {
            'title': 'Reservation Statuses',
            'headers': ['ID', 'Name', 'Description', 'Active'],
            'items': items,
            'add_url': reverse('reservation_app:reservation_status_create')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationStatusCreateView(View):
    def get(self, request):
        if wants_json(request):
            return JsonResponse({'message': 'Submit status.'})
        form = ReservationStatusForm()
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Reservation Status', 'form': form, 'list_url': reverse('reservation_app:reservation_status_list')
        })

    def post(self, request):
        data = get_request_data(request)
        form = ReservationStatusForm(data)
        if form.is_valid():
            status = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success', 'id': status.id}, status=21)
            return redirect('reservation_app:reservation_status_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Reservation Status', 'form': form, 'list_url': reverse('reservation_app:reservation_status_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationStatusUpdateView(View):
    def get(self, request, pk):
        status = get_object_or_404(ReservationStatus, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': status.id})
        form = ReservationStatusForm(instance=status)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Status: {status.name}', 'form': form, 'list_url': reverse('reservation_app:reservation_status_list')
        })

    def post(self, request, pk):
        status = get_object_or_404(ReservationStatus, pk=pk)
        data = get_request_data(request)
        form = ReservationStatusForm(data, instance=status)
        if form.is_valid():
            status = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success'})
            return redirect('reservation_app:reservation_status_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Status: {status.name}', 'form': form, 'list_url': reverse('reservation_app:reservation_status_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationStatusDeleteView(View):
    def get(self, request, pk):
        status = get_object_or_404(ReservationStatus, pk=pk)
        if wants_json(request):
            return JsonResponse({'message': 'Confirm delete.'})
        return render(request, 'reservation_app/confirm_delete.html', {
            'object_name': status.name, 'list_url': reverse('reservation_app:reservation_status_list')
        })

    def post(self, request, pk):
        status = get_object_or_404(ReservationStatus, pk=pk)
        status.delete()
        if wants_json(request):
            return JsonResponse({'status': 'success'})
        return redirect('reservation_app:reservation_status_list')


# --- RESERVATION VIEWS ---

@method_decorator(csrf_exempt, name='dispatch')
class ReservationListView(View):
    def get(self, request):
        reservations = Reservation.objects.all()
        
        customer_id = request.GET.get('customer')
        if customer_id:
            reservations = reservations.filter(customer_id=customer_id)
            
        reservation_date = request.GET.get('reservation_date')
        if reservation_date:
            reservations = reservations.filter(reservation_date=reservation_date)

        if wants_json(request):
            data = [{
                'id': r.id, 'customer_id': r.customer.id, 'table_id': r.table.id,
                'reservation_date': r.reservation_date.isoformat(),
                'start_time': r.start_time.isoformat(), 'end_time': r.end_time.isoformat(),
                'guests': r.guests, 'status_id': r.status.id
            } for r in reservations]
            return JsonResponse(data, safe=False)
            
        items = [{
            'id': r.id, 'customer': f"{r.customer.first_name} {r.customer.last_name}",
            'table': r.table.table_number, 'date': r.reservation_date,
            'time': f"{r.start_time} - {r.end_time}", 'guests': r.guests, 'status': r.status.name,
            'detail_url': reverse('reservation_app:reservation_detail', args=[r.id]),
            'edit_url': reverse('reservation_app:reservation_update', args=[r.id]),
            'cancel_url': reverse('reservation_app:reservation_cancel', args=[r.id]),
            'delete_url': reverse('reservation_app:reservation_delete', args=[r.id])
        } for r in reservations]
        return render(request, 'reservation_app/list.html', {
            'title': 'Reservations',
            'headers': ['ID', 'Customer', 'Table', 'Date', 'Time', 'Guests', 'Status'],
            'items': items,
            'add_url': reverse('reservation_app:reservation_create')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationCreateView(View):
    def get(self, request):
        if wants_json(request):
            return JsonResponse({'message': 'Submit reservation data.'})
        form = ReservationForm()
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Reservation', 'form': form, 'list_url': reverse('reservation_app:reservation_list')
        })

    def post(self, request):
        data = get_request_data(request)
        form = ReservationForm(data)
        if form.is_valid():
            reservation = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success', 'id': reservation.id}, status=21)
            return redirect('reservation_app:reservation_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Reservation', 'form': form, 'list_url': reverse('reservation_app:reservation_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationDetailView(View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': reservation.id, 'customer': reservation.customer.id, 'table': reservation.table.id})
            
        fields = {
            'ID': reservation.id,
            'Customer': f"{reservation.customer.first_name} {reservation.customer.last_name}",
            'Table': reservation.table.table_number,
            'Date': reservation.reservation_date,
            'Time': f"{reservation.start_time} - {reservation.end_time}",
            'Guests': reservation.guests,
            'Status': reservation.status.name,
            'Notes': reservation.notes,
            'Created At': reservation.created_at,
            'Updated At': reservation.updated_at
        }
        return render(request, 'reservation_app/detail.html', {
            'title': f"Reservation #{reservation.id}",
            'fields': fields,
            'edit_url': reverse('reservation_app:reservation_update', args=[reservation.id]),
            'cancel_url': reverse('reservation_app:reservation_cancel', args=[reservation.id]),
            'delete_url': reverse('reservation_app:reservation_delete', args=[reservation.id]),
            'list_url': reverse('reservation_app:reservation_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationUpdateView(View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': reservation.id})
        form = ReservationForm(instance=reservation)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Reservation #{reservation.id}', 'form': form, 'list_url': reverse('reservation_app:reservation_list')
        })

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        data = get_request_data(request)
        form = ReservationForm(data, instance=reservation)
        if form.is_valid():
            reservation = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success'})
            return redirect('reservation_app:reservation_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Reservation #{reservation.id}', 'form': form, 'list_url': reverse('reservation_app:reservation_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReservationCancelView(View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if wants_json(request):
            return JsonResponse({'message': 'Confirm cancel.'})
        return render(request, 'reservation_app/confirm_delete.html', {
            'object_name': f"Reservation #{reservation.id} (Cancel)", 'list_url': reverse('reservation_app:reservation_list')
        })

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        status_cancelled = ReservationStatus.objects.filter(name__iexact='CANCELLED').first()
        if not status_cancelled:
            status_cancelled, _ = ReservationStatus.objects.get_or_create(
                name='CANCELLED', defaults={'description': 'Cancelled', 'is_active': True}
            )
        reservation.status = status_cancelled
        reservation.save()
        
        if wants_json(request):
            return JsonResponse({'status': 'success'})
        return redirect('reservation_app:reservation_list')

@method_decorator(csrf_exempt, name='dispatch')
class ReservationDeleteView(View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if wants_json(request):
            return JsonResponse({'message': 'Confirm delete.'})
        return render(request, 'reservation_app/confirm_delete.html', {
            'object_name': f"Reservation #{reservation.id}", 'list_url': reverse('reservation_app:reservation_list')
        })

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.delete()
        if wants_json(request):
            return JsonResponse({'status': 'success'})
        return redirect('reservation_app:reservation_list')


# --- PAYMENT VIEWS ---

@method_decorator(csrf_exempt, name='dispatch')
class PaymentListView(View):
    def get(self, request):
        payments = Payment.objects.all()
        reservation_id = request.GET.get('reservation')
        if reservation_id:
            payments = payments.filter(reservation_id=reservation_id)

        if wants_json(request):
            data = [{
                'id': p.id, 'reservation_id': p.reservation.id, 'amount': str(p.amount),
                'payment_method': p.payment_method, 'payment_status': p.payment_status,
                'paid_at': p.paid_at.isoformat() if p.paid_at else None
            } for p in payments]
            return JsonResponse(data, safe=False)
            
        items = [{
            'id': p.id, 'reservation': f"Reservation #{p.reservation.id}",
            'amount': f"${p.amount}", 'method': p.payment_method, 'status': p.payment_status,
            'paid_at': p.paid_at or 'N/A',
            'detail_url': reverse('reservation_app:payment_detail', args=[p.id]),
            'edit_url': reverse('reservation_app:payment_update', args=[p.id])
        } for p in payments]
        return render(request, 'reservation_app/list.html', {
            'title': 'Payments',
            'headers': ['ID', 'Reservation', 'Amount', 'Method', 'Status', 'Paid At'],
            'items': items,
            'add_url': reverse('reservation_app:payment_create')
        })

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCreateView(View):
    def get(self, request):
        if wants_json(request):
            return JsonResponse({'message': 'Submit payment.'})
        form = PaymentForm()
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Payment', 'form': form, 'list_url': reverse('reservation_app:payment_list')
        })

    def post(self, request):
        data = get_request_data(request)
        form = PaymentForm(data)
        if form.is_valid():
            payment = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success', 'id': payment.id}, status=21)
            return redirect('reservation_app:payment_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': 'Create Payment', 'form': form, 'list_url': reverse('reservation_app:payment_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class PaymentDetailView(View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': payment.id, 'amount': str(payment.amount)})
        return render(request, 'reservation_app/detail.html', {
            'title': f"Payment #{payment.id}",
            'fields': {
                'ID': payment.id, 'Reservation': f"Reservation #{payment.reservation.id}",
                'Amount': f"${payment.amount}", 'Method': payment.payment_method,
                'Status': payment.payment_status, 'Paid At': payment.paid_at or 'N/A',
                'Ref': payment.transaction_ref or 'N/A'
            },
            'edit_url': reverse('reservation_app:payment_update', args=[payment.id]),
            'list_url': reverse('reservation_app:payment_list')
        })

@method_decorator(csrf_exempt, name='dispatch')
class PaymentUpdateView(View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': payment.id})
        form = PaymentForm(instance=payment)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Payment #{payment.id}', 'form': form, 'list_url': reverse('reservation_app:payment_list')
        })

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        data = get_request_data(request)
        form = PaymentForm(data, instance=payment)
        if form.is_valid():
            payment = form.save()
            if wants_json(request):
                return JsonResponse({'status': 'success'})
            return redirect('reservation_app:payment_list')
        if wants_json(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'reservation_app/form.html', {
            'title': f'Update Payment #{payment.id}', 'form': form, 'list_url': reverse('reservation_app:payment_list')
        })


# --- AUDIT LOG VIEWS ---

@method_decorator(csrf_exempt, name='dispatch')
class AuditLogListView(View):
    def get(self, request):
        logs = AuditLog.objects.all()
        reservation_id = request.GET.get('reservation')
        if reservation_id:
            logs = logs.filter(reservation_id=reservation_id)

        if wants_json(request):
            data = [{'id': l.id, 'action': l.action, 'performed_by': l.performed_by} for l in logs]
            return JsonResponse(data, safe=False)
            
        items = [{
            'id': l.id, 'reservation': f"Reservation #{l.reservation.id}",
            'action': l.action, 'user': l.performed_by, 'time': l.action_time,
            'detail_url': reverse('reservation_app:audit_log_detail', args=[l.id])
        } for l in logs]
        return render(request, 'reservation_app/list.html', {
            'title': 'Audit Logs',
            'headers': ['ID', 'Reservation', 'Action', 'Performed By', 'Time'],
            'items': items
        })

@method_decorator(csrf_exempt, name='dispatch')
class AuditLogDetailView(View):
    def get(self, request, pk):
        log = get_object_or_404(AuditLog, pk=pk)
        if wants_json(request):
            return JsonResponse({'id': log.id, 'action': log.action})
        return render(request, 'reservation_app/detail.html', {
            'title': f"Audit Log #{log.id}",
            'fields': {
                'ID': log.id, 'Reservation': f"Reservation #{log.reservation.id}",
                'Action': log.action, 'Performed By': log.performed_by,
                'Time': log.action_time, 'Details': log.details
            },
            'list_url': reverse('reservation_app:audit_log_list')
        })
