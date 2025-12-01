from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Transaction, Category, Budget, Goal,UserProfile
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Sum
from django.core.mail import send_mail
import random
import json





# Create your views here.


def index(request):
    return render(request, 'index.html')
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 == password2 and username and email:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password1)
                # Create default categories for new user
                default_categories = [
                    'Food & Dining', 'Transportation', 'Housing', 'Utilities', 'Entertainment',
                    'Healthcare', 'Shopping', 'Education', 'Travel', 'Insurance', 'Salary',
                    'Freelance', 'Business', 'Investment', 'Other Income', 'Miscellaneous'
                ]
                for cat_name in default_categories:
                    Category.objects.create(user=user, name=cat_name, description='')
                messages.success(request, 'Registration successful! Please login with your credentials.')
                return redirect('login')
            else:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Please fill all fields correctly.')
    return render(request, 'register.html')


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
    return render(request, 'login.html')

@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expenses
    recent_transactions = transactions.order_by('-date')[:2]
    recent_goals = Goal.objects.filter(user=request.user).order_by('-id')[:2]
    recent_budgets = Budget.objects.filter(user=request.user).order_by('-id')[:2]
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'recent_goals': recent_goals,
        'recent_budgets': recent_budgets,
    }
    return render(request, 'dashboard.html', context)

def user_logout(request):
    logout(request)
    # After logout, redirect to the public index page
    return redirect('index')

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transaction_list.html', {'transactions': transactions})

# ✅ View: Add a new transaction
@login_required
def add_transaction(request):
    # Create default categories if user has none
    if not Category.objects.filter(user=request.user).exists():
        default_categories = [
            'Food & Dining', 'Transportation', 'Housing', 'Utilities', 'Entertainment',
            'Healthcare', 'Shopping', 'Education', 'Travel', 'Insurance', 'Salary',
            'Freelance', 'Business', 'Investment', 'Other Income', 'Miscellaneous'
        ]
        for cat_name in default_categories:
            Category.objects.create(user=request.user, name=cat_name, description='')

    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category_name = request.POST.get('category_name')
        transaction_type = request.POST.get('transaction_type')
        date_str = request.POST.get('date')

        if not amount or not description or not category_name or not transaction_type:
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'transaction_form.html', {'categories': categories})

        try:
            amount = Decimal(amount)
        except ValueError:
            messages.error(request, 'Invalid amount.')
            return render(request, 'transaction_form.html', {'categories': categories})

        category = None
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name, user=request.user)

        transaction_date = timezone.now().date()
        if date_str:
            try:
                transaction_date = date.fromisoformat(date_str)
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return render(request, 'transaction_form.html', {'categories': categories})

        Transaction.objects.create(
            user=request.user,
            amount=amount,
            description=description,
            category=category,
            transaction_type=transaction_type,
            date=transaction_date
        )

        messages.success(request, 'Transaction added successfully!')
        return redirect('transaction_list')

    return render(request, 'transaction_form.html', {'categories': categories})

@login_required
def transaction_update(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category_name = request.POST.get('category_name')
        transaction_type = request.POST.get('transaction_type')
        date_str = request.POST.get('date')

        if amount and description and category_name and transaction_type:
            try:
                amount = Decimal(amount)
            except ValueError:
                messages.error(request, 'Invalid amount.')
                categories = Category.objects.filter(user=request.user)
                return render(request, 'transaction_form.html', {'transaction': transaction, 'categories': categories})

            category, created = Category.objects.get_or_create(name=category_name, user=request.user)

            transaction_date = transaction.date
            if date_str:
                try:
                    transaction_date = date.fromisoformat(date_str)
                except ValueError:
                    messages.error(request, 'Invalid date format.')
                    categories = Category.objects.filter(user=request.user)
                    return render(request, 'transaction_form.html', {'transaction': transaction, 'categories': categories})

            transaction.amount = amount
            transaction.description = description
            transaction.category = category
            transaction.transaction_type = transaction_type
            transaction.date = transaction_date
            transaction.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
        else:
            messages.error(request, 'Please fill all required fields.')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'transaction_form.html', {'transaction': transaction, 'categories': categories})

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category_list.html', {'categories': categories})

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
    return render(request, 'category_form.html')

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
    return render(request, 'category_form.html', {'category': category})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budget_list.html', {'budgets': budgets})

