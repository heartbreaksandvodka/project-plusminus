from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer, 
    UserProfileSerializer,
    PasswordChangeSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from .models import User, PasswordResetToken

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    # Check if user already exists
    errors = serializer.errors
    if 'email' in errors:
        for error in errors['email']:
            if 'already exists' in str(error) or 'unique' in str(error).lower():
                return Response({
                    'error_type': 'user_exists',
                    'message': 'An account with this email already exists. Please login instead.',
                    'redirect_to': 'login'
                }, status=status.HTTP_409_CONFLICT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error_type': 'missing_fields',
            'message': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user exists
    try:
        user = User.objects.get(email=email)
        # User exists, check password
        if not user.check_password(password):
            return Response({
                'error_type': 'incorrect_password',
                'message': 'Incorrect password. Please try again.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is active
        if not user.is_active:
            return Response({
                'error_type': 'inactive_user',
                'message': 'Your account has been deactivated. Please contact support.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Login successful
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # User doesn't exist
        return Response({
            'error_type': 'user_not_found',
            'message': 'No account found with this email. Please register first.',
            'redirect_to': 'register'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Invalidate any existing tokens for this user
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new reset token
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # In a real application, you would send an email with the reset link
        # For now, we'll just return the token for testing purposes
        reset_link = f"http://localhost:3001/reset-password?token={reset_token.token}"
        
        # Simulate email sending (in production, use actual email service)
        try:
            # You can uncomment this in production with proper email settings
            # send_mail(
            #     'Password Reset Request',
            #     f'Click the link to reset your password: {reset_link}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [email],
            #     fail_silently=False,
            # )
            pass
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return Response({
            'message': 'Password reset email sent successfully',
            'reset_link': reset_link,  # Remove this in production
            'token': reset_token.token  # Remove this in production
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        reset_token = PasswordResetToken.objects.get(token=token)
        user = reset_token.user
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        return Response({
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    from django.utils import timezone
    import datetime
    
    # Calculate account age
    account_age = timezone.now() - user.date_joined
    account_age_days = account_age.days
    
    # Calculate profile completeness
    profile_fields = [user.first_name, user.last_name, user.bio, user.phone_number, user.date_of_birth]
    completed_fields = sum(1 for field in profile_fields if field)
    profile_completeness = int((completed_fields / len(profile_fields)) * 100)
    
    # Mock recent activity (in real app, this would come from an activity log)
    recent_activity = [
        {
            'action': 'Profile updated',
            'timestamp': timezone.now() - datetime.timedelta(hours=2),
            'description': 'Updated profile information'
        },
        {
            'action': 'Password changed',
            'timestamp': timezone.now() - datetime.timedelta(days=1),
            'description': 'Changed account password'
        },
        {
            'action': 'Login',
            'timestamp': timezone.now() - datetime.timedelta(hours=1),
            'description': 'Logged into account'
        }
    ]
    
    # Mock notifications
    notifications = [
        {
            'type': 'info',
            'message': 'Welcome to your dashboard!',
            'timestamp': timezone.now()
        },
        {
            'type': 'warning',
            'message': 'Please complete your profile for better experience.',
            'timestamp': timezone.now() - datetime.timedelta(minutes=30)
        }
    ]
    
    return Response({
        'message': f'Welcome back, {user.first_name}!',
        'user': UserSerializer(user).data,
        'stats': {
            'account_age_days': account_age_days,
            'profile_completeness': profile_completeness,
            'total_logins': 1,  # Mock data
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'recent_activity': [
            {
                'action': activity['action'],
                'timestamp': activity['timestamp'].isoformat(),
                'description': activity['description']
            }
            for activity in recent_activity
        ],
        'notifications': [
            {
                'type': notif['type'],
                'message': notif['message'],
                'timestamp': notif['timestamp'].isoformat()
            }
            for notif in notifications
        ]
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    # Placeholder for subscriptions functionality
    return Response({
        'message': 'Subscriptions',
        'subscriptions': []
    }, status=status.HTTP_200_OK)
