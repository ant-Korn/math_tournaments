from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django import http
from django.http.response import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q

from tournaments.models import Round, Tournament, Task
from .views_round import FilterMixin, PermissionRequiredMixin
from tournaments.forms import TaskForm


class TourUserFilterMixin:
    def get_queryset(self):
        queryset = super(TourUserFilterMixin, self).get_queryset()
        queryset = queryset.filter(round__tournament__owner=self.request.user)
        return queryset

class CreateWithOwnerMixin:
    param_name = 'owner'
    kwargs = {}
    OwnerModel = None


    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.round = get_object_or_404(self.OwnerModel, pk=self.kwargs[self.param_name])
        obj.save()
        return http.HttpResponseRedirect(obj.get_absolute_url())

class TaskList(LoginRequiredMixin, PermissionRequiredMixin, FilterMixin, ListView):
    model = Task
    lookup = 'round'
    param_name = 'owner'
    permission = ('tournaments.add_task',
                  'tournaments.delete_task',
                  'tournaments.change_task')
    
        
    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        round = get_object_or_404(Round, pk=self.kwargs[self.param_name])
        context['round'] = round
        return context
    
class TaskCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateWithOwnerMixin, CreateView):
    model = Task
    OwnerModel = Round
    form_class = TaskForm
    permission = ('tournaments.add_task',)
    param_name = 'owner'
    
    
    def dispatch(self, request, *args, **kwargs):
        round = get_object_or_404(Round, pk=self.kwargs[self.param_name])
        if not round.tournament.owner == request.user:
            return HttpResponseForbidden()
        return super(TaskCreate, self).dispatch(request, *args, **kwargs)

class TaskDelete(LoginRequiredMixin, PermissionRequiredMixin, TourUserFilterMixin, DeleteView):
    model = Task
    success_url = None
    permission = ('tournaments.delete_task',)
    
    
    def get_success_url(self):
        self.success_url = reverse_lazy('task-list', kwargs={'owner': self.object.round.pk})
        return super(TaskDelete, self).get_success_url()

class TaskUpdate(LoginRequiredMixin, PermissionRequiredMixin, TourUserFilterMixin, UpdateView):
    form_class = TaskForm
    model = Task
    permission = 'tournaments.change_task'


    def post(self, *args, **kwargs):
        super(TaskUpdate, self).post(*args, **kwargs)
        return redirect(reverse('task-list', kwargs={'owner': self.object.round.pk}))
