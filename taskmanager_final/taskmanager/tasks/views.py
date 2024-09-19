from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.detail import DetailView
from django.shortcuts import render
from .models import Task
from .forms import TaskForm, UserRegistrationForm
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView

def home(request):
    return render(request, 'home.html')

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task-list')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task-list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task-list')
    return render(request, 'task_confirm_delete.html', {'task': task})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task-list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

    class TaskDetailView(DetailView):
    model = Task
    template_name = 'task_detail.html'

def task_list(request):
    search_query = request.GET.get('q', '')
    if search_query:
        tasks = Task.objects.filter(title__icontains=search_query) | Task.objects.filter(description__icontains=search_query)
    else:
        tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})

    class UserUpdateView(UpdateView):
    model = User
    fields = ['first_name', 'email']
    template_name = 'edit_profile.html'

    @receiver(post_save, sender=Task)
def notify_task_due(sender, instance, **kwargs):
    if instance.due_date and (instance.due_date - timezone.now()).days <= 1:
        # Exibir notificação ou mensagem de alerta
        print(f'A tarefa "{instance.title}" está próxima do vencimento!')
