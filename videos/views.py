from django.http import JsonResponse
from rest_framework import generics
from .models import Videos
from .serializers import VideoSerializer
from rest_framework.permissions import IsAuthenticated

def VideoUpload(request):
    pass

def VideoList(request):
    videos = Videos.objects.all()
    serializer = VideoSerializer(videos, many=True)
    return JsonResponse(serializer.data, safe=False)
