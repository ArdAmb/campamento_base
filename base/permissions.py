# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ipaddress
import six
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class LocalOrIsAuthenticated(IsAuthenticated):
    block_proxy = True
    use_proxy_remote = False

    def __init__(self):
        IsAuthenticated.__init__(self)
        if hasattr(settings, 'READ_PROXY_IP') and settings.READ_PROXY_IP:
            self.use_proxy_remote = True
            self.block_proxy = False
        if hasattr(settings, 'ALLOW_PROXY'):
            self.block_proxy = not settings.ALLOW_PROXY

    @staticmethod
    def is_local(ip):
        if not isinstance(ip, unicode):
            ip = six.u(ip)
        net_ip = ipaddress.ip_address(ip)
        if hasattr(settings, 'LOCAL_NETWORK'):
            local_net = settings.LOCAL_NETWORK
            if not isinstance(local_net, unicode):
                local_net = six.u(local_net)
            net = ipaddress.ip_network(local_net)
            return net_ip in net.hosts()
        return net_ip.is_private

    @staticmethod
    def is_proxy(request):
        proxy = False
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            proxy = request.META.get('HTTP_X_FORWARDED_FOR').split(',', 1)[0]
        return proxy

    def has_permission(self, request, view):
        remote_ip = request.META.get('REMOTE_ADDR')
        real_ip = LocalOrIsAuthenticated.is_proxy(request)
        if self.block_proxy and real_ip:
            return False
        elif self.use_proxy_remote and real_ip:
            remote_ip = real_ip
        if self.is_local(remote_ip):
            return True
        return IsAuthenticated.has_permission(self, request, view)
