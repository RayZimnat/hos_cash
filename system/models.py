import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import *
from decimal import Decimal
from django.db.models import Sum


class BranchManager(models.Model):
    name = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=100)
    branch = models.CharField(max_length=50)


class Agent(models.Model):
    agent_code = models.CharField(max_length=50, unique=True)
    agent_name = models.CharField(max_length=200)
    agent_email = models.EmailField(max_length=75, blank=True)
    agent_branch = models.CharField(max_length=20, default='Harare')
    agent_payment_method = models.CharField(max_length=100, default='Ecocash')
    agent_phone = models.CharField(max_length=100)
    agent_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.15)

    def __str__(self):
        return self.agent_name

    def commission_total(self):
        commission_total = 0
        if self.policy_set.all():
            for policy in self.policy_set.all():
                policy_commission = policy.payment_set.all().filter(
                    payment_commission_paid=False).aggregate(
                    sum=Sum('payment_value'))
                if policy_commission['sum']:
                    commission_total += policy_commission['sum'] * self.agent_commission

        return commission_total


class FieldManager(models.Model):
    name = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=100)
    branch_manager = models.ForeignKey(BranchManager)

    def __str__(self):
        return self.name


class Branch(models.Model):
    user = models.CharField(max_length=20)
    branch = models.CharField(max_length=20)


class Book(models.Model):
    agent = models.ForeignKey(Agent, null=True)
    number_from = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.number_from)

    def number_to(self):
        return self.number_from + 49


class Insured(models.Model):
    insured_surname = models.CharField(max_length=200)
    insured_name = models.CharField(max_length=200)
    insured_gender = models.CharField(max_length=2,
                                      choices=(
                                          ('m', 'Male'),
                                          ('f', 'Female')),
                                      default='m'
                                      )
    insured_id_number = models.CharField(max_length=20)
    insured_nationality = models.CharField(max_length=50, blank=True, default='Zimbabwean')
    insured_dob = models.DateField()
    insured_phone = models.CharField(max_length=200)
    insured_employer = models.CharField(max_length=200, blank=True)
    insured_occupation = models.CharField(max_length=200, blank=True)
    insured_ec_number = models.CharField(max_length=50, blank=True)
    insured_address = models.TextField()
    insured_e_address = models.EmailField(max_length=50, blank=True)

    def __str__(self):
        return "{} {}".format(self.insured_name, self.insured_surname)


class PayingAuthority(models.Model):
    paying_authority_name = models.CharField(max_length=50, unique=True)
    paying_contact_person = models.CharField(max_length=50)
    paying_contact_number = models.CharField(max_length=50)
    paying_cut_off_date = models.CharField(max_length=50, default="Month-end")

    def __str__(self):
        return self.paying_authority_name


class Plan(models.Model):
    plan_name = models.CharField(max_length=50)
    plan_adult_premium = models.DecimalField(max_digits=12, decimal_places=2)
    plan_minor_premium = models.DecimalField(max_digits=12, decimal_places=2)
    plan_cover_limit = models.DecimalField(max_digits=12, decimal_places=2)
    plan_date_modified = models.DateTimeField(auto_now=True)
    plan_modified_by = models.CharField(max_length=50)

    def __str__(self):
        return self.plan_name


class Scheme(models.Model):
    scheme_name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.scheme_name


