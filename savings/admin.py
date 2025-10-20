from cProfile import Profile

from django.contrib import admin
from django.contrib.auth.models import Group

from .models import *

admin.site.register(Member)
admin.site.register(Expense)
admin.site.register(Contribution)

# Register your models here.
