from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import redirect

from transfers.constants import CampusType, UserType, TransferType
from transfers.models import PS2TSTransfer, UserProfile
from transfers.forms import PS2TSTransferForm, TS2PSTransferForm

from transfers.utils.student_utils import (
    get_application_status, notify_ps2ts, notify_ts2ps,
    get_branch_from_branch_code
)
from transfers.utils.shared_utils import get_deadline_status
import pandas as pd 

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from transfers.decorators import student_required

@method_decorator([login_required, student_required], name='dispatch')
class StudentDashboardView(generic.TemplateView):
    template_name = 'transfers/student_dashboard.html'
    context = {}

    def get(self, request, *args, **kwargs):
        # Status of application remains 0 until both
        # supervisor and hod approve the application
        current_userprofile = request.user.userprofile
        (application_type, has_applied, application_status,
            error) = get_application_status(current_userprofile)
        self.context['application_type'] = application_type
        self.context['has_applied'] = has_applied
       
        self.context['application_status'] = application_status
        self.context['error'] = error
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        current_userprofile = request.user.userprofile
        (application_type, has_applied, application_status,
            error) = get_application_status(current_userprofile)
        self.context['application_type'] = application_type
        self.context['has_applied'] = has_applied
        self.context['application_status'] = application_status
        self.context['error'] = error
        return render(request, self.template_name, self.context)

@method_decorator([login_required, student_required], name='dispatch')
class PS2TSFormView(generic.FormView):
    form_class = PS2TSTransferForm
    initial = {'key': 'value'}
    template_name = 'transfers/PS2TS.html'
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        # is supervisor email valid (present in DB)?
        invalid_supervisor_email = False
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form,
            'hod_email_list': hod_email_list,
            'invalid_supervisor_email': invalid_supervisor_email
        }
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        
        if not get_deadline_status(TransferType.PS2TS.value):
            return redirect('/TMS/student/dashboard/')
        print('there')
        post = request.POST.copy()
        post['applicant'] = request.user.userprofile
        request.POST = post
        form = self.form_class(request.POST)
        # is supervisor email valid (present in DB)?
        invalid_supervisor_email = False

        if form.is_valid():
            email = form.cleaned_data.get('supervisor_email')
            supervisor_email_qs = UserProfile.objects.filter(
                user_type=UserType.SUPERVISOR.value, user__email=email)
            print("@@",email)
            print(supervisor_email_qs)
            if supervisor_email_qs:
                contact = form.cleaned_data.get('contact')
                current_user = request.user.userprofile
                current_user.contact = contact
                current_user.save()
                form.save()
                notify_ps2ts(request)
                return redirect('/TMS/student/dashboard/')
            else:
                invalid_supervisor_email = True
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form,
            'hod_email_list': hod_email_list,
            'invalid_supervisor_email': invalid_supervisor_email
            }
      
     
        return render(request, self.template_name, self.context)
        
@method_decorator([login_required, student_required], name='dispatch')
class TS2PSFormView(generic.FormView):
    form_class = TS2PSTransferForm
    initial = {'key': 'value'}
    template_name = 'transfers/TS2PS.html'
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form, 
            'hod_email_list': hod_email_list
        }
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if not get_deadline_status(TransferType.TS2PS.value):
            return redirect('/TMS/student/dashboard/')
        post = request.POST.copy()
        post['applicant'] = request.user.userprofile
        request.POST = post
        form = self.form_class(request.POST)
        if form.is_valid():
            contact = form.cleaned_data.get('contact')
            current_user = request.user.userprofile
            current_user.contact = contact
            current_user.save()
            form.save()
            notify_ts2ps(request)
            return redirect('/TMS/student/dashboard/')
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form, 
            'hod_email_list': hod_email_list
        }
        return render(request, self.template_name, self.context)


def validate_supervisor_email(request):
    email = request.GET.get('email', None)
    supervisor_email_list = UserProfile.objects.filter(
        user_type=UserType.SUPERVISOR.value, user__email=email
    )
    name = ''
    campus = ''
    is_valid = False
    if supervisor_email_list:
        is_valid = True
        name = supervisor_email_list[0].user.get_full_name()
        campus = supervisor_email_list[0].campus
        if campus == CampusType.GOA.value:
            campus = "BITS Pilani, Goa Campus"
        elif campus == CampusType.HYD.value:
            campus = "BITS Pilani, Hyderabad Campus"
        elif campus == CampusType.PILANI.value:
            campus = "BITS Pilani, Pilani Campus"
    data = {
        'is_valid': is_valid,
        'name': name,
        'campus': campus
    }
    return JsonResponse(data)
