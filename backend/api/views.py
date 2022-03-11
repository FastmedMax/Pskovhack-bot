from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .models import Case, Event, Callback

from .serializers import CaseSerializer, EventSerializer, CallbackSerializer


# Create your views here.
class CaseViewset(viewsets.GenericViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def retrieve(self, request, pk=None):
        case = self.get_object()
        serializer = self.serializer_class(case)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        cases = self.queryset.values_list("id", "title")
        return Response(cases, status=status.HTTP_200_OK)


class EventViewset(viewsets.GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def retrieve(self, request, pk=None):
        event = self.get_object()
        serializer = self.serializer_class(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        events = self.queryset.values_list("id", "title")
        return Response(events, status=status.HTTP_200_OK)


class CallbackViewset(viewsets.GenericViewSet):
    queryset = Callback.objects.all()
    serializer_class = CallbackSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
