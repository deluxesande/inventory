from django.shortcuts import render, redirect
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
from helpers.decorators import allowed_users

# Create your views here.
@login_required
def get_showing_reports(request, report):

    if request.GET and request.GET.get("filter"):
        if request.GET.get("filter") == "edit":
            return report.filter(for_edit=True)
        if request.GET.get("filter") == "noedit":
            return report.filter(for_edit=False)
    return report


@login_required
def home(request):
    if request.user.user_type == "manager":
        return HttpResponseRedirect(reverse("manager"))
    elif request.user.user_type == "accountant":
        return HttpResponseRedirect(reverse("accountant"))
    else:
        return HttpResponseRedirect(reverse("admin"))
    
    return render(request, "dashboard/dashboard.html")


@allowed_users(allowed_roles=["admin"])
@login_required
def admin(request):
    report = Reports.objects.all()
    # blog = Blog.objects.filter(owner = request.user)

    # filter querysets
    active_count = report.filter(for_edit=True).count()
    inactive_count = report.filter(for_edit=False).count()
    total_count = report.count()
    # context = {'report':[]} #--simulate no content
    context = {
        "report": get_showing_reports(request, report),
        "edit_count": active_count,
        "noedit_count": inactive_count,
        "total_count": total_count,
    }
    return render(request, "dashboard/admin.html", context)


@allowed_users(allowed_roles=["accountant"])
@login_required
def accountant(request):
    # Get all user feedback and latest feedback
    feedbacks = Feedback.objects.filter(directed_to=request.user, resolved=False)
    feedback = feedbacks.filter(directed_to=request.user).last()

    # Get the total payments and receipts
    total_payments = Reports.objects.aggregate(Sum("payments"))["payments__sum"] or 0
    total_receipts = Reports.objects.aggregate(Sum("receipts"))["receipts__sum"] or 0

    context = {"feedback" : feedback,"feedbacks" : feedbacks, "payments": total_payments, "receipts": total_receipts}

    # If the request is not POST, render the form
    return render(request, "dashboard/accountant.html", context)

@allowed_users(allowed_roles=["accountant"])
@login_required
def get_accountant_feedback(request, id):
    feedback = get_object_or_404(Feedback, id=id)
    report = feedback.report
    form = ReportsForm(instance=report)

    if request.method == "POST":
        form = ReportsForm(request.POST, instance=report)
        if form.is_valid():
            form.save()

            # Call the resolve_feedback view
            resolve_feedback(request, feedback.id)

            messages.add_message(
                request, messages.SUCCESS, "Report Updated Successfully"
            )
            return HttpResponseRedirect(reverse("home"))
        else:
            messages.error(form.errors)

    return render(
        request,
        "dashboard/accountant_feedback.html",
        {"feedback": feedback, "report": report, "form": form},
    )

@allowed_users(allowed_roles=["accountant"])
@login_required
def resolve_feedback(request, id):
    # Retrieve the Feedback instance
    feedback = get_object_or_404(Feedback, id=id)

    # Check if the user is a accountant
    if request.user.user_type == "accountant":
        # Check if feedback belongs to logged in user
        if feedback.directed_to == request.user:
            # Approve the Feedback
            feedback.resolved = True
            feedback.save()

        return HttpResponseRedirect(reverse("accountant"))

    # If the user is not a accountant, show an error message
    else:
        return HttpResponse("You are not authorized to approve reports.")

@allowed_users(allowed_roles=["manager"])
@login_required
def manager(request):
    # Retrieve all PendingReports instances where is_approved is False
    pending_reports = Reports.objects.filter(is_approved=False).order_by("created_at")

    # Pass the pending_reports to the template
    return render(
        request, "dashboard/manager.html", {"pending_reports": pending_reports}
    )

@allowed_users(allowed_roles=["manager", "admin"])
@login_required
def approve_report(request, id):
    # Retrieve the PendingReports instance
    report = get_object_or_404(Reports, id=id)

    # Approve the report
    report.is_approved = True
    report.save()

    return HttpResponseRedirect(reverse("manager"))

@allowed_users(allowed_roles=["manager", "admin"])
@login_required
def collect_feedback(request, id):
    report = get_object_or_404(Reports, id=id)
    if request.method == "POST":
        feedback_content = request.POST.get("feedback")
        reporter = request.user  # Assuming you have user in request
        directed_to = report.owner  # Assuming report has an owner field
        Feedback.objects.create(
            report=report,
            content=feedback_content,
            reporter=reporter,
            directed_to=directed_to,
        )
        messages.add_message(request, messages.SUCCESS, "Feedback sent Successfully")
        return HttpResponseRedirect(reverse("manager"))

    return render(request, "dashboard/collect_feedback.html", {"report": report})

