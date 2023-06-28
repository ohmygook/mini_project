# URL 패턴 정의 위해 import path
from django.urls import path

# views.py에 있는 뷰 함수 정의하기 위해 현재 모듈에(='.') import views
from . import views

# '/'과 함께 사용하여 views 함수 호출
# /board => views.board
urlpatterns = [
    path('',views.home, name='home'),
    path('board',views.board,name="board"),
    path('board_write', views.board_write, name="board_write"),
    path('board_insert', views.board_insert, name="board_insert"),
    path('board_view', views.board_view, name="board_view"),
    path('board_edit', views.board_edit, name="board_edit"),
    path('board_update', views.board_update, name="board_update"),
    path('board_delete', views.board_delete, name="board_delete"),

] 