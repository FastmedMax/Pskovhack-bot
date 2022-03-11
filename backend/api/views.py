from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .models import Case, Event, Callback

from .serializers import CaseSerializer, EventSerializer, CallbackSerializer


# Create your views here.
