from django.core.mail import send_mail
from .constants import UserType, TransferType, ThesisLocaleType, ApplicationsStatus
from django.http import JsonResponse
from .models import PS2TSTransfer, TS2PSTransfer, DeadlineModel
from django.utils import timezone as datetime

def get_application_status(userprofile):
    status = None
    alias = None
    has_applied = None
    error = None
    try:
        ps2ts = PS2TSTransfer.objects.filter(applicant=userprofile)
        ts2ps = TS2PSTransfer.objects.filter(applicant=userprofile)
        if ps2ts.count() == 1:
            alias = TransferType.PS2TS.value
            has_applied = 1
            error = 0
            status = _get_ps2ts_application_status(userprofile, ps2ts)
        elif ts2ps.count() == 1:
            alias = TransferType.TS2PS.value
            has_applied = 1
            status = _get_ts2ps_application_status(userprofile, ts2ps)
            error = 0
        else:
            status = -1
            has_applied = 0
            error = 0
    except Exception as e:
        status = -1
        has_applied = 0
        error = 1
    
    return (alias, has_applied, status, error)

def _get_ps2ts_application_status(userprofile, ps2ts):
    application = ps2ts[0]
    # until both supervisor and hod approves the application, the status remains 0
    if application.is_supervisor_approved == ApplicationsStatus.REJECTED.value or \
        application.is_hod_approved == ApplicationsStatus.REJECTED.value:
        return ApplicationsStatus.REJECTED.value
    else:
        return application.is_hod_approved * application.is_supervisor_approved

def _get_ts2ps_application_status(userprofile, ts2ps):
    application = ts2ps[0]
    return application.is_hod_approved

def notify_ps2ts(request):
    body = ""
    data=PS2TSTransfer.objects.filter(applicant = request.user.userprofile)[0]
    print(str(data.hod_email))
    body =  str("\nID: " + data.applicant.user.username+
    "\nName: " + data.applicant.user.first_name + " " +data.applicant.user.last_name +
    "\nTransfer Type: " + data.get_sub_type_display()+
    "\nCGPA: " + str(data.cgpa)+
    "\nThesis Locale: " + data.get_thesis_locale_display()+
    "\nThesis Subject: " + data.thesis_subject+
    "\nOrganization Name: " + data.name_of_org+
    "\nExpected Outcome: " + data.expected_deliverables)
    mail(data,request,body)

def notify_ts2ps(request):
    body = ""
    data=TS2PSTransfer.objects.filter(applicant = request.user.userprofile)[0]
    body =  str("\nID: " + data.applicant.user.username+
    "\nName: " + data.applicant.user.first_name + " " +data.applicant.user.last_name +
    "\nTransfer Type: " + data.get_sub_type_display()+
    "\nCGPA: " + str(data.cgpa)+
    "\nReason For Transfer: " + data.reason_for_transfer+
    "\nOrganization Name: " + data.name_of_org)
    mail(data,request,body)

def mail(data, request, body):
    send_mail("Transfer Application: " + request.user.username, body,
        'psdmail2020@gmail.com',[str(data.hod_email)],
        fail_silently=False)

def update_application(applicant, approved_by, status):
    try:
        transfer_form = PS2TSTransfer.objects.get(applicant__user__username=applicant)
        if approved_by == UserType.SUPERVISOR.value:
            transfer_form.is_supervisor_approved = int(status)
            print(int(status))
        elif approved_by == UserType.HOD.value:
            transfer_form.is_hod_approved = int(status)
            print(int(status))
        elif approved_by == UserType.AD.value:
            transfer_form.is_supervisor_approved = int(status)
            transfer_form.is_hod_approved = int(status)
        transfer_form.save()
        return True
    except Exception as e:
        print(e) # left for debugging
        return False
            
def fetch_ps2ts_list():
    ps2ts = PS2TSTransfer.objects.all().order_by('applicant.user.username')
    # fetching PS2TS data
    ps2ts_qs = PS2TSTransfer.objects.values(
        'applicant__user__username',
        'applicant__user__first_name', 'applicant__user__last_name',
        'sub_type', 'is_supervisor_approved',
        'is_hod_approved', 'cgpa', 'thesis_locale', 'supervisor_email',
            'thesis_subject', 'name_of_org', 'expected_deliverables'
    )
    # converting QuerySet --> List
    ps2ts_list = list(ps2ts_qs)
    return ps2ts_list

def fetch_ts2ps_list():
    ts2ps = TS2PSTransfer.objects.all().order_by('applicant.user.username')
    # fetching TS2PS data
    ts2ps_qs = TS2PSTransfer.objects.values(
        'applicant__user__username',
        'applicant__user__first_name', 'applicant__user__last_name',
        'sub_type', 'is_hod_approved', 'cgpa', 
            'reason_for_transfer', 'name_of_org', 
    )
    # converting QuerySet --> List
    ts2ps_list = list(ts2ps_qs)
    return ts2ps_list

def get_deadline_status(form_type):
    try:
        update_psd = DeadlineModel.objects.all().first()
    except:
        update_psd = DeadlineModel.objects.create()
    status = False
    if form_type == TransferType.PS2TS.value:
        if update_psd.is_active_PS2TS:
            if datetime.now() < update_psd.deadline_PS2TS:
                update_psd.is_active_PS2TS = True
                status = True
            else:
                
                update_psd.is_active_PS2TS = False
                status = False
        else:
            
            update_psd.is_active_PS2TS = False
            status = False
    else:
        if update_psd.is_active_TS2PS:
            if datetime.now() < update_psd.deadline_TS2PS:
                update_psd.is_active_TS2PS = True
                status = True
            else:
                update_psd.is_active_TS2PS = False
                status = False
        else:
            update_psd.is_active_TS2PS = False
            status = False
    update_psd.save()
    return status

def update_psd_data(form):
    try:
        update_psd = DeadlineModel.objects.all().first()
    except:
        update_psd = DeadlineModel.objects.create()
    update_psd.deadline_PS2TS = form.cleaned_data.get('deadline_PS2TS')
    update_psd.deadline_TS2PS = form.cleaned_data.get('deadline_TS2PS')
    update_psd.message = form.cleaned_data.get('message')
    update_psd.is_active_PS2TS = form.cleaned_data.get('is_active_PS2TS')
    update_psd.is_active_TS2PS = form.cleaned_data.get('is_active_TS2PS')
    update_psd.save()

def clean_list(application_list):
    for data in application_list:
        try:
            data['thesis_locale_alias'] = ThesisLocaleType._member_names_[data.pop('thesis_locale')]
            if 'is_supervisor_approved' in data:
                status_alias = ApplicationsStatus._member_names_[data.pop('is_supervisor_approved')]
                data['status'] = status_alias
            elif 'is_hod_approved' in data:
                status_alias = ApplicationsStatus._member_names_[data.pop('is_hod_approved')]
                data['status'] = status_alias  
        except Exception as e:
            print('ERROR OCCURED!')
            print(e) # left for debugging
    return application_list
