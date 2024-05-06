from django.contrib import admin
from .models import Event
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location') # Определите, какие поля отображать в списке событий
    search_fields = ['title', 'description', 'location'] # Определите поля для поиска

admin.site.register(Event, EventAdmin)
