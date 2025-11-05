from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import UserProfile,Transaction



# Create your views here.

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        error = None
       ##validation
        if not username or not email or not password or not confirm_password:
            error = 'All fields are required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already taken.'
        elif User.objects.filter(email=email).exists():
            error = 'An account with that email already exists.'

        if error:
            return render(request, 'register.html', {'error': error, 'username': username, 'email': email})
      
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return render(request, 'login.html', {'success': 'Account created successfully! Please login.'})
        
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        error = None
        if not username or not password:
            error = 'Both username and password are required.'
        else:
            user = authenticate(request, username=username, password=password)

            if user is None:
                error = 'Invalid username or password.'
            else:
                # Login successful
                auth_login(request, user)
                return redirect('dashboard')

    

        # If there’s an error, re-render login page with error message
        return render(request, 'login.html', {'error': error, 'username': username})

    # GET request → show login form
    return render(request, 'login.html')
         

@login_required
def user_dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'user_dashboard.html', {'profile': profile})
@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            print(f"Profile picture saved: {profile.profile_picture.url}")
        
        return render(request, 'profile.html', {'success': 'Profile updated successfully!', 'user': user, 'profile': profile})
    
    return render(request, 'profile.html', {'user': request.user, 'profile': profile})





    
    
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transaction_list.html', {'transactions': transactions})