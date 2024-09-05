from django.urls import path

from .views import MessagesViewInbox,SendMessagesView,MessagesListView,DialogsListView



urlpatterns = [
    path('messages/inbox/', MessagesViewInbox.as_view(),name='messages_inbox'),
    path('messages/dialogs/', DialogsListView.as_view(), name='messages_dialogs'),
    path('messages/send/', SendMessagesView.as_view(),name='messages_send'),
    path('messages/detail/<int:receiver_id>/', MessagesListView.as_view(),name='messages_detail'),

]
