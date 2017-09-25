
from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.contrib.auth.views import login, logout

from users.views import CreateUser, UpdateUser, ProfileUser
from users.forms import AuthForm

urlpatterns = [
        url(r'^registration', CreateUser.as_view(), name='create-user'),
        url(r'^login', login, {'authentication_form': AuthForm,
            'template_name': 'login.html'}, name='login'),
        url(r'^logout', logout, {'next_page': reverse_lazy('login')}, name='logout_pg'),
        url(r'^update$', UpdateUser.as_view(), name='update-user'),
        url(r'^profile$', ProfileUser.as_view(), name='profile-user'),
]
