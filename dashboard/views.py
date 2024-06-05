from django.shortcuts import render
from django.http import HttpResponse
from .forms import ReportsForm
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from authentication.models import User
from openpyxl import Workbook
from django.db.models import Sum

# Create your views here.
def get_showing_reports(request, report):
    
    if request.GET and request.GET.get('filter'):
        if request.GET.get('filter')=='edit':
            return report.filter(for_edit=True)
        if request.GET.get('filter')=='noedit':
            return report.filter(for_edit=False)
    return report

def home(request):
    return render(request, 'dashboard/dashboard.html')

def admin(request):
    report = Reports.objects.all()
    #blog = Blog.objects.filter(owner = request.user)


    #filter querysets
    active_count = report.filter(for_edit = True).count()
    inactive_count = report.filter(for_edit = False).count()
    total_count = report.count()
    #context = {'report':[]} #--simulate no content
    context = {
        'report':get_showing_reports(request, report),
          'edit_count':active_count,
            'noedit_count':inactive_count,
            'total_count':total_count,
            }
    return render(request, 'dashboard/admin.html', context)



def accountant(request):
    # Fetch all feedback
    feedbacks = Feedback.objects.all()  # Get all feedbacks
    feedbacks = feedbacks.filter(directed_to=request.user)

    total_payments = Reports.objects.aggregate(Sum('payments'))['payments__sum'] or 0
    total_receipts = Reports.objects.aggregate(Sum('receipts'))['receipts__sum'] or 0

    context = {'payments': total_payments, 'receipts': total_receipts}

    if request.method == 'POST':
        form = ReportsForm(request.POST)
        if form.is_valid():
            # Extract form data
            description = form.cleaned_data['description']
            main_category = form.cleaned_data['category']
            sub_category = form.cleaned_data.get('subcategory')  # Assuming you have a subcategory field in your form
            receipts = form.cleaned_data.get('receipts')
            payments = form.cleaned_data.get('payments')
        
            # Create a new PendingReports instance
            pending_report = Reports()
            pending_report.description = description
            pending_report.main_category = main_category
            pending_report.owner = request.user
            pending_report.sub_category = sub_category
            pending_report.receipts = receipts
            pending_report.payments = payments
            pending_report.save()
    
        # Redirect to the same page after saving the record
        return HttpResponseRedirect(reverse('accountant'))

    # If the request is not POST, render the form
    return render(request, 'dashboard/accountant.html', context)

def get_accountant_feedbacks(request):
    feedbacks = Feedback.objects.all()
    feedbacks = feedbacks.filter(directed_to=request.user)
    context = {"feedbacks": feedbacks}

    return render(request, 'dashboard/accountant_feedbacks.html', context)

def get_accountant_feedback(request, id):
    feedback = get_object_or_404(Feedback, id=id)
    report = feedback.report
    form = ReportsForm(instance=report)

    if request.method == 'POST':
        form = ReportsForm(request.POST, instance=report)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.SUCCESS, "Report Updated Successfully" )
            return HttpResponseRedirect(reverse('view_feedback', args=[feedback.id]))
        else:
            messages.error(form.errors)

    return render(request, 'dashboard/accountant_feedback.html', {'feedback': feedback, "report": report, "form": form})

def manager(request):
    # Retrieve all PendingReports instances where is_approved is False
    pending_reports = Reports.objects.filter(is_approved=False)

    # Pass the pending_reports to the template
    return render(request, 'dashboard/manager.html', {'pending_reports': pending_reports})

def approve_report(request, id):
    # Retrieve the PendingReports instance
    report = get_object_or_404(Reports, id=id)

    # Check if the user is a manager
    if request.user.user_type == 'manager':
        # Approve the report
        report.is_approved = True
        report.save()

        return HttpResponseRedirect(reverse('manager'))

    # If the user is not a manager, show an error message
    else:
        return HttpResponse('You are not authorized to approve reports.')

