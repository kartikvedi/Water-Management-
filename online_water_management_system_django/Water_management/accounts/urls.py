from django.conf.urls import url
from .views import login_user, logout_user, register_user, register_corporate

urlpatterns = [
    url(r'^login/$', login_user, name='LogIn'),
    url(r'^logout/$', logout_user),
    url(r'^register-customer/$', register_user),
    url(r'^register-corporate/$', register_corporate),

]
