import django


from django.urls import path
from .views import taskList, TaskDetail, TaskCreate, TaskUpdate, DeleteTask

urlpatterns = [
    path('', taskList.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteTask.as_view(), name='task-delete'),


]