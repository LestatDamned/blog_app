from django.urls import path

from .views import MessagesViewInbox,MessagesViewSent,SendMessagesView,MessagesDetailView



urlpatterns = [
    path('messages/inbox/', MessagesViewInbox.as_view(),name='messages_inbox'),
    path('messages/sent/', MessagesViewSent.as_view(),name='messages_sent'),
    path('messages/send/', SendMessagesView.as_view(),name='messages_send'),
    path('messages/detail/<int:pk>/', MessagesDetailView.as_view(),name='messages_detail'),

]
