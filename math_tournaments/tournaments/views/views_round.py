from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django import http
from django.http.response import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum

from tournaments.models import Round, Tournament, Task, Answer
from tournaments.forms import RoundForm

class CreateWithOwnerMixin:
    param_name = 'owner'
    kwargs = {}
    OwnerModel = None
    
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.tournament = get_object_or_404(self.OwnerModel, pk=self.kwargs[self.param_name])
        obj.save()
        return http.HttpResponseRedirect(obj.get_absolute_url())

class FilterMixin:
    lookup = ''
    param_name = ''
    kwargs = {}

    def get_queryset(self):
        filter_dict = {self.lookup: self.kwargs[self.param_name]}
        queryset = super(FilterMixin, self).get_queryset()
        queryset = queryset.filter(**filter_dict)
        return queryset

class TourUserFilterMixin:
    def get_queryset(self):
        queryset = super(TourUserFilterMixin, self).get_queryset()
        queryset = queryset.filter(tournament__owner=self.request.user)
        return queryset

class PermissionRequiredMixin:
    permission = None


    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perms(self.permission):
            return HttpResponseForbidden()
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)

class RoundList(LoginRequiredMixin, FilterMixin, ListView):
    model = Round
    lookup = 'tournament'
    param_name = 'owner'
    
    
    def get_context_data(self, **kwargs):
        context = super(RoundList, self).get_context_data(**kwargs)
        tour = get_object_or_404(Tournament, pk=self.kwargs[self.param_name])
        context['tour'] = tour
        top_table, user_row = tour.top_in_final(), 'user__id'
        context['top_users'] = (i[user_row] for i in top_table)
        return context

class RoundCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateWithOwnerMixin, CreateView):
    model = Round
    OwnerModel = Tournament
    form_class = RoundForm
    permission = ('tournaments.add_round',)
    param_name = 'owner'
    
    
    def dispatch(self, request, *args, **kwargs):
        tour = get_object_or_404(Tournament, pk=self.kwargs[self.param_name])
        if not tour.owner == request.user:
            return HttpResponseForbidden()
        return super(RoundCreate, self).dispatch(request, *args, **kwargs)

class RoundDelete(LoginRequiredMixin, PermissionRequiredMixin, TourUserFilterMixin, DeleteView):
    model = Round
    success_url = None
    permission = ('tournaments.delete_round',)
    
    
    def get_success_url(self):
        self.success_url = reverse_lazy('round-list', kwargs={'owner': self.object.tournament.pk})
        return super(RoundDelete, self).get_success_url()

class RoundUpdate(LoginRequiredMixin, PermissionRequiredMixin, TourUserFilterMixin, UpdateView):
    form_class = RoundForm
    model = Round
    permission = ('tournaments.change_round',)

    
    def post(self, *args, **kwargs):
        super(RoundUpdate, self).post(*args, **kwargs)
        return redirect(reverse('round-list', kwargs={'owner': self.object.tournament.pk}))
    
class RoundSubscribe(LoginRequiredMixin, TemplateView):
    template_name = 'tournaments/round_confirm_subscribe.html'
    param_name = 'pk'
    
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RoundSubscribe, self).dispatch(request, *args, **kwargs)
    
    @method_decorator(transaction.atomic)
    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(Round, pk=self.kwargs[self.param_name])
        response = reverse_lazy('round-list', kwargs={'owner': obj.tournament.pk})
        top_users, user_row = obj.tournament.top_in_final(), 'user__id'
        top_users = (i[user_row] for i in top_table)
        if not obj.subscribe_available:
            return HttpResponseForbidden()
        elif request.user not in obj.subscribers.all() and \
             ((obj.typization != Round.FINAL) or \
             (request.user.pk in top_users)):
            obj.subscribers.add(request.user)
            obj.save()
        return redirect(response)
    
    def get_context_data(self, *args, **kwargs):
        context = super(RoundSubscribe, self).get_context_data(**kwargs)
        context['object'] = get_object_or_404(Round, pk=self.kwargs[self.param_name])
        return context

class RoundStart(LoginRequiredMixin, FilterMixin, ListView):
    model = Task
    lookup = 'round'
    param_name = 'round'
    template_name = 'tournaments/round_start.html'
    
    
    def get_context_data(self, *args, **kwargs):
        context = super(RoundStart, self).get_context_data(**kwargs)
        context['tour'] = self.kwargs['tour']
        context['round'] = self.kwargs['round']
        context['score'] = Answer.objects.filter(user=self.request.user,
                                                 correctness=True,
                                                 task__round_id=context['round']).aggregate(sum=Sum('task__score'))['sum']
        return context
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        round = get_object_or_404(Round, pk=kwargs['round'])
        if not round.subscribers.filter(pk=request.user.pk).exists() or not round.in_progress:
            return HttpResponseForbidden()
        return super(RoundStart, self).dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super(RoundStart, self).get_queryset()
        queryset = queryset.exclude(user_answer__id=self.request.user.pk)
        return queryset
    
    @method_decorator(transaction.atomic)
    def post(self, request, tour, round, task, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        answer = request.POST.get('answer-{0}-{1}-{2}'.format(tour, round, task), None)
        if answer is None:
            print('answer-{0}-{1}-{2}'.format(tour, round, task))
            print(request.POST)
            return self.render_to_response(context, **kwargs)
        task = get_object_or_404(Task, pk=task)
        if task.user_answer.filter(pk=request.user.pk).exists():
            return self.render_to_response(context, **kwargs)
        correctness = task.check_answer(answer)
        answer_obj = Answer.objects.create(user=request.user, task=task, correctness=correctness)
        answer_obj.save()
        context = self.get_context_data()
        return self.render_to_response(context, **kwargs)
