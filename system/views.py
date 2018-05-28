import calendar
import csv
import datetime
import django_excel as excel
import io
import json
import pyexcel.ext.xlsx
import requests


from dateutil.relativedelta import *
from django.db.models import Q
from django.utils import timezone
from django.forms import modelformset_factory
from django.forms.models import inlineformset_factory, model_to_dict
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Sum
from django.template.context import RequestContext
from django.template.defaulttags import register
from dateutil.relativedelta import *
from django.views import generic

from .forms import (AgentSearchForm, CancelForm, PolicyForm, PolicyVersionForm, InsuredForm, LodgementReportForm,
                    LodgementDownloadForm, ReportForm, SearchForm, PayingAuthorityForm,GPWReportForm,AgentForm, BookForm)
from .models import (Agent, Allocation, Book, Branch, Dependant, Payment, PayingAuthority, Policy, PolicyVersion,
                     Insured, Instalment, Scheme, SMS)


def calculate_premium(dependant):
    if dependant.dependant_dob < dependant.policy.proposal_date - relativedelta(years=17):
        if dependant.dependant_dob > dependant.policy.proposal_date - relativedelta(years=22) and dependant.still_in_school == True:
            monthly_premium = dependant.plan.plan_minor_premium
        else:
            monthly_premium = dependant.plan.plan_adult_premium
    else:
        monthly_premium = dependant.plan.plan_minor_premium

    return monthly_premium


@register.filter
def get_value(dict, key):
    return dict[key]


def agent_search(request):
    if request.is_ajax():
        q = request.GET.get('q')

        if q is not None:
            agents = Agent.objects.filter(
                Q(agent_name__icontains=q) ).order_by( 'agent_name' )

            return render_to_response( 'system/agents.html',
                                       { 'agents': agents, },
                                       context_instance = RequestContext(request) )

@login_required
def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            policy_list = Policy.objects.filter(
                Q(proposal_number__icontains=form.cleaned_data['search'])|
                Q(insured__insured_surname__icontains=form.cleaned_data['search']) |
                Q(insured__insured_name__icontains=form.cleaned_data['search'])|
                Q(insured__insured_id_number__icontains=form.cleaned_data['search'])|
                Q(insured__insured_phone__icontains=form.cleaned_data['search'])|
                Q(dependant__dependant_name__icontains=form.cleaned_data['search'])|
                Q(dependant__dependant_id_number__icontains=form.cleaned_data['search'])
            ).filter(cancelled=False).order_by('-date_created').distinct()
        else:
            policy_list = ""
    else:
        policy_list = Policy.objects.order_by('-date_created')[:20]

        form = SearchForm()
    return render(request, 'system/index.html', {
        'policy_list': policy_list,
        'form': form
    })


def logout_view(request):
    logout(request)
    return HttpResponse("Logout successful")


@login_required
def create_policy(request):
    DependantFormSet = inlineformset_factory(Policy, Dependant,
                                             exclude=('policy', 'dependant_deleted', 'dependant_monthly_premium',
                                                      'renewal_version','endorsement_version'),
                                             extra=9)

    if request.method == 'POST':
        insured_form = InsuredForm(request.POST)
        policy_form = PolicyForm(request.POST)
        dependant_formset = DependantFormSet(request.POST, request.FILES)

        if insured_form.is_valid() and policy_form.is_valid() and dependant_formset.is_valid():
            insured = Insured(
                insured_surname=insured_form.cleaned_data['insured_surname'],
                insured_name=insured_form.cleaned_data['insured_name'],
                insured_gender=insured_form.cleaned_data['insured_gender'],
                insured_id_number=insured_form.cleaned_data['insured_id_number'],
                insured_dob=insured_form.cleaned_data['insured_dob'],
                insured_address=insured_form.cleaned_data['insured_address'],
                insured_phone=insured_form.cleaned_data['insured_phone'],
                insured_employer=insured_form.cleaned_data['insured_employer'],
                insured_e_address=insured_form.cleaned_data['insured_e_address'],
                insured_occupation=insured_form.cleaned_data['insured_occupation'],
                insured_nationality=insured_form.cleaned_data['insured_nationality'],
                insured_ec_number=insured_form.cleaned_data['insured_ec_number']
            )

            branch_user = Branch.objects.get(user=request.user.username)

            policy = Policy(
                proposal_number=policy_form.cleaned_data['proposal_number'].upper(),
                proposal_date=policy_form.cleaned_data['proposal_date'],
                payment_method=policy_form.cleaned_data['payment_method'],
                paying_authority=policy_form.cleaned_data['paying_authority'],
                agent=policy_form.cleaned_data['agent'],
                branch=branch_user.branch,
                created_by=request.user.username,
                scheme=policy_form.cleaned_data['scheme'],
            )

            insured.save()
            insured.policy_set.add(policy, bulk=False)

            policy = Policy.objects.get(proposal_number=policy_form.cleaned_data['proposal_number'].upper())

            version = PolicyVersion(
	            policy = policy,
	            narration = 'New'
            )

            version.save()

            dependant_formset = DependantFormSet(request.POST, request.FILES, instance=policy)
            dependant_formset.clean()
            dependant_formset.save()

            for dependant in policy.dependant_set.all():
                dependant.dependant_monthly_premium = calculate_premium(dependant)
                dependant.endorsement_version = 0
                dependant.renewal_version = 0

                dependant.save()


            #send SMS to client
            message = send_nb_sms(policy)

            return HttpResponseRedirect(reverse('system:view_policy', kwargs={'pk': policy.id}))
    else:
        insured_form = InsuredForm()
        policy_form = PolicyForm()
        dependant_formset = DependantFormSet()

    return render(request, 'system/create_policy.html',
                  {'insured_form': insured_form,
                   'policy_form': policy_form,
                   'dependant_formset': dependant_formset

                   })


