from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import ( Agent, Allocation, Branch, Book, Card, Claim, ClaimEvent, Dependant,
                      Insured, Instalment, Payment, Plan, Policy, PolicyVersion, PayingAuthority, Scheme, SMS )

class AgentAdmin(admin.ModelAdmin):
	search_fields = ['agent_name']


class CardAdmin(admin.ModelAdmin):
    pass


class PolicyAdmin(admin.ModelAdmin):
	inlines = [ClaimEvent]
	list_display = ('claim_number', )


class PaymentResource(resources.ModelResource):
	

	class Meta:
		model = Payment
		import_id_fields = ("payment_id",)
		exclude = ('payment_matched','payment_commission_paid',)


class PaymentAdmin(ImportExportModelAdmin):
	resource_class = PaymentResource
	search_fields = ['payment_id', 'payment_proposal_number',  ]


class DependantInLine(admin.TabularInline):
	model = Dependant
	extra = 5

class InstalmentInLine(admin.TabularInline):
	model = Instalment
	extra = 1

class VersionInLine(admin.TabularInline):
    model = PolicyVersion
    readonly_fields = ('version_date',)
    extra = 1

class CardInLine(admin.StackedInline):
	model = Card

class PolicyAdmin(admin.ModelAdmin):
	inlines = [DependantInLine, InstalmentInLine, VersionInLine, CardInLine]
	list_display = ('proposal_number', 'date_created', 'inception_date')
	list_filter = ['date_created', ]
	search_fields = ['proposal_number']

admin.site.register(Claim)
admin.site.register(Insured)
admin.site.register(Card)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Allocation)
admin.site.register(Branch)
admin.site.register(Book)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PayingAuthority)
admin.site.register(Plan)
admin.site.register(Scheme)
admin.site.register(SMS)


