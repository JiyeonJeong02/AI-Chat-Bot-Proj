from django.urls import path
from . import views_main
from . import views_chatbot
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index/', views_main.dashboard_view, name='index'),
    path('tmp/', views_main.dashboard_view_practice, name='tmp'),
    path('tmp_origin/', views_main.dashboard_view_practice2, name='tmp_origin'),
    path('chatbot/send/', views_chatbot.chatbot_response, name='chatbot_send'),
    path('chatbot/history/', views_chatbot.get_chat_history, name='chat_history'),
    path('chatbot/init/', views_chatbot.initialize_chat_session, name='init_chat'),
    path('chatbot/sessions/', views_chatbot.get_chat_sessions, name='chat_sessions'),
    path('chatbot/messages/<str:session_id>/', views_chatbot.get_session_messages, name='session_messages'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
