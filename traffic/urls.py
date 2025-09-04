# classifier/urls.py
from django.urls import path
from .views import  signup, user_login, user_logout,index,predict
from .views import control_traffic_light,upload_image,dashboard, process_all_traffic_images

urlpatterns = [
    
    # path('signup/', signup, name='signup'),
    # path('login/', user_login, name='login'),
    path('', index, name='index'),
    path('predict/', predict, name='predict'),
    # path('logout/', user_logout, name='logout'),
    path('control-traffic-light/', control_traffic_light, name='control_traffic_light'),
    path('upload-image/', upload_image, name='upload_image'),
    # path('dashboard/', dashboard, name='dashboard'),
    path('images/', process_all_traffic_images, name='process_all_traffic_images'),
]