def resend_sms(request):
    policy_id = request.GET.get('policy_id', None)
    sms_id = request.GET.get('sms_id', None)

    policy = Policy.objects.get(id=policy_id)
    sms = SMS.objects.get(id=sms_id)

    message = ""
    if sms.type == "New policy":
        message = send_nb_sms(policy)

    data = {'message':message}

    return JsonResponse(data)


def send_nb_sms(policy):

    client_message = "Dear {}\n" \
              "Thank you for taking up Hospital Cash Cover. Please pay your first premium to activate your policy {}.\n" \
              "Welcome to Zimnat family".format(policy.insured.insured_name.split(' ', 1)[0], policy.proposal_number)

    ins_f_name = policy.insured.insured_name.title() + " " + policy.insured.insured_surname.title()

    agent_message = "Your HCP Policy Captured\n"\
                    "Policy No: {}"\
                    "\nInsured: {}"\
                    "\nThank you for the support".format(policy.proposal_number, ins_f_name)
    client_sms = {
        'message': client_message,
        'recipients': policy.insured.insured_phone
    }

    result = send_sms(client_sms)

    if result['result']:
        status = 'Sent'
    else:
        status = 'Failed'

    SMS(
        party_type = "Insured",
        party_id = policy.id,
        phone_number = policy.insured.insured_phone,
        type = "New policy",
        message = client_message,
        status = status,
    ).save()

    if policy.agent.id not in [34, 12]: #Bancassurance, Direct
        agent_sms = {
            'message': agent_message,
            'recipients': policy.agent.agent_phone
        }

        result = send_sms(agent_sms)
        if result['result']:
            status = 'Sent'
        else:
            status = 'Failed'

        SMS(
            party_type="Agent",
            party_id=policy.agent.id,
            phone_number=policy.agent.agent_phone,
            type="New policy",
            message=agent_message,
            status=status,
        ).save()

    if result['result']:
        message = "SMS sent successfully"

    else:
        message = "SMS not sent.\n {}".format(result['error'])


    return message


@login_required
def cancel_policy(request, pk):

    policy = get_object_or_404(Policy, id=pk)
    if request.method == 'POST':
        form = CancelForm(request.POST)
        if form.is_valid():
            policy.cancelled = True
            policy.cancellation_reason = form.cleaned_data['reason']
            policy.cancelled_date = form.cleaned_data['date']
            policy.save()

            return HttpResponseRedirect(reverse('system:index',))

    else:
        form = CancelForm()
        return render(request, 'system/cancel_policy.html',
                      { 'policy':policy,
                        'form':form
                        })


@login_required
def dependant_endorsement(request, pk):
    DependantFormSet = modelformset_factory(Dependant,
                                            exclude=('policy', 'dependant_monthly_premium',
                                                     'endorsement_version', 'renewal_version'
                                                          ),
                                            extra=9,
                                            can_delete=True
                                            )


    policy = get_object_or_404(Policy, id=pk)
    version = policy.policyversion_set.all().order_by('-version_date')[0]
    renewal_version = version.renewal_version
    endorsement_version = version.endorsement_version

    if request.method == 'POST':
        dependant_formset = DependantFormSet(request.POST, request.FILES)
        policy_version_form = PolicyVersionForm(request.POST)
        if dependant_formset.is_valid() and policy_version_form.is_valid():
            for form in dependant_formset:
                dep = form.cleaned_data
                if not dep.get('DELETE'):
                    if dep.get('plan'):
                        dependant = Dependant(
                            renewal_version = renewal_version,
                            endorsement_version = endorsement_version+1,
                            dependant_name = dep.get('dependant_name'),
                            dependant_id_number = dep.get('dependant_id_number'),
                            dependant_dob = dep.get('dependant_dob'),
                            dependant_gender = dep.get('dependant_gender'),
                            plan = dep.get('plan'),
                            dependant_relationship = dep.get('dependant_relationship'),
                            still_in_school = dep.get('still_in_school'),
                        )
                        policy.dependant_set.add(dependant, bulk=False)

                        dependant.dependant_monthly_premium = calculate_premium(dependant)
                        dependant.save()

            version = PolicyVersion(
                    policy=policy,
                    renewal_version = renewal_version,
                    endorsement_version = endorsement_version+1,
                    narration = policy_version_form.cleaned_data['narration']
            )
            version.save()

            return HttpResponseRedirect(reverse('system:view_policy', kwargs={'pk': policy.id}))


    else:
        policy_version_form = PolicyVersionForm()
        dependants = policy.dependant_set.all().filter(
            renewal_version=renewal_version,
            endorsement_version=endorsement_version
        )
        dependant_formset = DependantFormSet(queryset=dependants)

    return render(request, 'system/endorsement.html',
                      { 'policy':policy,
                        'dependant_formset': dependant_formset,
                        'policy_version_form': policy_version_form
                       })



def insured_endorsement(request, pk):
    policy = get_object_or_404(Policy, id=pk)
    if request.method == 'POST':
        insured_form = InsuredForm(request.POST, instance=policy.insured)
        if insured_form.is_valid():

            if insured_form.has_changed():

                insured_form.save()
                """
                for field in insured_form.changed_data:
                    import pdb; pdb.set_trace()
                    policy.insured.__dict__[field] = insured_form.cleaned_data[field]
                    policy.insured.save()
                """
                return HttpResponseRedirect(reverse('system:view_policy', kwargs={'pk': policy.id}))
            else:
                return HttpResponseRedirect(reverse('system:view_policy', kwargs={'pk': policy.id}))

    else:
        insured_form = InsuredForm(instance=policy.insured)

    return render (request, 'system/insured_endorsement.html',
                   {
                       'policy': policy,
                       'insured_form': insured_form
                   })



