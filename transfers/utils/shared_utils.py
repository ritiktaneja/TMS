# This file will contain utility functions that are not strictly related to a single user types and other places
from transfers.constants import UserType, ApplicationsStatus, ThesisLocaleType
from transfers.models import DeadlineModel, PS2TSTransfer
from transfers.constants import TransferType
from django.utils import timezone as datetime


def update_application(applicant, application_type, approved_by, status):
    try:
        if application_type == TransferType.TS2PS:
            transfer_form = TS2PSTransfer.objects.get(applicant__user__username=applicant)
        else:
            transfer_form = PS2TSTransfer.objects.get(applicant__user__username=applicant)
        if approved_by == UserType.SUPERVISOR.value:
            transfer_form.is_supervisor_approved = int(status)
            print(int(status))
        elif approved_by == UserType.HOD.value:
            transfer_form.is_hod_approved = int(status)
            print(int(status))
        elif approved_by == UserType.AD.value:
            if application_type == TransferType.TS2PS:    
                transfer_form.is_hod_approved = int(status)
            else:
                transfer_form.is_supervisor_approved = int(status)
                transfer_form.is_hod_approved = int(status)
        transfer_form.save()
        return True
    except Exception as e:
        print(e) # left for debugging
        return False

def clean_list(application_list):
    for data in application_list:
        try:
            data['thesis_locale_alias'] = ThesisLocaleType._member_names_[data.pop('thesis_locale')]
            if 'is_supervisor_approved' in data:
                status_alias = ApplicationsStatus._member_names_[data.pop('is_supervisor_approved')]
                data['status'] = status_alias
                print(status_alias)
                print('OK 1')
            elif 'is_hod_approved' in data:
                status_alias = ApplicationsStatus._member_names_[data.pop('is_hod_approved')]
                data['status'] = status_alias
                print(status_alias)
                print('OK 2')
        except Exception as e:
            print('ERROR OCCURED!')
            print(e) # left for debugging
    return application_list

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
