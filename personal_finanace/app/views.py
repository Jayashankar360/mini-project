from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Transaction, Category, Budget, Goal
from datetime import datetime, timedelta

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'app/index.html')

def create_default_categories(user):
    default_categories = [
        {'name': 'Food & Dining', 'description': 'Restaurants, groceries, food delivery'},
        {'name': 'Transportation', 'description': 'Gas, public transport, car maintenance'},
        {'name': 'Shopping', 'description': 'Clothing, electronics, general shopping'},
        {'name': 'Entertainment', 'description': 'Movies, games, subscriptions'},
        {'name': 'Bills & Utilities', 'description': 'Electricity, water, internet, phone'},
        {'name': 'Healthcare', 'description': 'Medical expenses, insurance, pharmacy'},
        {'name': 'Education', 'description': 'Books, courses, tuition fees'},
        {'name': 'Salary', 'description': 'Monthly salary and wages'},
        {'name': 'Freelance', 'description': 'Freelance work income'},
        {'name': 'Investments', 'description': 'Stock dividends, interest income'},
    ]
    for cat_data in default_categories:
        Category.objects.create(user=user, **cat_data)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 == password2 and username and email:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password1)
                create_default_categories(user)
                messages.success(request, 'Registration successful! Please login with your credentials.')
                return redirect('login')
            else:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Please fill all fields correctly.')
    return render(request, 'app/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'app/login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    user = request.user
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]
    total_income = Transaction.objects.filter(user=user, transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Transaction.objects.filter(user=user, transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    goals = Goal.objects.filter(user=user)
    budgets = Budget.objects.filter(user=user)
    context = {
        'recent_transactions': recent_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'goals': goals,
        'budgets': budgets,
    }
    return render(request, 'app/dashboard.html', context)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'app/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create(request):
    if not Category.objects.filter(user=request.user).exists():
        create_default_categories(request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        transaction_type = request.POST.get('transaction_type')
        date = request.POST.get('date')
        
        if amount and category_id and transaction_type:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                description=description,
                category=category,
                transaction_type=transaction_type,
                date=date or datetime.now().date()
            )
            return redirect('transaction_list')
    
    categories = Category.objects.filter(user=request.user)
    return render(request, 'app/transaction_form.html', {'categories': categories})

@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        transaction_type = request.POST.get('transaction_type')
        date = request.POST.get('date')
        
        if amount and category_id and transaction_type:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            transaction.amount = amount
            transaction.description = description
            transaction.category = category
            transaction.transaction_type = transaction_type
            transaction.date = date or transaction.date
            transaction.save()
            return redirect('transaction_list')
    
    categories = Category.objects.filter(user=request.user)
    return render(request, 'app/transaction_form.html', {'transaction': transaction, 'categories': categories})

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'app/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'app/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            Category.objects.create(
                user=request.user,
                name=name,
                description=description or ''
            )
            return redirect('category_list')
    return render(request, 'app/category_form.html')

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            category.name = name
            category.description = description or ''
            category.save()
            return redirect('category_list')
    return render(request, 'app/category_form.html', {'category': category})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'app/category_confirm_delete.html', {'category': category})

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'app/budget_list.html', {'budgets': budgets})

@login_required
def budget_create(request):
    if not Category.objects.filter(user=request.user).exists():
        create_default_categories(request.user)
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if category_id and amount and start_date and end_date:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            Budget.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                start_date=start_date,
                end_date=end_date
            )
            return redirect('budget_list')
    
    categories = Category.objects.filter(user=request.user)
    return render(request, 'app/budget_form.html', {'categories': categories})

@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'app/goal_list.html', {'goals': goals})

@login_required
def goal_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        target_amount = request.POST.get('target_amount')
        current_amount = request.POST.get('current_amount')
        deadline = request.POST.get('deadline')
        
        if name and target_amount:
            Goal.objects.create(
                user=request.user,
                name=name,
                target_amount=target_amount,
                current_amount=current_amount or 0,
                deadline=deadline
            )
            return redirect('goal_list')
    return render(request, 'app/goal_form.html')

@login_required
def goal_update(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        target_amount = request.POST.get('target_amount')
        current_amount = request.POST.get('current_amount')
        deadline = request.POST.get('deadline')
        
        if name and target_amount:
            goal.name = name
            goal.target_amount = target_amount
            goal.current_amount = current_amount or 0
            goal.deadline = deadline
            goal.save()
            return redirect('goal_list')
    return render(request, 'app/goal_form.html', {'goal': goal})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('goal_list')
    return render(request, 'app/goal_confirm_delete.html', {'goal': goal})

@login_required
def analytics(request):
    user = request.user
    monthly_expenses = Transaction.objects.filter(
        user=user, transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    income_trend = Transaction.objects.filter(
        user=user, transaction_type='income', date__range=[start_date, end_date]
    ).values('date__month').annotate(total=Sum('amount')).order_by('date__month')
    expense_trend = Transaction.objects.filter(
        user=user, transaction_type='expense', date__range=[start_date, end_date]
    ).values('date__month').annotate(total=Sum('amount')).order_by('date__month')
    context = {
        'monthly_expenses': list(monthly_expenses),
        'income_trend': list(income_trend),
        'expense_trend': list(expense_trend),
    }
    return render(request, 'app/analytics.html', context)