def policy_versions(request, pk, rn, en):
    policy = get_object_or_404(Policy, id=pk)

    versions = policy.policyversion_set.all().order_by('-version_date')

    dependants = policy.dependant_set.all().filter(
        renewal_version=rn,
        endorsement_version=en
    )

    instalments = policy.instalment_set.all().filter(
        renewal_version=rn,
        endorsement_version=en
    )

    payments = policy.payment_set.all()
    return render(request, 'system/view_policy.html', {
        'policy': policy,
        'payments': payments,
        'dependants': dependants,
        'instalments':instalments,
        'versions':versions
    })



@login_required
def view_policy(request, pk):
    policy = get_object_or_404(Policy, id=pk)

    versions = policy.policyversion_set.all().order_by('-version_date')
    version = policy.policyversion_set.all().order_by('-version_date')[0]

    renewal_version = version.renewal_version
    endorsement_version = version.endorsement_version

    dependants = policy.dependant_set.all().filter(
        renewal_version=renewal_version,
        endorsement_version=endorsement_version
    )

    instalments = policy.instalment_set.all().filter(
        renewal_version=renewal_version,
        endorsement_version=endorsement_version
    )

    smses = SMS.objects.filter(
        party_type = "Insured",
        party_id = policy.id
    )

    payments = policy.payment_set.all()
    return render(request, 'system/view_policy.html', {
        'policy': policy,
        'payments': payments,
        'dependants': dependants,
        'instalments': instalments,
        'versions': versions,
        'smses': smses
    })


@login_required
def print_card(request, pk):

    policy = get_object_or_404(Policy, id=pk)

    versions = policy.policyversion_set.all().order_by('-version_date')
    version = policy.policyversion_set.all().order_by('-version_date')[0]

    renewal_version = version.renewal_version
    endorsement_version = version.endorsement_version

    dependants = policy.dependant_set.all().filter(
        renewal_version=renewal_version,
        endorsement_version=endorsement_version
    )

    return render(request, 'system/print_card.html', {
        'policy': policy,
        'dependants': dependants,
        'versions': versions
    })


@login_required
def view_agent(request, pk):
    agent = get_object_or_404(Agent, id=pk)

    agent_premium_total = sum(
        policy.total_receipts()['annual_premium'] for policy in agent.policy_set.all())

    agent_monthly_premium_total = sum(
        policy.monthly_premium() for policy in agent.policy_set.all())

    premium_paid_total = sum(
        policy.total_receipts()['payments_total'] for policy in agent.policy_set.all())

    total_commission = sum(
        policy.commission() for policy in agent.policy_set.all())

    total_commission_paid = sum(
        policy.commission_paid() for policy in agent.policy_set.all())

    total_commission_outstanding = sum(
        policy.commission_outstanding() for policy in agent.policy_set.all())

    return render(request, 'system/view_agent.html', {
        'agent': agent,
        'agent_premium_total': agent_premium_total,
        'agent_monthly_premium_total': agent_monthly_premium_total,
        'premium_paid_total': premium_paid_total,
        'total_commission_outstanding': total_commission_outstanding,
        'total_commission': total_commission,
        'total_commission_paid': total_commission_paid,
    })


@login_required
def list_view_agents(request):
    agent_list = Agent.objects.order_by('agent_name')
    return render(request, 'system/list_view_agents.html', {'agent_list': agent_list})


