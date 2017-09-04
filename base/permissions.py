from rest_framework.permissions import IsAuthenticated
import ipaddress
import six


class LocalOrIsAuthenticated(IsAuthenticated):
    block_proxy = True
    use_proxy_remote = True

    @staticmethod
    def is_local(ip):
        return ipaddress.ip_address(six.u(ip)).is_private

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