class Policy(models.Model):
    insured = models.ForeignKey(Insured)
    agent = models.ForeignKey(Agent)
    proposal_number = models.CharField(unique=True, max_length=50)
    proposal_date = models.DateField(default=timezone.now)
    inception_date = models.DateField(blank=True, null=True, )
    payment_method = models.CharField(default='ecocash',
                                      max_length=20,
                                      choices=(
                                          ('Ecocash', 'Ecocash'),
                                          ('Stop order', 'Stop order'),
                                          ('Cash', 'Cash'),
                                          ('Netcash', 'Netcash')
                                      ))
    paying_authority = models.ForeignKey(PayingAuthority, blank=True, null=True)
    renewed = models.BooleanField(default=False)
    lapsed = models.BooleanField(default=False)
    branch = models.CharField(max_length=20, default="Harare")
    created_by = models.CharField(max_length=50, default="Someone")
    date_created = models.DateTimeField(auto_now_add=True)
    scheme = models.ForeignKey(Scheme, blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    cancelled_date = models.DateField(null=True)
    cancellation_reason = models.CharField(max_length = 100, blank=True)

    def __str__(self):
        return "{} {} ({})".format(self.insured.insured_name.title(),
                                   self.insured.insured_surname.title(),
                                   self.proposal_number)

    def monthly_premium(self):

        version = self.policyversion_set.all().order_by('-version_date')[0]

        total_monthly = self.dependant_set.filter(
            renewal_version=version.renewal_version,
            endorsement_version=version.endorsement_version
        ).aggregate(
            sum=Sum('dependant_monthly_premium')
        )

        if total_monthly['sum'] == None:
            total_monthly['sum'] = 0

        return total_monthly['sum']

    def due_to_date(self):
        version = self.policyversion_set.all().order_by('-version_date')[0]

        total_due = self.instalment_set.filter(
            instalment_date_due__lte=datetime.date.today(),
            renewal_version=version.renewal_version,
            endorsement_version=version.endorsement_version
        ).aggregate(sum=Sum('instalment_amount'))
        return total_due['sum']

    def total_receipts(self):
        version = self.policyversion_set.all().order_by('-version_date')[0]

        total_due = self.instalment_set.filter(
            instalment_date_due__lte=datetime.date.today(),
            renewal_version=version.renewal_version,
            endorsement_version=version.endorsement_version
        ).aggregate(sum=Sum('instalment_amount'))
        if total_due['sum'] == None:
            total_due['sum'] = 0

        payments = self.payment_set.all().aggregate(Sum('payment_value'))
        if payments['payment_value__sum'] == None:
            payments['payment_value__sum'] = 0

        payments_total = payments['payment_value__sum']
        if payments_total == None:
            payments_total = 0

        instalment_total = self.instalment_set.all().filter(
            renewal_version=version.renewal_version,
            endorsement_version=version.endorsement_version
        ).aggregate(Sum('instalment_amount'))
        paid = 0
        if instalment_total['instalment_amount__sum'] == None:
            instalment_total['instalment_amount__sum'] = 0

        if instalment_total['instalment_amount__sum'] <= payments_total:
            if self.instalment_set.all().exists():
                next_date = 'Fully paid'
            else:
                next_date = '1st premium'

        for instalment in self.instalment_set.all().filter(
                renewal_version=version.renewal_version,
                endorsement_version=version.endorsement_version
        ):
            if paid < payments_total:
                paid += instalment.instalment_amount
                next_date = instalment.instalment_date_due
                continue
            elif paid == payments_total:
                next_date = instalment.instalment_date_due
                break
            else:
                break

        outstanding_now = total_due['sum'] - payments_total
        outstanding_total = instalment_total['instalment_amount__sum'] - payments_total
        return {'payments_total': payments_total,
                'next_date': next_date,
                'annual_premium': instalment_total['instalment_amount__sum'],
                'outstanding_now': outstanding_now,
                'outstanding_total': outstanding_total
                }

    def commission(self):
        commission_tot = self.total_receipts()['payments_total'] * self.agent.agent_commission
        return commission_tot

    def commission_paid(self):
        payments = Payment.objects.filter(
            payment_proposal_number=self.proposal_number).filter(
            payment_commission_paid=True).aggregate(
            Sum('payment_value'))

        if payments['payment_value__sum'] == None:
            payments['payment_value__sum'] = 0

        return payments['payment_value__sum'] * self.agent.agent_commission

    def commission_outstanding(self):
        payments = self.payment_set.all().filter(
            payment_commission_paid=False).aggregate(
            Sum('payment_value'))

        if payments['payment_value__sum'] == None:
            payments['payment_value__sum'] = 0

        return payments['payment_value__sum'] * self.agent.agent_commission

    def inception(self):
        # instalments = self.instalment_set.all()
        # instalments.delete()

        receipt_list = []
        receipts = Payment.objects.filter(payment_policy=self)

        if self.inception_date == None:
            if self.payment_set.all().count() > 0:
                receipts = self.payment_set.all()
                for receipt in receipts:
                    receipt_list.append(receipt.payment_date)

                receipt_list.sort()

                self.inception_date = receipt_list[0]
                self.save()

                print (self.insured.insured_surname + ' ' + self.inception_date.strftime("%d-%m-%Y"))
            else:
                print("No receipt")
        else:
            print("Already incepted")

        '''        
        if receipts:
            print ('pane receipt')
    
            for receipt in receipts:
                receipt_list.append(receipt.payment_date)
    
            receipt_list.sort()
    
            self.inception_date = receipt_list[0]
            self.save()
    
            for x in range(12):
                inst = Instalment(
                    instalment_date_due=receipt_list[0] + relativedelta(months=x),
                    instalment_amount=self.monthly_premium(),
                    renewal_version = 0,
                    endorsement_version = 0
                )
                self.instalment_set.add(inst, bulk=False)
    
        else:
            print ('no receipt')
            self.inception_date = None
            self.save()
    
        return "You're a star!"
        '''


class Card(models.Model):
    policy = models.ForeignKey(Policy)
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Card - " + self.policy.insured.insured_name[0] + ". " + self.policy.insured.insured_surname



class PolicyVersion(models.Model):
    policy = models.ForeignKey(Policy)
    version_date = models.DateTimeField(auto_now_add=True)
    renewal_version = models.IntegerField(default=0)
    endorsement_version = models.IntegerField(default=0)
    narration = models.CharField(max_length=100)
    effective_date = models.DateField(null=True)

    def __str__(self):
        return "{} {} ({}.{})".format(
            self.policy.insured.insured_surname,
            self.policy.insured.insured_name,
            self.renewal_version,
            self.endorsement_version)


class Dependant(models.Model):
    policy = models.ForeignKey(Policy)
    renewal_version = models.IntegerField(blank=True, null=True)
    endorsement_version = models.IntegerField(blank=True, null=True)
    dependant_name = models.CharField(max_length=200)
    dependant_id_number = models.CharField(max_length=50)
    dependant_dob = models.DateField()
    dependant_gender = models.CharField(max_length=2,
                                        choices=(
                                            ('m', 'Male'),
                                            ('f', 'Female')),
                                        default='m'
                                        )
    dependant_relationship = models.CharField(max_length=50)
    plan = models.ForeignKey(Plan)
    dependant_monthly_premium = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0)
    still_in_school = models.BooleanField(default=False)
    dependant_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.dependant_name

        # def dependant_monthly_premium(self):

    #	if self.dependant_dob<self.policy.inception_date-relativedelta(years=17):
    #		return self.plan.plan_adult_premium
    #	else:
    #		return self.plan.plan_minor_premium