@login_required
def download(request, pk):

    agent = get_object_or_404(Agent, id=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Commission Statement.csv"'

    writer = csv.writer(response)
    writer.writerow([agent.agent_name, ])
    writer.writerow([agent.agent_code, ])
    writer.writerow([
        "Statement as at",
        datetime.date.today().strftime("%d - %m - %Y"),
    ])

    writer.writerow([
        "Proposal number",
        "Name",
        "Surname",
        "Inception Date",
        "Monthly prem",
        "Premium due",
        "Commision Due"
    ])
    for policy in Policy.objects.filter(cancelled=false).filter(agent=agent):
        if policy.inception_date:
            inception_date = policy.inception_date
        else:
            inception_date = 'none'

        writer.writerow([
            policy.proposal_number,
            policy.insured.insured_name,
            policy.insured.insured_surname,
            inception_date,
            policy.monthly_premium(),
            policy.total_receipts()['outstanding_now'],
            policy.commission_outstanding()
        ])

    return response


@login_required
def reports(request):
    annual_premium = 0
    if request.method == 'POST':
        form = ReportForm(request.POST)
        lodgement_report_form = False
        if form.is_valid():
            policy_list = Policy.objects.filter(
                Q(inception_date__gte=form.cleaned_data['inception_date_from']),
                Q(inception_date__lte=form.cleaned_data['inception_date_to'])
            ).order_by('-date_created')
            annual_premium = sum(
                policy.total_receipts()['annual_premium'] for policy in policy_list)
        else:
            policy_list = False
    else:
        policy_list = False
        form = ReportForm()
        lodgement_report_form = LodgementReportForm()

    return render(request,
                  'system/reports.html', {
                      'form': form,
                      'lodgement_report_form': lodgement_report_form,
                      'policy_list': policy_list,
                      'annual_premium': annual_premium
                  })


@login_required
def lodgement(request):
    if request.method == 'POST':
        form = LodgementReportForm(request.POST)
        if lodgement_report_form.is_valid():
             instalment_list = Instalment.objects.filter(
                Q(instalment_date_due__gte=lodgement_report_form.cleaned_data['installment_date_from']),
                Q(instalment_date_due__lte=lodgement_report_form.cleaned_data['installment_date_to']),
                Q(policy__payment_method=lodgement_report_form.cleaned_data['payment_method']),
            ).order_by('policy__insured__insured_employer')
        else:
            instalment_list = False
    else:
        form = LodgementReportForm()
    return render(request,
                  'system/lodgement_report.html', {
                      'form': form,
                  })


@login_required
def download_lodgement(request):
    form = LodgementDownloadForm(request.POST)

    if form.is_valid():

        if request.POST.get('paying_authority') == '':
            policies = Policy.objects.filter(Q(payment_method=request.POST.get('payment_method')),
                                             Q(instalment__instalment_date_due__gte=request.POST.get('date_from')),
                                             Q(instalment__instalment_date_due__lte=request.POST.get('to'))
            ).distinct()
        else:
            policies = Policy.objects.filter(Q(payment_method=request.POST.get('payment_method')),
                                             Q(paying_authority=request.POST.get('paying_authority')),
                                             Q(instalment__instalment_date_due__gte=request.POST.get('date_from')),
                                             Q(instalment__instalment_date_due__lte=request.POST.get('to'))
            ).distinct()



        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Lodgement Schedule.csv"'

        writer = csv.writer(response)
        if request.POST.get('paying_authority') == '':
            writer.writerow(['Lodgement Schedule', ])
        else:
            writer.writerow([PayingAuthority.objects.get(id=request.POST.get('paying_authority')).paying_authority_name + ' Lodgement Schedule', ])
        writer.writerow([
            "Policy number",
            "Name",
            "Surname",
            "ID Number",
            "EC Number",
            "Phone number",
            "Montlhy instalment",
            "Amount outstanding",
        ])
        for policy in policies:
            instalment = Instalment.objects.filter(
                Q(instalment_date_due__gte=request.POST.get('date_from')),
                Q(instalment_date_due__lte=request.POST.get('to')),
                Q(policy=policy)
            ).order_by('-instalment_date_due')[:1].get()
            writer.writerow([
                policy.proposal_number,
                policy.insured.insured_name,
                policy.insured.insured_surname,
                policy.insured.insured_id_number,
                policy.insured.insured_ec_number,
                policy.insured.insured_phone,
                instalment.instalment_amount,
                policy.total_receipts()['outstanding_now'],
            ])

        return response

    return render(request,
                  'system/lodgement_report.html', {
                      'form': form,
                  })


def download_clients(request):
    insured_list = Insured.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Hospital Cash Clients.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', ])
    writer.writerow(['User', ])

    writer.writerow([
        "Full name",
        "Phone number",

    ])
    for insured in insured_list:
        writer.writerow([
            insured.insured_name + " " + insured.insured_surname,
            insured.insured_phone
        ])

    return response


def receipts(request):

    unmatched_receipt_list = Payment.objects.filter(
        Q(allocated=False),
    ).order_by('-payment_date')

    return render(request, 'system/receipts.html', {
        'unmatched_receipt_list':unmatched_receipt_list,
    })


def auto_match(request):
    unmatched_receipt_list = Payment.objects.filter(Q(allocated=False))

    for receipt in unmatched_receipt_list:

        try:
            policy = Policy.objects.get(proposal_number=receipt.payment_proposal_number.upper())

        except Policy.DoesNotExist:
            continue

        allocate_premium(policy, receipt)

    return redirect('system:receipts')


def match_receipt(request, pk):
    receipt = Payment.objects.get(id=pk)
    sch = False
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            policy_list = Policy.objects.filter(
                Q(proposal_number__icontains=form.cleaned_data['search'])|
                Q(insured__insured_surname__icontains=form.cleaned_data['search']) |
                Q(insured__insured_name__icontains=form.cleaned_data['search'])|
                Q(insured__insured_id_number__icontains=form.cleaned_data['search'])|
                Q(insured__insured_phone__icontains=form.cleaned_data['search'])|
                Q(dependant__dependant_name__icontains=form.cleaned_data['search'])|
                Q(dependant__dependant_id_number__icontains=form.cleaned_data['search'])
            ).order_by('-date_created').distinct()
        else:
            policy_list = ""
    else:
        policy_list = ""
        sch = True
        form = SearchForm()

    return render (request, 'system/match_receipt.html', {
        'receipt':receipt,
        'policy_list': policy_list,
        'form': form,
        'sch':sch
    }
    )


def match(request, pk, rk):
    policy = Policy.objects.get(id=pk)
    receipt = Payment.objects.get(id=rk)

    allocate_premium(policy, receipt)


    return redirect('system:receipts')


def allocate_premium(policy, receipt):

    if policy.payment_set.count() < 1:

        policy.inception_date = receipt.payment_date
        policy.save()

        if receipt.payment_value < policy.monthly_premium():
            message = "Dear {}\n" \
                      "Your premium of ${} has been received.  Please pay the balance of ${} to activate your policy".format(
                policy.insured.insured_name.title(),
                str(receipt.payment_value),
                str(policy.monthly_premium()-receipt.payment_value)
            )
        else:
            message = "Dear {}\n" \
                      "Your premium of ${} has been received.  You policy is now active.  Your policy # is {} \n" \
                      "Please get in touch to collect your card".format(
                policy.insured.insured_name.title(),
                receipt.payment_value,
                policy.proposal_number
            )

    else:
        message = "Dear {}\n" \
                  "Your premium of ${} has been received.  Your next premium of * is due on * ".format( #TODO Add next premium due and date
            policy.insured.insured_name,
            receipt.payment_value,

        )
    sms = {
        'message': message,
        'recipients': policy.insured.insured_phone
    }
    send_sms(sms)

    policy.payment_set.add(receipt, bulk=False)
    receipt.allocated=True
    receipt.save()

def add_paying_authority(request):
    if request.method == 'POST':
        paying_authority_form = PayingAuthorityForm(request.POST)

        if paying_authority_form.is_valid():
            last_save = paying_authority_form.cleaned_data['paying_authority_name']
            paying_authority_form.save()
            message = last_save + ' has been saved successfully'
            messages.add_message(request, messages.INFO, message)

            return HttpResponseRedirect(reverse('system:add_paying_authority'))
    else:
        paying_authority_form = PayingAuthorityForm()

    return render(request, 'system/add_paying_authority.html',
                  {'paying_authority_form': paying_authority_form,}
                  )



def birthday_message():
    recipients = Dependant.object.filter(dependant_dob=datetime.date.today())

    for recipient in recipients:
        if recipient.dependant_relationship == self:
            message = "Happy birthday to a much cherished client. Our whole team at Zimnat recognises your role in our success " \
                      "and wishes you a special day!!"

        else:
            message = "Today is your {} {} birthday.  We wish you e special day for your entire family.".format(
                recipient.dependant_relationship,
                recipient.dependant_name
            )

        sms = {
            'message': message,
            'recipients': recipient.policy.insured.insured_phone
        }
        send_sms(sms)


def send_statements(request):
    agents = request.POST.getlist('agents[]')

    for agent in agents:
        this_agent = Agent.objects.get(id=agent)
        policies = Policy.objects.filter(agent=this_agent)
        csvfile = io.StringIO()
        csvwriter = csv.writer(csvfile)

        csvwriter.writerow(['Agent name:',this_agent.agent_name,])
        csvwriter.writerow(['Agent code:',this_agent.agent_code,])
        csvwriter.writerow(['Statement as at:', datetime.date.today().strftime('%d %B %Y')])
        csvwriter.writerow(['Policy number',
                            'Name',
                            'Surname',
                            'Phone number',
                            'Proposal date',
                            'Inception date',
                            'Monthly premium',
                            'Outstanding premium',
                            ])

        for policy in policies:
            csvwriter.writerow([
                policy.proposal_number,
                policy.insured.insured_name,
                policy.insured.insured_surname,
                policy.insured.insured_phone,
                policy.proposal_date,
                policy.inception_date,
                policy.monthly_premium(),
                policy.total_receipts()['outstanding_now'],
            ])

        message = EmailMessage("Commission Statement",
                               request.POST.get('email_text','') +
                               "\n\nRegards, \n\n"
                               "Hospital Cash team",
                               "Hospital Cash <do_not_reply@zimnat.co.zw>",
                               [this_agent.agent_email])
        message.attach('Statement - ' + this_agent.agent_name + '.csv', csvfile.getvalue(), 'text/csv')
        message.send()

    return HttpResponse('Zvaita')


def gwp_report(request):

    if request.method == 'POST':
        form = GPWReportForm(request.POST)
        schemes = Scheme.objects.all()
        scheme_list = []
        premium_list={}
        paid_up_list={}

        if form.is_valid():
            for scheme in schemes:
                scheme_list.append(scheme.scheme_name)
                instalments = Instalment.objects.filter(
                    Q(instalment_date_due__gte=form.cleaned_data['date_from']),
                    Q(instalment_date_due__lte=form.cleaned_data['date_to']),
                    Q(policy__scheme=scheme)
                )

                paid_up = Payment.objects.filter(
                    Q(payment_date__gte=form.cleaned_data['date_from']),
                    Q(payment_date__lte=form.cleaned_data['date_to']),
                    Q(payment_policy__scheme=scheme)
                )
                prem = instalments.aggregate(Sum('instalment_amount'))['instalment_amount__sum']
                paid_up_prem = paid_up.aggregate(Sum('payment_value'))['payment_value__sum']

                premium_list[scheme.scheme_name]=prem
                paid_up_list[scheme.scheme_name]=paid_up_prem

    else:
        form = GPWReportForm()
        scheme_list = False
        premium_list = False
        paid_up_list = False

    return render(request,
                  'system/gwp_report.html',
                  {
                      'form': form,
                      'scheme_list':scheme_list,
                      'premium_list':premium_list,
                      'paid_up_list':paid_up_list
                  })


def agent_statements(request):
    if request.method == "POST":
        form = AgentSearchForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['agent_branch'] == '':
                agent_list = Agent.objects.filter(
                    Q(agent_name__icontains=form.cleaned_data['agent_name']),
                    Q(agent_code__icontains=form.cleaned_data['agent_code'])).order_by('-agent_name')
            else:
                agent_list = Agent.objects.filter(
                    Q(agent_name__icontains=form.cleaned_data['agent_name']),
                    Q(agent_branch=form.cleaned_data['agent_branch']),
                    Q(agent_code__icontains=form.cleaned_data['agent_code'])).order_by('-agent_name')
        else:
            agent_list = ""
    else:
        agent_list = Agent.objects.order_by('agent_name')
        form = AgentSearchForm()

    return render(request, 'system/agent_statements.html', {'agent_list': agent_list,
                                                                'form':form})


def add_agent(request):
    book_form = False
    if request.method == 'POST':
        agent_form = AgentForm(request.POST)

        if agent_form.is_valid():
            last_save = agent_form.cleaned_data['agent_name']
            agent = agent_form.save()
            message = last_save + ' has been saved successfully'
            messages.add_message(request, messages.INFO, message)

            return HttpResponseRedirect(reverse('system:allocate_book',kwargs={'pk':agent.id} ))
    else:
        agent_form = AgentForm()

    return render(request, 'system/add_agent.html',
                  {'agent_form': agent_form,
                   'book_form':book_form
                   }
                  )


def allocate_book(request, pk):
    agent = Agent.objects.get(id=pk)
    book_form = BookForm()
    return render (request, 'system/add_agent.html',
                   {'agent':agent,
                    'book_form':book_form}
    )


def allocate(request, agent):
    if request.method =='POST':
        book_form = BookForm(request.POST)
        agent = Agent.objects.get(id=agent)

        if book_form.is_valid():
            book = book_form.save()
            agent.book_set.add(book, bulk=False)

            message = "Book " + str(book.number_from) + ' allocated to ' + agent.agent_name
            messages.add_message(request, messages.INFO, message)

            return render(request, 'system/add_agent.html', {})

    return render(request, 'system/add_agent.html', {'book_form':book_form,
                                                     'agent':agent})


def comm_statements(request):
    if request.method == "POST":
        form = AgentSearchForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['agent_branch'] == '':
                agent_list = Agent.objects.filter(
                    Q(agent_name__icontains=form.cleaned_data['agent_name']),
                    Q(agent_code__icontains=form.cleaned_data['agent_code'])).order_by('-agent_name')
            else:
                agent_list = Agent.objects.filter(
                    Q(agent_name__icontains=form.cleaned_data['agent_name']),
                    Q(agent_branch=form.cleaned_data['agent_branch']),
                    Q(agent_code__icontains=form.cleaned_data['agent_code'])).order_by('-agent_name')
        else:
            agent_list = ""
    else:
        agent_list = Agent.objects.order_by('agent_name')
        form = AgentSearchForm()

    return render(request, 'system/comm_statements.html', {'agent_list': agent_list,
                                                                'form':form})


def download_statement(request):
    agents = request.POST.getlist('agents[]')
    import pdb; pdb.set_trace()
    if request.POST.get('download_statement')== 'Download statement':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Hospital Cash Commision Statement.csv"'

        writer = csv.writer(response)
        writer.writerow(['Hospital Cash Commision Statement', ])
        writer.writerow(['As at', datetime.date.today() ])

        writer.writerow([
            "Agent Code",
            "Agent Name",
            "Branch",
            "Phone number",
            "Number of policies",
            "Commision due",
        ])

        for agent in agents:
            agent = Agent.objects.get(id=agent)

            writer.writerow([
                agent.agent_code,
                agent.agent_name,
                agent.agent_branch,
                agent.agent_phone,
                agent.policy_set.count(),
                agent.commission_total()
            ])

        return response
    elif request.POST.get('download_statement')== 'Pay commissions':
        for agent in agents:
            agent = Agent.objects.get(id=agent)

            if agent.policy_set.all():
                for policy in agent.policy_set.all():
                    receipts  = policy.payment_set.all().filter(payment_commission_paid=False)

                    for receipt in receipts:
                        receipt.payment_commission_paid = True
                        receipt.save()
        return HttpResponseRedirect(reverse('system:comm_statements', ))





def renew(policies, month,year):
    #month = 1
    #year = 2017
    last_day = calendar.monthrange(year, month)[1]

    for policy in policies:
        if policy.instalment_set.filter(
                instalment_date_due__lte=datetime.date(year, month, last_day),
                instalment_date_due__gte=datetime.date(year, month, 1)):
            print ('policy already renewed')
        else:
            policy_version = policy.policyversion_set.all().order_by('-version_date')[0]

            next_premium = monthly_premium(policy, policy_version)
            debit_list = []
            debits = policy.instalment_set.all()
            for debit in debits:
                debit_list.append(debit.instalment_date_due)

            debit_list.sort(reverse=True)

            next_instalment_date =debit_list[0] + relativedelta(months=1)

            new_debit = Instalment(
                instalment_date_due=next_instalment_date,
                instalment_amount=next_premium,
                renewal_version=0,
                endorsement_version=0
            )

            policy.instalment_set.add(new_debit, bulk=False)


def new_business_report(request):
    policies = Policy.objects.filter(proposal_date__gte=datetime.date(2018, 1, 1),
                                     proposal_date__lte=datetime.date.today())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="New Business.csv"'

    writer = csv.writer(response)

    writer.writerow(["Policy #","Agent", "Proposal Date", "Premium", "Inception date"])

    for p in policies:
        writer.writerow([
            p.proposal_number,
            p.agent.agent_name,
            p.proposal_date,
            str(p.monthly_premium()),
            p.inception_date
        ])

    return response


def test(request):
    agent = Agent.objects.get(id=34)
    policies = Policy.objects.filter(proposal_date__gte=datetime.date(2017,1,1),proposal_date__lte=datetime.date(2017,12,31),agent=agent)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Unmtched receipts.csv"'

    writer = csv.writer(response)

    writer.writerow(["Policy #",  "Date", "Premium"])

    for p in policies:
        writer.writerow([
            p.proposal_number,
            p.proposal_date,
            str(p.monthly_premium()),
        ])

    return response
    """
    debits  = Instalment.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Unmtched receipts.csv"'

    writer = csv.writer(response)


    writer.writerow(["Policy", "renewal","endt", "Date" ])

    for p in debits:

        writer.writerow([
            p.policy.proposal_number,
            p.renewal_version,
            p.endorsement_version,
            p.instalment_date_due,
            p.instalment_amount
        ])


    return response
    """

"""
def download_dev(request):
    #p = Policy.objects.all()
    rec_nums = ''
    p = Policy.objects.filter(agent__id='34')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Barclays statement.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Policy #',
        'Name',
        'Proposal date',
        'Monthly Premium',
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct', 
        'Nov',
        'Dec',
    ])



    for pol in p:
        jan_rec_nums = ''
        feb_rec_nums = ''
        mar_rec_nums = ''
        apr_rec_nums = ''
        may_rec_nums = ''
        jul_rec_nums = ''
        jun_rec_nums = ''

        jan_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #jan_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)
        #                            ).count()

        feb_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,2,28),payment_date__gte=datetime.date(2017,2,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #feb_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,2,28),payment_date__gte=datetime.date(2017,2,1)
        #                            ).count()

        mar_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,3,31),payment_date__gte=datetime.date(2017,3,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #mar_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,3,31),payment_date__gte=datetime.date(2017,3,1)
        #                            ).count()

        apr_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,4,30),payment_date__gte=datetime.date(2017,4,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #apr_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,4,30),payment_date__gte=datetime.date(2017,4,1)
        #                            ).count()

        may_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,5,31),payment_date__gte=datetime.date(2017,5,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #may_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,5,31),payment_date__gte=datetime.date(2017,5,1)
        #                            ).count()

        jun_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,6,30),payment_date__gte=datetime.date(2017,6,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #jun_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,6,30),payment_date__gte=datetime.date(2017,6,1)
        #                            ).count()

        jul_premium = pol.payment_set.filter(payment_date__lte=datetime.date(2017,7,31),payment_date__gte=datetime.date(2017,7,1)
                                    ).aggregate(sum=Sum('payment_value'))['sum']
        #jul_count = pol.payment_set.filter(payment_date__lte=datetime.date(2017,7,31),payment_date__gte=datetime.date(2017,7,1)
        #                            ).count()
        aug_premium = pol.payment_set.filter(
            payment_date__lte=datetime.date(2017, 8, 31), payment_date__gte=datetime.date(2017, 8, 1)
                               ).aggregate(sum=Sum('payment_value'))['sum']
        sep_premium = pol.payment_set.filter(
            payment_date__lte=datetime.date(2017, 9, 30), payment_date__gte=datetime.date(2017,9, 1)
        ).aggregate(sum=Sum('payment_value'))['sum']

        oct_premium = pol.payment_set.filter(
            payment_date__lte=datetime.date(2017, 10, 31), payment_date__gte=datetime.date(2017, 10, 1)
        ).aggregate(sum=Sum('payment_value'))['sum']

        '''
        if jan_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)):
                jan_rec_nums += ' ' + str(rec.payment_id)
        else:
            jan_rec_nums = 'nil'

        if feb_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017, 1, 31),
                                              payment_date__gte=datetime.date(2017, 1, 1)):
                feb_rec_nums += ' ' + str(rec.payment_id)
        else:
            feb_rec_nums = 'nil'

        if mar_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)):
                mar_rec_nums += ' ' + str(rec.payment_id)
        else:
            mar_rec_nums = 'nil'

        if apr_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)):
                apr_rec_nums += ' ' + str(rec.payment_id)
        else:
            apr_rec_nums = 'nil'

        if may_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)):
                may_rec_nums += ' ' + str(rec.payment_id)
        else:
            may_rec_nums = 'nil'

        if jun_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017,1,31),payment_date__gte=datetime.date(2017,1,1)):
                jun_rec_nums += ' ' + str(rec.payment_id)
        else:
            jun_rec_nums = 'nil'

        if jul_count > 0:
            for rec in pol.payment_set.filter(payment_date__lte=datetime.date(2017, 1, 31),
                                              payment_date__gte=datetime.date(2017, 1, 1)):
                jul_rec_nums += ' ' + str(rec.payment_id)
        else:
            jul_rec_nums = 'nil'
        '''

        writer.writerow([
            pol.proposal_number,
            pol.insured.insured_name+ ' ' + pol.insured.insured_surname,
            pol.proposal_date.strftime('%d/%m/%Y'),
            str(pol.monthly_premium()),
            jan_premium,
            feb_premium,
            mar_premium,
            apr_premium,
            may_premium,
            jun_premium,
            jul_premium,
            aug_premium,
            sep_premium,
            oct_premium,

        ])

    return response
"""



def download_dev(request):
    p = Policy.objects.filter(agent__id='34')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Barclays statement.csv"'

    writer = csv.writer(response)

    months = {
        1: ['Jan', 31],
        2: ['Feb', 29],
        3: ['Mar', 31],
        4: ['Apr', 30],
        5: ['May', 31],
        6: ['Jun', 30],
        7: ['Jul', 31],
        8: ['Aug', 31],
        9: ['Sep', 30],
        10: ['Oct', 31],
        11: ['Nov', 30],
        12: ['Dec', 31]
    }

    writer.writerow([
        'Policy #',
        'Name',
        'Proposal date',
        'Monthly Premium',
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    ])

    for pol in p:
        monthly_prems = []
        for x in range(1,13):

            prem = pol.payment_set.filter(
                payment_date__lte=datetime.date(2016, x,months[x][1]),
                payment_date__gte=datetime.date(2016, x, 1)
            ).aggregate(sum=Sum('payment_value'))['sum']
            monthly_prems.append(prem)

        writer.writerow([
            pol.proposal_number,
            pol.insured.insured_name+ ' ' + pol.insured.insured_surname,
            pol.proposal_date.strftime('%d/%m/%Y'),
            str(pol.monthly_premium()),
            monthly_prems[0],
            monthly_prems[1],
            monthly_prems[2],
            monthly_prems[3],
            monthly_prems[4],
            monthly_prems[5],
            monthly_prems[6],
            monthly_prems[7],
            monthly_prems[8],
            monthly_prems[9],
            monthly_prems[10],
            monthly_prems[11],


        ])

    return response


def download_dev1(request):
    p = Policy.objects.all()
    rec_nums = ''
    #p = Policy.objects.filter(agent__id='34')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Mar statement.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Policy #',
        'Name',
        'Agent',
        'inception date',
        'Monthly Premium',
        'Payment method selected',
        'Payment method used',
        'Paying authority',
        'Paid premium',
        'Number of receipts',
        "Receipt refs",
        ])

    for pol in p:
        rec_refs = ''

        rec_set = pol.payment_set.filter(payment_date__lte=datetime.date(2018,4,30),
                                         payment_date__gte=datetime.date(2018,4,1))

        prem_paid = rec_set.aggregate(sum=Sum('payment_value'))['sum']
        count = rec_set.count()

        if count > 0:
            method_used = rec_set[0].payment_method
            for rec in rec_set:
                rec_refs += ' ' + str(rec.payment_id)
        else:
            rec_refs = 'nil'
            method_used = ''

        writer.writerow([
            pol.proposal_number,
            pol.insured.insured_name+ ' ' + pol.insured.insured_surname,
            pol.agent.agent_name,
            pol.inception_date,
            str(pol.monthly_premium()),
            pol.payment_method,
            method_used,
            pol.paying_authority,
            prem_paid,
            count,
            rec_refs
        ])


    return response


