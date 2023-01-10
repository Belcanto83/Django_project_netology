from django.shortcuts import redirect
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement, AdvertisementStatusChoices
from advertisements.pagination import AdvertisementPagination
from advertisements.permissions import IsOwnerOrReadOnly
from advertisements.serializers import AdvertisementSerializer


def index(request):
    return redirect('admin/')


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    # настраиваем ViewSet, указываем атрибуты для кверисета, сериализаторов, фильтров и паджинатора
    queryset = Advertisement.objects.order_by('-updated_at')
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    pagination_class = AdvertisementPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return Advertisement.objects.order_by('-updated_at')
            # combined_queryset = Advertisement.objects.exclude(status=AdvertisementStatusChoices.DRAFT) | \
            #                     Advertisement.objects.filter(creator=user)
            combined_queryset = Advertisement.objects.filter(~Q(status=AdvertisementStatusChoices.DRAFT) |
                                                             Q(creator=user))
            # print(combined_queryset.query)
            return combined_queryset.order_by('-updated_at')
        return Advertisement.objects.exclude(status=AdvertisementStatusChoices.DRAFT).order_by('-updated_at')

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return []

    @action(methods=['POST', 'PUT', 'PATCH'], detail=True)
    def add_to_favorites(self, request, pk=None):
        advertisement = self.get_object()
        user = request.user
        if user.is_authenticated:
            if user == advertisement.creator:
                return Response({"detail": "it's impossible to add to favorites your own advertisement"},
                                status=status.HTTP_403_FORBIDDEN)
            user.favorite_advertisements.add(advertisement)
            return Response({"detail": "ok"})
        return Response({"detail": "authentication credentials were not provided"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False)
    def show_favorites(self, request):
        user = request.user
        if user.is_authenticated:
            favorite_advertisements = user.favorite_advertisements
            serializer = self.get_serializer(favorite_advertisements, many=True)
            return Response(serializer.data)
        return Response({"detail": "authentication credentials were not provided"}, status=status.HTTP_403_FORBIDDEN)
