"""定义learning_log的url模式"""

from django.urls import path

from . import views

app_name = 'learning_logs'
urlpatterns = [
    # 主页
    path('', views.predict, name='predict'),
    # 显示所有主题的页面
]