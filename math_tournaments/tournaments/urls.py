from django.conf.urls import url
from tournaments.views import TournamentsList, TournamentCreate, \
                              TournamentDetailed, TournamentUpdate, TournamentDelete, \
                              RoundList, RoundCreate, RoundUpdate, \
                              RoundDelete, RoundSubscribe, TaskList, \
                              TaskCreate, TaskDelete, TaskUpdate, RoundStart, \
                              TopList

urlpatterns = [
        url(r'^$', TournamentsList.as_view(), name='index'),
        url(r'^tournament/all/$', TournamentsList.as_view(), name='tour-list'),
        url(r'^tournament/create/', TournamentCreate.as_view(), name='tour-create'),
        url(r'^tournament/delete/(?P<pk>[0-9]+)/$', TournamentDelete.as_view(), name='tour-delete'),
        url(r'^tournament/update/(?P<pk>[0-9]+)/$', TournamentUpdate.as_view(), name='tour-update'),

        url(r'^tournament/(?P<owner>[0-9]+)/$', RoundList.as_view(), name='round-list'),
        url(r'^tournament/(?P<owner>[0-9]+)/create/', RoundCreate.as_view(), name='round-create'),
        url(r'^round/delete/(?P<pk>[0-9]+)/$', RoundDelete.as_view(), name='round-delete'),
        url(r'^round/update/(?P<pk>[0-9]+)/$', RoundUpdate.as_view(), name='round-update'),
        url(r'^round/subscribe/(?P<pk>[0-9]+)/$', RoundSubscribe.as_view(), name='round-subscribe'),
        
        url(r'^round/(?P<owner>[0-9]+)/$', TaskList.as_view(), name='task-list'),
        url(r'^round/(?P<owner>[0-9]+)/create/', TaskCreate.as_view(), name='task-create'),
        url(r'^task/delete/(?P<pk>[0-9]+)/$', TaskDelete.as_view(), name='task-delete'),
        url(r'^task/update/(?P<pk>[0-9]+)/$', TaskUpdate.as_view(), name='task-update'),
        
        url(r'^answer/(?P<tour>[0-9]+)/(?P<round>[0-9]+)/(?P<task>[0-9]+)/$', RoundStart.as_view(), name='task-answer'),
        url(r'^answer/(?P<tour>[0-9]+)/(?P<round>[0-9]+)/$', RoundStart.as_view(), name='round-start'),
        
        url(r'^tour/(?P<tour>[0-9]+)/top/$', TopList.as_view(), name='top-list'),
    ]
