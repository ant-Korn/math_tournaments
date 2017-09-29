from datetime import datetime

from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django import http
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from tournaments.models import Tournament
from users.models import User
from tournaments.forms import TournamentCreateForm, TournamentUpdateForm


class CreateWithOwnerMixin:
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return http.HttpResponseRedirect(obj.get_absolute_url())

class UserFilterMixin:
    def get_queryset(self):
        queryset = super(UserFilterMixin, self).get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset

class PermissionRequiredMixin:
    permission = None


    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(self.permission):
            return HttpResponseForbidden()
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
    
def order(queryset, ordering=()):
    return queryset.order_by(*ordering)

class TournamentsList(LoginRequiredMixin, ListView):
        model = Tournament

class TournamentCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateWithOwnerMixin, CreateView):
    model = Tournament
    form_class = TournamentCreateForm
    permission = 'tournaments.add_tournament'


class TournamentDelete(LoginRequiredMixin, PermissionRequiredMixin, UserFilterMixin, DeleteView):
    model = Tournament
    success_url = reverse_lazy('tour-list')
    permission = 'tournaments.delete_tournament'


class TournamentUpdate(LoginRequiredMixin, PermissionRequiredMixin, UserFilterMixin, UpdateView):
    form_class = TournamentUpdateForm
    model = Tournament
    permission = 'tournaments.change_tournament'


    def post(self, *args, **kwargs):
        super(TournamentUpdate, self).post(*args, **kwargs)
        return redirect(reverse('tour-list'))


class TournamentDetailed(LoginRequiredMixin, UserFilterMixin, DetailView):
    model = Tournament

class TopList(LoginRequiredMixin, TemplateView):
    model = Tournament
    template_name = 'tournaments/tounament_top_list.html'
    param_name = 'tour'
    
    
    def get_context_data(self, *args, **kwargs):
        context = super(TopList, self).get_context_data(**kwargs)
        tour = get_object_or_404(self.model, pk=self.kwargs[self.param_name])
        top_table = tour.top_in_final()
        context['tour'] = tour
        context['top_table'] = top_table
        return context
    
