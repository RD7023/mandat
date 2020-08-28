from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse
from django.core import serializers
from django.conf import settings

import json

from MyApp.find_optimal import *

@api_view(['POST'])
def hello_world(request):
    if request.method == 'POST':
        min_dev, best, best_arr = get_opt(request.data)
        res = Response({"message": "Got some data!", "data": best, 'Access-Control-Allow-Origin': "*"})
        res['Access-Control-Allow-Origin'] = "*"
        res['Access-Control-Allow-Methods'] = "DELETE, POST, GET, OPTIONS"
        return res
    return Response({"message": "Hello, world!"})



# Create your views here.