@login_required
def budget_create(request):
    if not Category.objects.filter(user=request.user).exists():
        default_categories = [
            'Food & Dining', 'Transportation', 'Housing', 'Utilities', 'Entertainment',
            'Healthcare', 'Shopping', 'Education', 'Travel', 'Insurance', 'Salary',
            'Freelance', 'Business', 'Investment', 'Other Income', 'Miscellaneous'
        ]
        for cat_name in default_categories:
            Category.objects.create(user=request.user, name=cat_name, description='')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if category_name and amount and start_date and end_date:
            category, created = Category.objects.get_or_create(name=category_name, user=request.user)
            Budget.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                start_date=start_date,
                end_date=end_date
            )
            return redirect('budget_list')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'budget_form.html', {'categories': categories})

@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'goal_list.html', {'goals': goals})

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
    return render(request, 'goal_form.html')

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
    return render(request, 'goal_form.html', {'goal': goal})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('goal_list')
    return render(request, 'goal_confirm_delete.html', {'goal': goal})

@login_required
def analytics(request):
    user = request.user
    monthly_expenses = Transaction.objects.filter(
        user=user, transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    total_expenses = sum(expense['total'] for expense in monthly_expenses)
    # Add percentage to each expense
    for expense in monthly_expenses:
        expense['percentage'] = (expense['total'] / total_expenses * 100) if total_expenses > 0 else 0
    # Create labels for expense chart
    expense_labels = [item['category__name'] or 'Uncategorized' for item in monthly_expenses]
    # Prepare a consistent last-12-month trend (aligned months)
    end_date = datetime.now().date()
    months_count = 12
    # Build (year, month) tuples for the last `months_count` months (from older -> newer)
    month_tuples = []
    for i in range(months_count):
        months_ago = months_count - 1 - i
        y = end_date.year
        m = end_date.month - months_ago
        while m <= 0:
            m += 12
            y -= 1
        month_tuples.append((y, m))

    # Use ExtractYear and ExtractMonth to group by year+month so we don't combine the same month number across different years
    date_from = end_date - timedelta(days=365)
    income_trend_qs = Transaction.objects.filter(
        user=user, transaction_type='income', date__range=[date_from, end_date]
    ).annotate(year=ExtractYear('date'), month=ExtractMonth('date')).values('year', 'month').annotate(total=Sum('amount'))
    expense_trend_qs = Transaction.objects.filter(
        user=user, transaction_type='expense', date__range=[date_from, end_date]
    ).annotate(year=ExtractYear('date'), month=ExtractMonth('date')).values('year', 'month').annotate(total=Sum('amount'))

    income_by_month = {(item['year'], item['month']): item['total'] for item in income_trend_qs}
    expense_by_month = {(item['year'], item['month']): item['total'] for item in expense_trend_qs}

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    labels = [f"{month_names[m-1]} {y}" for (y, m) in month_tuples]

    income_data = [float(income_by_month.get((y, m), 0) or 0) for (y, m) in month_tuples]
    expense_data = [float(expense_by_month.get((y, m), 0) or 0) for (y, m) in month_tuples]
    expense_totals = [item['total'] for item in monthly_expenses]
    # Totals across user transactions
    total_income = Transaction.objects.filter(user=user, transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses_all = Transaction.objects.filter(user=user, transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'monthly_expenses': list(monthly_expenses),
        'total_expenses': total_expenses,
        'expense_labels': expense_labels,
        'expense_totals': expense_totals,
        'income_data': income_data,
        'expense_data': expense_data,
        'trend_labels': labels,
        'total_income': total_income,
        'total_expenses_all': total_expenses_all,
        'net_balance': float(total_income or 0) - float(total_expenses_all or 0),
        # JSON strings for safe insertion into JS
        'trend_labels_json': json.dumps(labels),
        'income_data_json': json.dumps(income_data),
        'expense_data_json': json.dumps(expense_data),
    }
    return render(request, 'analytics.html', context)

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
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'profile.html', {'user': request.user, 'profile': profile})

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    from_email = 'your_email@example.com'  # Replace with your email
    send_mail(subject, message, from_email, [email])
    return otp

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        user = User.objects.filter(email=email).first()
        if user:
            print(user)
            otp = send_otp(email)
            context = {
                'otp': otp,
                'email': email
            }
            return render(request,'verify_otp.html',context)
        else:
            messages.error(request, 'Email address not found.')
    return render(request, 'password_reset.html')




def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otpold = request.POST.get('otpold')
        otp = request.POST.get('otp')
        if otpold == otp:
            contextv = {
                "email": email,
            }
            return render(request, 'setnew_password.html', contextv)
        else:
            messages.error(request, 'Invalid OTP.')
            return render(request, 'verify_otp.html', {'email': email, 'otpold': otpold})
        
    return render(request, 'verify_otp.html')
def set_new_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            try:
                user = User.objects.filter(email=email).first()
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password has been reset successfully.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
        return render(request, 'setnew_password.html', {'email': email})
    return render(request, 'setnew_password.html',{'email': email})