def unmatched_report(request):
    receipts = Payment.objects.filter(
        allocated=False,
    #    payment_date__lte=datetime.date(2017, 9, 30),
    #    payment_date__gte=datetime.date(2017, 1, 1)
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Unmatched receipts.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Receipt Ref',
        'Date',
        'Payment method',
        'ref',
        'Amount'
    ])

    for receipt in receipts:

        writer.writerow([
            receipt.payment_id,
            receipt.payment_date.strftime('%d/%m/%Y'),
            receipt.payment_method,
            receipt.payment_proposal_number,
            receipt.payment_value
        ])

    return response


def download_policy_list(request):
    policies = Policy.objects.filter(agent__id=34)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Policies.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Policy number',
        'Agent',
        'Proposal date',
        'Premium',
        'Payment method',
        'Paying authority',
    ])

    for policy in policies:
        writer.writerow([
            policy.proposal_number,
            policy.agent.agent_name,
            policy.proposal_date.strftime('%d/%m/%Y'),
            str(policy.monthly_premium()),
            policy.payment_method,
            policy.paying_authority,
        ])

    return response


def send_sms(sms):
    settings = {
        'sub_account': '2673_hcp',
        'sub_account_pass': 'rayjowa001',
        'action': 'send_sms',
    }

    parameters = {**settings, **sms}
    parameters['recipients'] = '0773152085'
    status = requests.get("http://cheapglobalsms.com/api_v1", params=parameters)
    error = ""

    try:
        response = status.json()['batch_id']
        result = True

    except KeyError:
        result = False
        error = status.json()['error']


    return {'result':result, 'error':error}


