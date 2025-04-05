from django.contrib import admin

from .models import (GeneticOrganisation, HydrogenaseClass,
                     HydrogenaseSequence, NonHydrogenaseSequence, Structure)


@admin.register(HydrogenaseSequence)
class HydrogenaseSequenceAdmin(admin.ModelAdmin):

    list_display = ('ncbi_accession', 'organism',
                    'hydrogenase_class', 'phylum', 'order')

    search_fields = ('ncbi_accession', 'organism',
                     'hydrogenase_class__name', 'phylum', 'activity_predicted')

    list_filter = ('hydrogenase_class', 'phylum', 'activity_predicted',
                   'oxygen_tolerance_predicted', 'subunits_predicted',
                   'accessory_subunits_predicted')

    radio_fields = {'activity_predicted': admin.HORIZONTAL,
                    'oxygen_tolerance_predicted': admin.HORIZONTAL}


@admin.register(NonHydrogenaseSequence)
class NonHydrogenaseSequenceAdmin(admin.ModelAdmin):

    list_display = ('accession', 'organism', 'domain', 'phylum', 'order')


#@admin.register(GeneticOrganisation)
class GeneticOrganisationInline(admin.TabularInline):

    model = GeneticOrganisation


class StructureInline(admin.TabularInline):

    model = Structure


@admin.register(HydrogenaseClass)
class HydrogenaseClassAdmin(admin.ModelAdmin):
    list_display = ('name',)

    inlines = [
        GeneticOrganisationInline,
        StructureInline,
    ]

    fieldsets = (
        ('', {
            'fields': (('name', 'putative_class'),)
        }),
        ('Properties', {
            'fields': (('group', 'subgroup'), 'function', 'activity',
                       'oxygen_tolerance', 'localisation'),
        }),
        ('Distribution', {
            'fields': ('ecosystem_distribution', 'taxonomic_distribution',
                       'distribution_image'),
        }),
        ('Architecture', {
            'fields': ('subunits', 'subunit_description', 'catalytic_site',
                       'fes_clusters'),
        }),
        ('Notes', {
            'fields': ('notes',),
        }),
        ('Literature', {
            'fields': ('literature',),
        }),
    )
