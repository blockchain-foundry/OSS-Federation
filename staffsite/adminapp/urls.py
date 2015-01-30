from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from axes.decorators import watch_login

from .forms import AdminappAuthenticationForm
from . import views
from utils.decorators import staff_required

urlpatterns = patterns('',
    url(r'^set_language/$', views.set_language, name='set_language'),
    url(r'^$', views.index, name='index'),
    url(r'^login/', watch_login(login),
        dict(template_name="adminapp/login.html",
             authentication_form=AdminappAuthenticationForm),
        name='login'),
    url(r'^logout/$', logout,
        dict(next_page='/adminapp/login'), name='logout'),
    url(r'^issuer_list/', staff_required(views.AdminIssuerListView.as_view()),
        name='issuer_list'),
    url(r'^unconfirmed_issuer_list/',
        staff_required(views.AdminUnconfirmedIssuerListView.as_view()),
        name='unconfirmed_issuer_list'),
    url(r'^issuer_create/$', views.admin_issuer_create,
        name='issuer_create'),
    url(r'^issuer_detail/(?P<pk>\d+)/$',
        staff_required(views.AdminIssuerDetailView.as_view()),
        name='issuer_detail'),
    url(r'^issuer_update/(?P<pk>\d+)/$',
        staff_required(views.AdminIssuerUpdateView.as_view()),
        name='issuer_update'),
    url(r'^issuer_delete/(?P<pk>\d+)/$',
        views.admin_issuer_delete,
        name='issuer_delete'),
    url(r'issuer_accept/(?P<pk>\d+)/$',
        views.admin_issuer_accept,
        name='issuer_accept'),
    url(r'^(?P<pk>\d+)/add_color/$', views.admin_issuer_add_color,
        name='issuer_add_color'),
    url(r'^color_list/$', staff_required(views.AdminColorListView.as_view()),
        name='color_list'),
    url(r'^unconfirmed_color_list/$',
        staff_required(views.AdminUnconfirmedColorListView.as_view()),
        name='unconfirmed_color_list'),
    url(r'^color_detail/(?P<pk>\d+)/$',
        staff_required(views.AdminColorDetailView.as_view()),
        name='color_detail'),
    url(r'^color_reject/(?P<pk>\d+)/$',
        views.admin_color_reject,
        name='color_reject'),
    url(r'^color_accept/(?P<pk>\d+)/$',
        views.admin_color_accept,
        name='color_accept'),
    url(r'^txs_list/$', views.txs_list, name='txs_list'),
    url(r'^tx/$', views.tx, name='tx'),
    url(r'^tx/(?P<tx_id>.+)$', views.tx, name='tx'),
    url(r'^alliance_list/$', views.admin_alliance_list, name='alliance_list'),
)