def restructure(policies):
    #policies = Policy.objects.exclude(inception_date=None)
    count = 0
    for policy in policies:
        count +=1
        print(str(count) + 'of' + str(policies.count()))
        version = policy.policyversion_set.get(renewal_version=0, endorsement_version=0)
        monthly_prem = monthly_premium(policy, version)
        i = 0
        if policy.payment_set.all():
            receipt_list = []
            recs = policy.payment_set.all()
            for receipt in recs:
                receipt_list.append(receipt.payment_date)

            receipt_list.sort()

            policy.inception_date = receipt_list[0]
            policy.save()

        policy.instalment_set.all().delete()
        instalment = Instalment(
                    instalment_date_due=policy.inception_date,
                    instalment_amount=monthly_prem,
                    renewal_version = 0,
                    endorsement_version = 0
                )

        while instalment.instalment_date_due <= datetime.date(2017,12,31):
            policy.instalment_set.add(instalment, bulk=False)
            i += 1
            instalment = Instalment(
                instalment_date_due=policy.inception_date + relativedelta(months=i),
                instalment_amount=monthly_prem,
                renewal_version=0,
                endorsement_version=0
            )
        if policy.policyversion_set.count() > 1:
            for version in policy.policyversion_set.order_by('version_date'):
                new_prem = monthly_premium(policy,version)
                for instalment in policy.instalment_set.all():
                    if instalment.instalment_date_due >= version.version_date.date():
                        instalment.instalment_amount = new_prem
                        instalment.save()






def monthly_premium(policy, version):
    total_monthly = policy.dependant_set.filter(
        renewal_version=version.renewal_version,
        endorsement_version=version.endorsement_version
    ).aggregate(
        sum=Sum('dependant_monthly_premium')
    )

    if total_monthly['sum'] == None:
        total_monthly['sum'] = 0

    return total_monthly['sum']


def allocate_premiums(policy):
    debits = policy.instalment_set.filter(instalment_paid=False)
    recs = policy.payment_set.filter(matched=False)

    for receipt in recs:
        if receipt.balance() > 0:
            for debit in debits:
                if debit.balance() > 0:
                    if debit.balance() > receipt.balance():
                        Allocation(
                            receipt = receipt,
                            debit = debit,
                            amount = receipt.balance()
                        ).save()
                        receipt.matched=True
                        receipt.save()
                    else:
                        Allocation(
                            receipt=receipt,
                            debit=debit,
                            amount=debit.balance()
                        ).save()
                        debit.instalment_paid = True
                        debit.instalment_paid_date = receipt.payment_date
                        debit.save()






