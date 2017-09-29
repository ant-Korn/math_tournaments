from django.contrib import admin
from .models import Tournament, Round, Task, Answer
# Register your models here.
admin.site.register(Tournament, admin.ModelAdmin)
admin.site.register(Round, admin.ModelAdmin)
admin.site.register(Task, admin.ModelAdmin)
admin.site.register(Answer, admin.ModelAdmin)


