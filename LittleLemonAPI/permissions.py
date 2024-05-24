from rest_framework.permissions import BasePermission


class IsAuthorizedGroup(BasePermission):
    groups: list[str]

    def has_permission(self, request, *args, **kwargs):
        return in_group(request, self.groups)


class IsManager(IsAuthorizedGroup):
    groups = ["Manager"]


class IsDeliveryCrew(BasePermission):
    groups = ["Delivery Crew"]


def in_group(request, groups: list[str]):
    return request.user.groups.filter(name__in=groups)


def is_manager(request):
    return in_group(request, ["Manager"])


def is_delivery_crew(request):
    return in_group(request, ["Delivery Crew"])
