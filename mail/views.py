import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.db import IntegrityError
from django.urls import reverse

from .helpers import strong_password
from .models import User, Email

# Create your views here.
@login_required
def index(request):    

    yay_message = request.session.get('yay_message', '')

    request.session['yay_message'] = ""

    return render(request, "mail/index.html", {
        "yay_message": yay_message
    })


# Allow user to create a new account
def register(request):
    # If user submitted form
    if request.method == 'POST':
        # Define variables
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        # Handle cases
        if not username or not email or not password or not confirm:
            return render(request, "mail/register.html", {
                'nay_message': 'Please fill all field'
            })

        if password != confirm:
            return render(request, "mail/register.html", {
                'nay_message': 'Passwords do not match'
            })

        if not strong_password(password):
            return render(request, "mail/register.html", {
                'nay_message': 'Your password is not strong enough, please choose stronger password'
            })

        # If everything okay, try creating a new user, except for that user already exist
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "mail/register.html", {
                'nay_message': 'Username already taken'
            })

        login(request, user)

        request.session['yay_message'] = 'Registered successfully'

        return HttpResponseRedirect(reverse('mail:index'))

    # If user was being redirect or clicked link
    else:
        return render(request, "mail/register.html")


# Allow user to login and logout
def login_view(request):
    # If user submitted form
    if request.method == 'POST':
        # Define variables
        username = request.POST['username']
        password = request.POST['password']

        if not username or not password:
            return render(request, 'mail/login.html', {
                'nay_message': "Please fill all field"
            })

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['yay_message'] = 'Logged in successfully'
            return HttpResponseRedirect(reverse('mail:index'))
    
        return render(request, "mail/login.html", {
            "nay_message": "Invalid credential"
        })

    # if user reached route via clicking link or being redirected
    else:
        yay_message = request.session.get('yay_message', '')
        request.session['yay_message'] = ""
        return render(request, "mail/login.html", {
            "yay_message": yay_message
        })


def logout_view(request):
    logout(request)
    request.session['yay_message'] = 'Logged out'
    return HttpResponseRedirect(reverse('mail:login'))


# Allow user to compose and send email in a single page
@login_required
@csrf_exempt
def compose(request):
    # POST request required
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)

    # Get data from the form
    data = json.loads(request.body)

    # Get the emails list
    emails = [email.strip() for email in data.get('recipients').split(',')]
    if emails == ['']:
        return JsonResponse({'error': 'At least one recipient required'}, status=400)
    
    # Get the recipients list
    recipients = []
    for email in emails:
        try:
            user = User.objects.get(email=email)
            recipients.append(user)

        except User.DoesNotExist:
            print(f"User with email {email} does not exist")
    
    # Include the current user to receive a copy of this email
    users = set()
    users.add(request.user)
    users.update(recipients)

    # Get the email content
    subject = data.get('subject', '')
    body = data.get('body', '')

    # Save a copy of this email to relevant people
    for user in users:
        email = Email(
            user = user,
            sender = request.user,
            subject = subject,
            body = body,
            read = user == request.user
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()

    return JsonResponse({'message': 'email sent'})


# Allow user to get the appropriate email when choosing mailbox
@csrf_exempt
@login_required
def mailbox(request, mailbox):
    if mailbox == 'inbox':
        emails = Email.objects.filter(
            user = request.user,
            recipients = request.user,
            archive = False
        )
    elif mailbox == 'sent':
        emails = Email.objects.filter(
            user = request.user,
            sender = request.user,
            archive = False
        )
    elif mailbox == 'archive':
        emails = Email.objects.filter(
            user = request.user,
            archive = True
        )
    else:
        return JsonResponse({'error': 'Invalid mailbox'}, status=400)
    
    # Order emails
    emails = emails.order_by("-timestamp").all()

    return JsonResponse([email.serialize() for email in emails], safe=False)


# Allow user to access email content
@csrf_exempt
@login_required
def email(request, email_id):
    try:
        email = Email.objects.get(pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({'error': 'email not found'}, status=404)
    
    if request.method == 'GET':
        return JsonResponse(email.serialize())
    elif request.method == 'PUT':
        data = json.loads(request.body)
        if data.get('read') is not None:
            email.read = data['read']
            print(email.read)
        if data.get('archive') is not None:
            email.archive = data['archive']
            print(email.archive)

        email.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({'error': 'PUT or GET method required'}, status=400)