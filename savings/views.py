from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.views.generic import TemplateView
import calendar

from .forms import MemberForm, ContributionForm, ExpenseForm
from .models import Member, Contribution, Expense


from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import UserRegistrationForm

# savings/views.py
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

from django.db import IntegrityError, transaction


def is_admin(user):
    return user.is_staff

def is_registrar(user):
    return user.groups.filter(name='Registrar').exists()


def is_staff_user(user):
    """Check if the user is logged in and has staff status."""
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user, login_url='/login/')
def register_member_view(request):
    """Admin view to register a new User and Member profile."""
    if request.method == 'POST':
        # 1. Get data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        current_location = request.POST.get('current_location')
        phone_num_1 = request.POST.get('phone_num_1')
        phone_num_2 = request.POST.get('phone_num_2')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # 2. Basic Validation
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'registration/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User with username '{username}' already exists.")
            return render(request, 'registration/register.html')

        try:
            with transaction.atomic():
                # 3. Create Django User for Authentication
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    # Note: You can optionally set is_staff=True here if you intended
                    # the admin registering a member to automatically make them an admin.
                    # For a member, leave is_staff=False (default).
                )

                # 4. Create the linked Member profile
                Member.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    current_location=current_location,
                    phone_number_1=phone_num_1,
                    phone_number_2=phone_num_2 if phone_num_2 else None
                )

                messages.success(request, f"Successfully registered new member: {first_name} {last_name}.")
                return redirect('dashboard')  # Redirect back to dashboard after success

        except IntegrityError:
            messages.error(request, "A database error occurred. The username might already be in use.")
            return render(request, 'registration/register.html')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return render(request, 'registration/register.html')

    # For GET request, render the empty form
    return render(request, 'registration/register.html')



@login_required
def dashboard(request):
    today = timezone.now()
    month = today.month
    year = today.year
    lifetime_total_contributions = Contribution.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    total_contributions = Contribution.objects.filter(month=month, year=year).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.filter(date__month=month, date__year=year).aggregate(total=Sum('amount'))['total'] or 0
    user_contributions = Contribution.objects.filter(month=month, year=year).select_related('member')
    expenses = Expense.objects.filter(date__month=month, date__year=year)
    net_balance = total_contributions - total_expenses
    return render(request, 'dashboard.html', {
        'lifetime_total_contributions': lifetime_total_contributions,
        'total_contributions': total_contributions,
        'total_expenses': total_expenses,
        'user_contributions': user_contributions,
        'expenses': expenses,
        'net_balance': net_balance,
        'month': calendar.month_name[month],
        'year': year
    })

@user_passes_test(is_registrar)
def add_member(request):
    form = MemberForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'member_form.html', {'form': form})

@user_passes_test(is_admin)
def add_contribution(request):
    form = ContributionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'contribution_form.html', {'form': form})

@user_passes_test(is_admin)
def add_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.created_by = request.user
        expense.save()
        return redirect('dashboard')
    return render(request, 'expense_form.html', {'form': form})

@login_required
def monthly_summary(request):
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    total_contributions = Contribution.objects.filter(month=month, year=year).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.filter(date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0
    user_contributions = Contribution.objects.filter(month=month, year=year).select_related('member')
    balance = total_contributions - total_expenses
    expenses = Expense.objects.filter(date__month=month, date__year=year)
    return render(request, 'monthly_summary.html', {
        'month': calendar.month_name[month],
        'year': year,
        'total_contributions': total_contributions,
        'total_expenses': total_expenses,
        'balance': balance,
        'user_contributions': user_contributions,
        'expenses': expenses,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Optional: Create a Member profile linked to this user
            Member.objects.create(
                first_name=user.first_name,
                last_name=user.last_name,
                user=user
            )

            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    Logs out the current user and redirects to the login page.
    We add a short success message (optional).
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile_view(request):
    """View to display the current user's profile and linked member data."""
    # The login_required decorator ensures request.user is an authenticated user.
    try:
        # Attempt to retrieve the linked Member profile using the logged-in user
        # This uses the OneToOneField relationship established in your Member model.
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        # If no linked profile exists (shouldn't happen after admin registration),
        # set member to None. The template handles displaying the warning.
        member = None
        messages.error(request, "Your family savings profile could not be found. Please contact an admin.")

    context = {
        'member': member,  # This is the object passed to the profile.html template
    }
    return render(request, 'my_profile.html', context)



@user_passes_test(is_staff_user)
def member_management_view(request):
    """Displays a list of all registered family members."""
    members = Member.objects.select_related('user').all().order_by('first_name')
    context = {
        'members': members,
    }
    return render(request, 'member_management.html', context)


@user_passes_test(is_staff_user)
def member_detail_view(request, member_id):
    """Displays the profile and financial history for a specific member."""
    # Fetch the member object, raising a 404 if not found
    member = get_object_or_404(Member.objects.select_related('user'), id=member_id)

    # Fetch transactions related to this member
    contributions = member.contributions.all().order_by('-date')
    # expenses = member.member_expenses.all().order_by('-date') # Assuming a related name 'member_expenses' is needed if member can be linked to an Expense

    context = {
        'member': member,
        'contributions': contributions,
        # 'expenses': expenses,
    }
    return render(request, 'member_detail.html', context)
