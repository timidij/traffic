# classifier/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from .models import TrafficLight
from .utils import get_prediction_result,get_traffic_demand,predict_image
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

import json
import cv2
import numpy as np
import base64
import uuid
from datetime import datetime



from django.core.files.storage import FileSystemStorage
from .forms import ImageUploadForm
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            # Here you can add your image processing logic
            return redirect('upload_image')  # Redirect to the same page or another page
    else:
        form = ImageUploadForm()
    return render(request, 'classifier/upload_image.html', {'form': form})


from django.contrib.auth.models import User
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user with the provided email and password
            return redirect('index')  # Redirect to the index page after signup
    else:
        form = SignupForm()
    return render(request, 'classifier/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirect to the index page after login
            else:
                return render(request, 'classifier/login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'classifier/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

def control_traffic_light(request):
    traffic_light = TrafficLight.objects.first()  # Get the first traffic light instance
    if request.method == 'POST':
        new_state = request.POST.get('state')
        if new_state in dict(TrafficLight.STATE_CHOICES):
            traffic_light.state = new_state
            traffic_light.save()
            return redirect('control_traffic_light')  # Redirect to the same page to see the updated state
    return render(request, 'classifier/control_traffic_light.html', {'traffic_light': traffic_light})

def dashboard(request):
    return render(request, 'classifier/dashboard.html')


def index(request):
    return render(request, 'classifier/index.html')

def predict(request):
    # """Handle image prediction requests for multiple images"""
    if request.method == 'POST' and request.FILES:
        uploaded_images = request.FILES.getlist('images') # Get all uploaded files
        
        if len(uploaded_images) != 4:
            return JsonResponse({'error': 'Please upload exactly 4 images for the intersection (North, South, East, West).'}, status=400)

        directions = ['north', 'south', 'east', 'west']
        
        individual_predictions = {}
        for i, image_file in enumerate(uploaded_images):
            direction = directions[i]
            img_bytes = image_file.read()
            
            prediction_result = get_prediction_result(img_bytes)
            
            if prediction_result is None:
                # Ensure 'image' key is always present, even for errors, to prevent frontend issues
                individual_predictions[direction] = {'class': 'error', 'confidence': 0, 'filename': image_file.name, 'image': ''}
            else:
                prediction_result['filename'] = image_file.name
                individual_predictions[direction] = prediction_result
        
        # Get the simplified traffic demand booleans
        traffic_demand_booleans = get_traffic_demand(individual_predictions)

        response_data = {
            'individual_predictions': individual_predictions,
            'traffic_demand': traffic_demand_booleans # This is what the frontend will use for logic
        }
            
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)