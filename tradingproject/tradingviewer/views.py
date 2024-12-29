from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os
import sys
from tradingviewer.logic.main import *


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def process_data_plain(request):
    data = JsonResponse(process_data())
    return HttpResponse(data)

def process_data_table(request):
    data = process_data()
    display_table(data)
    return HttpResponse(display_table(data))

def test_endpoint(request):
    main()
    return HttpResponse("Test Endpoint. Check console.")