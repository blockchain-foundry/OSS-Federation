from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'oss.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^create/$', views.issuer_create, name='issuer_create'),
    url(r'^(?P<pk>\d+)/delete/$', views.issuer_delete,
        name='issuer_delete'),
    url(r'^(?P<pk>\d+)/update/$', views.BaseIssuerUpdateView.as_view(),
        name='issuer_update'),
    url(r'^(?P<pk>\d+)/detail/$',
        views.BaseIssuerDetailView.as_view(),
        name='issuer_detail'),
    url(r'^(?P<issuer_pk>\d+)/add_color/$',
        views.issuer_add_color, name='issuer_add_color'),
    url(r'^issuer_list/$', views.BaseIssuerListView.as_view(), name='issuer_list'),
    url(r'^unconfirmed_issuer_list/$',
        views.UnconfirmedBaseIssuerListView.as_view(),
        name='unconfirmed_issuer_list/$'),
    url(r'^color_list/$', views.ColorListView.as_view(), name='color_list'),
    url(r'^unconfirmed_color_list/$', views.UnconfirmedColorListView.as_view(),
        name='unconfirmed_color_list'),
    url(r'^(?P<pk>\d+)/color_detail', views.ColorDetailView.as_view(),
        name='color_detail'),
)
