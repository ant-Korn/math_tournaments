
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from users.models import User
from users.forms import UserForm
from users.forms import UserUpdateForm

class LoginAfterFormValidMixin:
    def form_valid(self, form):
        super(LoginAfterFormValidMixin, self).form_valid(form)
        new_user = authenticate(username=form.cleaned_data['email'],
                                password=form.cleaned_data['password']
                               )
        login(self.request, new_user)
        return http.HttpResponseRedirect(reverse_lazy('profile-user'))


class CreateUser(LoginAfterFormValidMixin, CreateView):
    template_name = 'registrate.html'
    form_class = UserForm
    success_url = reverse_lazy('tournaments-list')
    model = User

class UpdateUser(LoginRequiredMixin, LoginAfterFormValidMixin, UpdateView):
    template_name = 'update_user.html'
    form_class = UserUpdateForm
    model = User
    success_url = reverse_lazy('tournaments-list')

    def get_object(self, queryset=None):
        return self.request.user

class ProfileUser(LoginRequiredMixin, DetailView):
    template_name = 'profile.html'
    model = User

    def get_object(self, queryset=None):
        return self.request.user
