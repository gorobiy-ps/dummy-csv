"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from dummy import views

urlpatterns = [
    re_path(r'^edit_schema/(?P<schema_id>\d+)/', views.edit_schema, name="edit_schema"),
    re_path(r'^new_schema', views.new_schema, name="new_schema"), # (?P<param_name>reg_exp)
    path('admin/', admin.site.urls),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('page_404', views.page_404, name='page_404'),
    path('my_schemes', views.my_schemes, name='my_schemes'),
    path('my_datasets', views.my_datasets, name='my_datasets'),
    path('download_file/<str:f_name>', views.download_file, name='download_file'),
    path('put_csv', views.put_csv, name='put_csv'),
    path('check_task_status', views.check_task_status, name='check_task_status'),
    path('get_snippet', views.get_snippet, name='get_snippet'),
    path('', views.index, name='home'),

]
