from django.urls import path

from . import views

urlpatterns = [
    path('health', views.health, name='health'),
    path('diagrams/load', views.diagram_load, name='diagram-load'),
    path('diagrams/save', views.diagram_save, name='diagram-save'),
    path('diagrams/list', views.diagram_list, name='diagram-list'),
    path('diagrams/validate', views.diagram_validate, name='diagram-validate'),
    path('diagrams/render', views.diagram_render, name='diagram-render'),
]
