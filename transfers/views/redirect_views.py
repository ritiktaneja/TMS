# from django.contrib.auth.models import User
from django.shortcuts import redirect

from transfers.constants import UserType


def login_redirect_view(request):
    if request.user.is_anonymous:
        return redirect('/TMS/login/')
    else:
        if request.user.is_superuser:
            return redirect('/TMS-admin/')
        user_type = request.user.userprofile.user_type
        if user_type == UserType.STUDENT.value:
            return redirect('/TMS/student/dashboard/')
        elif user_type == UserType.SUPERVISOR.value:
            return redirect('/TMS/supervisor/home/')
        elif user_type == UserType.HOD.value:
            return redirect('/TMS/hod/home/')
        elif user_type == UserType.AD.value:
            return redirect('/TMS/assoc-dean/home/')

def application_data_redirect_view(request):
    if request.user.is_anonymous:
        return redirect('/TMS/login/')
    else:
        if request.user.is_superuser:
            return redirect('/TMS-admin/')
        user_type = request.user.userprofile.user_type
        if user_type == UserType.HOD.value:
            return redirect('/TMS/hod/get-hod-data/')
        elif user_type == UserType.SUPERVISOR.value:
            return redirect('/TMS/supervisor/get-supervisor-data/')
        else:
            return redirect('/TMS/login-redirect/')

def approve_transfer_request_redirect_view(request):
    if request.user.is_anonymous:
        return redirect('/TMS/login/')
    else:
        student_username = request.GET.get('student_username')
        if request.user.is_superuser:
            return redirect('/TMS-admin/')
        user_type = request.user.userprofile.user_type
        if user_type == UserType.HOD.value:
            return redirect('/TMS/hod/approve-transfer-request?student_username='+student_username)
        elif user_type == UserType.SUPERVISOR.value:
            return redirect('/TMS/supervisor/approve-transfer-request?student_username='+student_username)
        else:
            return redirect('/TMS/login-redirect/')
