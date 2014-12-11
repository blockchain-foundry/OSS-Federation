from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'website/', include('pages.urls', namespace='pages')),
    url(r'issuer/', include('baseissuer.urls', namespace='baseissuer')),
)
