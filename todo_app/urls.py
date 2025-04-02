from django.urls import path
from .views import ActivateView, LoginView, MarkPendingView, ResendVerificationView, SignupView, TodoListView, TodoCreateView, TodoUpdateView, TodoDeleteView, MarkCompletedView , CustomLogoutView, PageView
from todo_app import views

urlpatterns = [
    path('todolist/',TodoListView.as_view(), name='todo_list'),
    path('add/', TodoCreateView.as_view(), name='add_todo'),
    path('update/<int:pk>/', TodoUpdateView.as_view(), name='update_todo'),
    path('delete/<int:pk>/', TodoDeleteView.as_view(), name='delete_todo'),
    path('mark_completed/<int:pk>/',MarkCompletedView.as_view(), name='mark_completed'),
    path('mark_pending/<int:pk>/', MarkPendingView.as_view(), name='mark_pending'),
    
    path('signup/', SignupView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
    path('', LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', PageView.as_view(), name='dashboard'),

]



