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
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
