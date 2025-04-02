from datetime import timezone
from django.utils import timezone
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.db.models import Q
from .models import Todo
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages 
from .forms import LoginForm, SignupForm, TodoForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from .forms import SignupForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView


current_time = timezone.now()

class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'index.html'
    context_object_name = 'todos'   
    paginate_by = 5
    login_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to view this page.")
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # queryset = Todo.objects.all()
        queryset = Todo.objects.filter(user=self.request.user).order_by('-created_at')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        filter_option = self.request.GET.get('filter', 'all')  
        if filter_option == 'upcoming':
            queryset = queryset.filter(start_date__gte=timezone.now())
        elif filter_option == 'completed':
            queryset = queryset.filter(completed=True)
        elif filter_option == 'pending':
            queryset = queryset.filter(completed=False)

        return queryset


class TodoDashboardView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'add_todo.html'  
    context_object_name = 'todos'
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_tasks'] = Todo.objects.count()
        context['completed_tasks'] = Todo.objects.filter(completed=True).count()
        context['pending_tasks'] = Todo.objects.filter(completed=False).count()
        return context
    

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm 
    template_name = 'add_todo.html'
    # fields = ['title', 'description', 'start_date', 'end_date']
    success_url = reverse_lazy('todo_list')
    login_url = "/login/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Your Todo has been added successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding your Todo. Please try again.")
        return super().form_invalid(form)
    
    

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'update_todo.html'
    success_url = reverse_lazy('todo_list')
    login_url = "/login/"

    def form_valid(self, form):
        todo = form.save(commit=False)  # Ensure object updates properly
        todo.save()
        messages.success(self.request, "Todo updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "End date cannot be earlier than start date. Please try again.")
        return super().form_invalid(form)


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'delete_todo.html'
    success_url = reverse_lazy('todo_list') 
    login_url = "/login/"



class MarkCompletedView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk):
        todo = Todo.objects.get(pk=pk)
        todo.completed = True
        todo.save()
        return redirect('todo_list')

class MarkPendingView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk):
        todo = Todo.objects.get(pk=pk)
        todo.completed = False  
        todo.save()
        return redirect('todo_list')
    
class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already SingIN in!")
            return redirect('todo_list')
        form = SignupForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if User.objects.filter(email=email).exists():
                return render(request, 'signup.html', {'form': form, 'error': 'Email already exists'})

            # Auto-generate username from email
            username = email.split('@')[0]

            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            user.is_active = False  # Deactivate user until email is verified
            user.save()

            # Send Email Verification
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email_message = EmailMessage(subject, message, to=[email])
            email_message.send()

            return render(request, 'email_sent.html')

        return render(request, 'signup.html', {'form': form})
    

class ActivateView(View):
    def get(self, request, uidb64, token):
        print(f"Received activation request: uidb64={uidb64}, token={token}")  # Debugging

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            print(f"Decoded UID: {uid}")  # Debugging
            
            user = User.objects.get(pk=uid)
            print(f"User found: {user}")  # Debugging

            if user is not None and default_token_generator.check_token(user, token):
                user.is_active = True  # Activate the user
                user.save()
                print("User successfully activated!")  # Debugging
                
                return render(request, 'account_activated.html')

            print("Invalid token or user already activated")  # Debugging
            return render(request, 'activation_failed.html', {'error': 'Invalid or expired activation link.'})

        except Exception as e:
            print(f"Activation Error: {e}")  # Debugging
            return render(request, 'activation_failed.html', {'error': 'Invalid activation link.'})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect(reverse_lazy('todo_list')) 
        
        form = LoginForm()  
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None  # No user found

            if user is not None:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect(reverse_lazy('dashboard')) # Redirect to dashboard
                    else:
                        messages.error(request, "Verify your email first")
                else:
                    messages.error(request, "Invalid password")  
            else:
                messages.error(request, "User does not exist")  

        return render(request, 'login.html', {'form': form})


class ResendVerificationView(View):
    def get(self, request):
        # Get the latest registered user who is NOT active
        user = User.objects.filter(is_active=False).order_by('-date_joined').first()

        if user:
            # Generate email confirmation link
            current_site = get_current_site(request)
            subject = 'Resend Activation Email'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email_message = EmailMessage(subject, message, to=[user.email])
            email_message.send()

            messages.success(request, f"Verification email resent to {user.email}.")
        else:
            messages.error(request, "No unverified users found.")

        return redirect("login")  # Redirect to login page after resending email
    

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        messages.success(self.request, "You have been logged out successfully.")
        return "/login/" 
    

class PageView(TemplateView):
    template_name = 'desbord.html'
    def get_context_data(self, **kwargs):
        all_count = Todo.objects.count()
        completed_count = Todo.objects.filter(completed=True).count()
        pending_count = Todo.objects.filter(completed=False).count()
        upcoming_count = Todo.objects.filter(start_date__gt=timezone.now()).count()

        context = super().get_context_data(**kwargs)
        context['all_count'] = all_count
        context['completed_count'] = completed_count
        context['pending_count'] = pending_count
        context['upcoming_count'] = upcoming_count

        return context
    
        