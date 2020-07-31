from django.contrib import admin
from .models import City, Language, Vacancy, Error, Url


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company')
    list_filter = ('timestamp', 'title', "company",)
    search_fields = ('title', "company",)
    #prepopulated_fields = {'slug': ('title',)}

admin.site.register(Error)

@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = ('url_data',)