class Instalment(models.Model):
    policy = models.ForeignKey(Policy)
    renewal_version = models.IntegerField(blank=True, null=True)
    endorsement_version = models.IntegerField(blank=True, null=True)
    instalment_date_due = models.DateField()
    instalment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    instalment_paid = models.BooleanField(default=False)
    instalment_paid_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.instalment_date_due.strftime('%B %Y') + ' instalment'

    def balance(self):
        allocations = self.allocation_set.all().aggregate(Sum('amount'))['amount__sum']

        if allocations == None:
            allocations = 0

        balance = self.instalment_amount - allocations
        return balance

class Payment(models.Model):
    payment_id = models.CharField(unique=True, max_length=50)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20)
    payment_value = models.DecimalField(max_digits=12, decimal_places=2)
    payment_proposal_number = models.CharField(max_length=50)
    payment_commission_paid = models.BooleanField(default=False)
    payment_policy = models.ForeignKey(Policy, blank=True, null=True)
    allocated = models.BooleanField(default=False)
    matched = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_id

    def balance(self):
        allocations = self.allocation_set.all().aggregate(Sum('amount'))['amount__sum']

        if allocations == None:
            allocations = 0

        balance = self.payment_value - allocations
        return balance



class Allocation(models.Model):
    receipt = models.ForeignKey(Payment)
    debit = models.ForeignKey(Instalment)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    date = models.DateTimeField(auto_now_add=True)


class SMS(models.Model):
    party_type = models.CharField(max_length=20)
    party_id = models.IntegerField()
    phone_number = models.CharField(max_length=50)
    type = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {}".format(self.type, self.party_type)
