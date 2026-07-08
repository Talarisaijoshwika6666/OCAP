import json
import urllib.request
import urllib.error
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from accounts.models import ChatRateLimit

@csrf_exempt
@login_required(login_url='/accounts/login/')
def chatbot_api_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    # Load Groq API key dynamically from settings
    groq_key = getattr(settings, 'GROQ_API_KEY', '').strip()
    
    if not groq_key or groq_key == 'YOUR_GROQ_API_KEY_HERE':
        return JsonResponse({
            'error': 'Groq API key is not configured. Please create a .env file in the root directory and set GROQ_API_KEY to your actual Groq API key.'
        }, status=500)
    
    user = request.user
    
    # Extract real IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')
        
    now = timezone.now()
    one_minute_ago = now - timedelta(minutes=1)
    one_day_ago = now - timedelta(days=1)
    
    # 1. Clean up old rate limit logs (older than 1 day) and apply rate limiting
    try:
        ChatRateLimit.objects.filter(timestamp__lt=one_day_ago).delete()
        
        # 2. Check rate limit limits:
        # 5 requests per minute, and 100 requests per day per user
        minute_limit = 5
        day_limit = 100
        
        # For authenticated users, rate limit by user account. Otherwise, rate limit by IP.
        if user and user.is_authenticated:
            minute_requests = ChatRateLimit.objects.filter(user=user, timestamp__gte=one_minute_ago).count()
            day_requests = ChatRateLimit.objects.filter(user=user, timestamp__gte=one_day_ago).count()
        else:
            minute_requests = ChatRateLimit.objects.filter(ip_address=ip_address, timestamp__gte=one_minute_ago).count()
            day_requests = ChatRateLimit.objects.filter(ip_address=ip_address, timestamp__gte=one_day_ago).count()
            
        if minute_requests >= minute_limit:
            return JsonResponse({
                'error': 'Rate limit exceeded: You can make at most 5 chat requests per minute. Please wait a bit and try again.'
            }, status=429)
            
        if day_requests >= day_limit:
            return JsonResponse({
                'error': 'Rate limit exceeded: You have reached the daily chat limit of 100 queries. Please try again tomorrow.'
            }, status=429)
            
        # Record current request to DB
        ChatRateLimit.objects.create(
            user=user if user and user.is_authenticated else None,
            ip_address=ip_address
        )
        remaining_minute_limit = max(0, minute_limit - minute_requests - 1)
    except Exception as db_err:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Database rate limiting error: {db_err}")
        remaining_minute_limit = 4
    
    # 3. Parse JSON Body
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
        history = data.get('history', [])
    except Exception:
        return JsonResponse({'error': 'Invalid request payload'}, status=400)
        
    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
    # Set up system instructions to define chatbot behavior
    system_instruction = (
        "You are echo, an advanced educational programming assistant built into the LogicLabs Online Coding Assessment platform.\n"
        "Your mission is to guide students/users, explain concepts, and help them debug coding problems.\n"
        "Crucial Guidelines:\n"
        "1. Do NOT write complete code solutions for their assessment problems directly. Instead, explain the logic, highlight flaws, write pseudocode, or outline a step-by-step algorithm.\n"
        "2. Help users learn. Ask guiding questions, point out edge cases, and teach programming principles.\n"
        "3. Provide rich, beautifully formatted markdown answers. Wrap code in blocks specifying language (e.g. ```python), use bold text, lists, and tables.\n"
        "4. Keep answers clear, technical, encouraging, and focused on coding learning."
    )
    
    # Call Groq API (OpenAI format compatible)
    formatted_messages = []
    formatted_messages.append({
        'role': 'system',
        'content': system_instruction
    })
    for item in history:
        role = item.get('role')
        text = item.get('text', '')
        if role and text:
            mapped_role = 'assistant' if role == 'model' else role
            formatted_messages.append({
                'role': mapped_role,
                'content': text
            })
    formatted_messages.append({
        'role': 'user',
        'content': user_message
    })
    
    groq_model = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
    payload = {
        'messages': formatted_messages,
        'model': groq_model,
        'temperature': 0.7,
        'max_tokens': 1500
    }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {groq_key}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            choices = res_body.get('choices', [])
            if choices:
                ai_reply = choices[0].get('message', {}).get('content', '')
                if ai_reply:
                    return JsonResponse({
                        'response': ai_reply,
                        'remaining_minute_limit': remaining_minute_limit
                    })
            return JsonResponse({'error': 'Received an empty response from Groq AI service'}, status=502)
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            error_msg = error_data.get('error', {}).get('message', str(e))
        except Exception:
            error_msg = str(e)
        return JsonResponse({'error': f"Groq API returned error: {error_msg}"}, status=e.code)
    except Exception as e:
        return JsonResponse({'error': f"Failed to connect to Groq AI service: {str(e)}"}, status=500)
