from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

urlpatterns = patterns('',
    url(r'session_security/', include('session_security.urls')),
)

urlpatterns += i18n_patterns('',
    url(r'', include('accounts.urls', namespace='accounts')),
)
