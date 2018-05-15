from django.contrib import admin
from .models import Mot
from .models import Flexion

# admin.site.register(Mot)
# admin.site.register(Flexion)


class FlexionInline(admin.StackedInline):
    model = Flexion
    extra = 0


class MotAdmin(admin.ModelAdmin):
    mot_fields = Mot._meta.get_fields()

    # fieldsets = [
    #     (None,               {'fields': mot_fields}),
    #     ('Autre écritures masculines', {
    #      'fields': ['masculin_singulier_2', 'masculin_singulier_3', 'masculin_singulier_4'], 
    #      'classes': ['collapse in',]
    #      }),
    #     (None,               {'fields': ['masculin_singulier']}),

    # ]

    inlines = [FlexionInline]
    search_fields = ['masculin_singulier']
    list_display = ('masculin_singulier', 'masculin_pluriel',  'validation_status', 'flexion_count',)

    def flexion_count(self, obj):
        return obj.flexion_set.count()

    def validation_status(self, obj):
        pass
        # return obj.flexion_set.all()[0].validation


admin.site.register(Mot, MotAdmin)
