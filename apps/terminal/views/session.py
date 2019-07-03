# -*- coding: utf-8 -*-
#

from django.views.generic import ListView
from django.views.generic.edit import SingleObjectMixin
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

from common.permissions import PermissionsMixin, IsOrgAdmin, IsAuditor
from common.mixins import DatetimeSearchMixin
from ..models import Session, Command, Terminal
from ..backends import get_multi_command_storage
from .. import utils


__all__ = [
    'SessionOnlineListView', 'SessionOfflineListView',
    'SessionDetailView',
]


class SessionListView(PermissionsMixin, DatetimeSearchMixin, ListView):
    model = Session
    template_name = 'terminal/session_list.html'
    context_object_name = 'session_list'
    paginate_by = settings.DISPLAY_PER_PAGE
    user = asset = system_user = ''
    date_from = date_to = None
    permission_classes = [IsOrgAdmin | IsAuditor]

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.user = self.request.GET.get('user')
        self.asset = self.request.GET.get('asset')
        self.system_user = self.request.GET.get('system_user')

        filter_kwargs = dict()
        filter_kwargs['date_start__gt'] = self.date_from
        filter_kwargs['date_start__lt'] = self.date_to
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'asset_list': utils.get_session_asset_list()[:10],
            'date_from': self.date_from,
            'date_to': self.date_to,
            'user': self.user,
            'asset': self.asset,
            'system_user': self.system_user,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class SessionOnlineListView(SessionListView):

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_finished=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Sessions'),
            'action': _('Session online list'),
            'type': 'online',
            'now': timezone.now(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class SessionOfflineListView(SessionListView):

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_finished=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Sessions'),
            'action': _('Session offline'),
            'now': timezone.now(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class SessionDetailView(SingleObjectMixin, PermissionsMixin, ListView):
    template_name = 'terminal/session_detail.html'
    model = Session
    object = None
    permission_classes = [IsOrgAdmin | IsAuditor]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        command_store = get_multi_command_storage()
        return command_store.filter(session=self.object.id)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Sessions'),
            'action': _('Session detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