@allowed_users(allowed_roles=["accountant", "admin"])
@login_required
def create_report(request):
    form = ReportsForm()
    context = {"form": form}

    if request.method == "POST":
        form = ReportsForm(request.POST)
        if form.is_valid():
            # Extract form data
            description = form.cleaned_data["description"]
            main_category = form.cleaned_data["category"]
            sub_category = form.cleaned_data.get(
                "subcategory"
            )  # Assuming you have a subcategory field in your form
            receipts = form.cleaned_data.get("receipts")
            payments = form.cleaned_data.get("payments")

            # Create a new report instance
            report = Reports()
            report.description = description
            report.main_category = main_category
            report.owner = User.objects.get(username=request.user.username)
            report.sub_category = sub_category
            report.receipts = receipts
            report.payments = payments
            report.save()

            messages.add_message(request, messages.SUCCESS, "Report Created Successfully")
            # Redirect to the same page after saving the record
            return HttpResponseRedirect(reverse("accountant"))
        
    return render(request, "dashboard/create-report.html", context)

@allowed_users(allowed_roles=["manager", "admin"])
@login_required
def accountant_list(request):
    report = Reports.objects.all()
    # blog = Blog.objects.filter(owner = request.user)

    # filter querysets
    active_count = report.filter(for_edit=True).count()
    inactive_count = report.filter(for_edit=False).count()
    total_count = report.count()
    # context = {'report':[]} #--simulate no content
    context = {
        "report": get_showing_reports(request, report),
        "edit_count": active_count,
        "noedit_count": inactive_count,
        "total_count": total_count,
    }

    return render(request, "dashboard/accountant_list.html", context)

@allowed_users(allowed_roles=["manager", "admin"])
@login_required
def report_edit(request, id):
    report = get_object_or_404(Reports, pk=id)
    form = ReportsForm(instance=report)
    context = {"report": report, "form": form}

    if request.method == "POST" and request.POST.get("_method") == "PUT":
        # Handle as PUT request
        form = ReportsForm(request.POST, instance=report)
        if form.is_valid():
            # Extract form data
            description = form.cleaned_data["description"]
            main_category = form.cleaned_data["category"]
            sub_category = form.cleaned_data.get("subcategory")
            receipts = form.cleaned_data.get("receipts")
            payments = form.cleaned_data.get("payments")

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

            messages.add_message(
                request, messages.SUCCESS, "Report Updated Successfully"
            )
            return HttpResponseRedirect(reverse("manager"))
        else:
            messages.error(request, form.errors)

        return HttpResponseRedirect(reverse("report-edit", kwargs={"id": report.pk}))

    return render(request, "dashboard/report-edit.html", context)

@allowed_users(allowed_roles=["manager", "admin"])
@login_required
def export_to_excel(request):
    filename = f"Reports_requested_by_{request.user.username}.xlsx"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f'attachment; filename={filename}'

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Report"

    # Add headers
    headers = ["Description", "Owner", "Receipts", "Payments", "Is_approved"]
    ws.append(headers)

    # Add data from the model
    reports = Reports.objects.all()
    for report in reports:
        ws.append(
            [
                report.description,
                report.owner.username,
                report.receipts,
                report.payments,
                report.is_approved,
            ]
        )

    # Save the workbook to the HttpResponse
    wb.save(response)
    return response

@allowed_users(allowed_roles=["manager", "admin"])
@login_required
def export_single_report_to_excel(request, id):
    report = Reports.objects.get(id=id)

    filename = f"Report_{id}_requested_by_{request.user.username}.xlsx"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f'attachment; filename={filename}'

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Report"

    # Add headers
    headers = ["Description", "Owner", "Receipts", "Payments", "Is_approved"]
    ws.append(headers)

    # Add data from the report
    ws.append(
        [
            report.description,
            report.owner.username,
            report.receipts,
            report.payments,
            report.is_approved,
        ]
    )

    # Save the workbook to the HttpResponse
    wb.save(response)
    return response



@login_required
@allowed_users(allowed_roles=['admin'])
def change_user_type(request, id):
    user = User.objects.get(id=id)

    # Prevent the admin from changing their own user type
    if request.user.user_type == "admin" and user == request.user:
        return redirect('all-users')

    if request.method == 'POST':
        # Get the new user type from the POST data
        new_user_type = request.POST.get('user_type')

        # Change the user's type
        user.user_type = new_user_type
        user.save()

        messages.success(request, "User type updated successfully.")
        return redirect('all-users')

    else:
        return render(request, 'dashboard/change_user_type.html', {'user': user})