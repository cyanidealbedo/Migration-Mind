# django_app/apps/core/views/auth_views.py
import logging
import json
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    error = None
    mode = request.POST.get('mode', 'login')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if mode == 'register':
            display_name = request.POST.get('display_name', '').strip() or username
            if User.objects.filter(username=username).exists():
                error = "That username is already taken."
            elif len(password) < 6:
                error = "Password must be at least 6 characters."
            else:
                user = User.objects.create_user(username=username, password=password)
                user.first_name = display_name
                user.save()
                user = authenticate(request, username=username, password=password)
                login(request, user)
                return redirect('/')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(request.POST.get('next', '/'))
            else:
                error = "Invalid username or password."

    return render(request, 'core/login.html', {
        'error': error,
        'mode': mode,
        'next': request.GET.get('next', '/')
    })


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    from apps.core.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    success = None
    error   = None

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'update_info':
            display_name = request.POST.get('display_name', '').strip()
            bio          = request.POST.get('bio', '').strip()
            if display_name:
                request.user.first_name = display_name
                request.user.save()
            profile.bio = bio
            profile.save()
            success = "Profile updated."

        elif action == 'update_password':
            old_pw  = request.POST.get('old_password', '')
            new_pw  = request.POST.get('new_password', '')
            if not request.user.check_password(old_pw):
                error = "Current password is incorrect."
            elif len(new_pw) < 6:
                error = "New password must be at least 6 characters."
            else:
                request.user.set_password(new_pw)
                request.user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                success = "Password changed."

        elif action == 'upload_avatar':
            avatar_data = request.POST.get('avatar_data', '')
            if avatar_data and avatar_data.startswith('data:image'):
                profile.avatar_data = avatar_data
                profile.save()
                success = "Avatar updated."

    from apps.core.models import Assessment, Notification
    assessments = Assessment.objects.filter(user=request.user).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]

    return render(request, 'core/profile.html', {
        'profile': profile,
        'user': request.user,
        'assessments': assessments,
        'notifications': notifications,
        'success': success,
        'error': error,
    })