def collect_feedback(request, id):
    report = get_object_or_404(Reports, id=id)
    if request.method == 'POST':
        feedback_content = request.POST.get('feedback')
        reporter = request.user  # Assuming you have user in request
        directed_to = report.owner  # Assuming report has an owner field
        Feedback.objects.create(
            report=report,
            content=feedback_content,
            reporter=reporter,
            directed_to=directed_to
        )
        messages.add_message(request, messages.SUCCESS, "Feedback sent Successfully" )
        return HttpResponseRedirect(reverse('manager'))
    
    return render(request, 'dashboard/collect_feedback.html', {'report': report})

@login_required
def create_report(request):
    form = ReportsForm()
    context = {'form':form}

    if request.method == 'POST':
        form = ReportsForm(request.POST)
        if form.is_valid():
            # Extract form data
            description = form.cleaned_data['description']
            main_category = form.cleaned_data['category']
            sub_category = form.cleaned_data.get('subcategory')  # Assuming you have a subcategory field in your form
            receipts = form.cleaned_data.get('receipts')
            payments = form.cleaned_data.get('payments')

            # Create a new report instance
            report = Reports()
            report.description = description
            report.main_category = main_category
            report.owner = User.objects.get(username=request.user.username)
            report.sub_category = sub_category
            report.receipts = receipts
            print("hello")
            print(report.main_category)
            report.payments = payments
            report.save()

        messages.add_message(request, messages.SUCCESS, "report Created Successfully" )

        # return HttpResponseRedirect(reverse("accountant", kwargs={'id': report.pk}))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'accountant'))
        # return HttpResponseRedirect(reverse('HTTP_REFERER', 'accountant'))


    return render(request, 'dashboard/create-report.html', context)


def accountant_list(request):
    report = Reports.objects.all()
    #blog = Blog.objects.filter(owner = request.user)


    #filter querysets
    active_count = report.filter(for_edit = True).count()
    inactive_count = report.filter(for_edit = False).count()
    total_count = report.count()
    #context = {'report':[]} #--simulate no content
    context = {
        'report':get_showing_reports(request, report),
          'edit_count':active_count,
            'noedit_count':inactive_count,
            'total_count':total_count,
            }

    return render(request, 'dashboard/accountant_list.html', context)

def report_edit(request, id):
    report = get_object_or_404(Reports, pk=id)
    form = ReportsForm(instance=report)
    context = {'report' : report, 'form' : form}

    if request.method == 'POST' and request.POST.get('_method') == 'PUT':
        # Handle as PUT request
        form = ReportsForm(request.POST, instance=report)
        if form.is_valid():
            # Extract form data
            description = form.cleaned_data['description']
            main_category = form.cleaned_data['category']
            sub_category = form.cleaned_data.get('subcategory')
            receipts = form.cleaned_data.get('receipts')
            payments = form.cleaned_data.get('payments')

            # Create a new report instance
            report = Reports.objects.get(pk=id)
            report.description = description
            report.main_category = main_category
            report.owner = User.objects.get(username=request.user.username)
            report.sub_category = sub_category
            report.receipts = receipts
            report.is_approved = True  # Add this line to approve the report

            report.payments = payments
            report.save()

            messages.add_message(request, messages.SUCCESS, "Report Updated Successfully" )
            return HttpResponseRedirect(reverse('manager'))
        else:
            messages.error(request, form.errors)


        return HttpResponseRedirect(reverse("report-edit", kwargs={'id': report.pk}))
    
    return render(request, 'dashboard/report-edit.html', context)

def export_to_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Report"

    # Add headers
    headers = ["Description", "Owner", "Receipts", "Payments"]
    ws.append(headers)

    # Add data from the model
    reports = Reports.objects.all()
    for report in reports:
        ws.append([report.description, report.owner.username ,report.receipts, report.payments])

    # Save the workbook to the HttpResponse
    wb.save(response)
    return response

