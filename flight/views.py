import math

from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, HttpResponseRedirect, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt

from capstone.utils import render_to_pdf, generate_booking
from .constant import TAX
from .forms import ContactForm
from .forms import LoginForm
from .models import *

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))
            else:
                message = "Invalid username and/or password."
        else:
            message = "Please enter a valid username and password."
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home'))
        else:
            form = LoginForm()
            message = ""
    return render(request, "flight/login.html", {
        "form": form,
        "message": message
    })


def register_view(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensuring password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "flight/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except:
            return render(request, "flight/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "flight/register.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


@csrf_exempt
def flight(request):
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    return_date = None
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        return_date = datetime.strptime(returndate, "%Y-%m-%d")
        flightday2 = Week.objects.get(number=return_date.weekday())  ##
        origin2 = Place.objects.get(code=o_place)  ##
        destination2 = Place.objects.get(code=d_place)  ##
    seat = request.GET.get('SeatClass')

    flightday = Week.objects.get(number=depart_date.weekday())
    destination = Place.objects.get(code=d_place)
    origin = Place.objects.get(code=o_place)
    if seat == 'economy':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(
            economy_fare=0).order_by('economy_fare')
        try:
            max_price = flights.last().economy_fare
            min_price = flights.first().economy_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':  ##
            flights2 = Flight.objects.filter(depart_day=flightday2, origin=origin2, destination=destination2).exclude(
                economy_fare=0).order_by('economy_fare')  ##
            try:
                max_price2 = flights2.last().economy_fare  ##
                min_price2 = flights2.first().economy_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##

    elif seat == 'business':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(
            business_fare=0).order_by('business_fare')
        try:
            max_price = flights.last().business_fare
            min_price = flights.first().business_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':  ##
            flights2 = Flight.objects.filter(depart_day=flightday2, origin=origin2, destination=destination2).exclude(
                business_fare=0).order_by('business_fare')  ##
            try:
                max_price2 = flights2.last().business_fare  ##
                min_price2 = flights2.first().business_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##

    elif seat == 'first':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(
            first_fare=0).order_by('first_fare')
        try:
            max_price = flights.last().first_fare
            min_price = flights.first().first_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':  ##
            flights2 = Flight.objects.filter(depart_day=flightday2, origin=origin2, destination=destination2).exclude(
                first_fare=0).order_by('first_fare')
            try:
                max_price2 = flights2.last().first_fare  ##
                min_price2 = flights2.first().first_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##    ##

    # print(calendar.day_name[depart_date.weekday()])
    if trip_type == '2':
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'flights2': flights2,  ##
            'origin2': origin2,  ##
            'destination2': destination2,  ##
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price / 100) * 100,
            'min_price': math.floor(min_price / 100) * 100,
            'max_price2': math.ceil(max_price2 / 100) * 100,  ##
            'min_price2': math.floor(min_price2 / 100) * 100  ##
        })
    else:
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price / 100) * 100,
            'min_price': math.floor(min_price / 100) * 100
        })


def review(request):
    flight_1 = request.GET.get('flight1Id')
    date1 = request.GET.get('flight1Date')
    seat = request.GET.get('seatClass')
    round_trip = False
    if request.GET.get('flight2Id'):
        round_trip = True

    if round_trip:
        flight_2 = request.GET.get('flight2Id')
        date2 = request.GET.get('flight2Date')

    if request.user.is_authenticated:
        flight1 = Flight.objects.get(id=flight_1)
        flight1ddate = datetime(int(date1.split('-')[2]), int(date1.split('-')[1]), int(date1.split('-')[0]),
                                flight1.depart_time.hour, flight1.depart_time.minute)
        flight1adate = (flight1ddate + flight1.duration)
        flight2 = None
        flight2ddate = None
        flight2adate = None
        if round_trip:
            flight2 = Flight.objects.get(id=flight_2)
            flight2ddate = datetime(int(date2.split('-')[2]), int(date2.split('-')[1]), int(date2.split('-')[0]),
                                    flight2.depart_time.hour, flight2.depart_time.minute)
            flight2adate = (flight2ddate + flight2.duration)

        if round_trip:
            return render(request, "flight/book_summary.html", {
                'flight1': flight1,
                'flight2': flight2,
                "flight1ddate": flight1ddate,
                "flight1adate": flight1adate,
                "flight2ddate": flight2ddate,
                "flight2adate": flight2adate,
                "seat": seat,
                "fee": TAX
            })
        return render(request, "flight/book_summary.html", {
            'flight1': flight1,
            "flight1ddate": flight1ddate,
            "flight1adate": flight1adate,
            "seat": seat,
            "fee": TAX
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def book_summary(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            if request.POST.get('flight2'):
                # Get details of the arrival flight
                arrival_flight = request.POST.get('flight2')
                arrival_flight_date = request.POST.get('flight2Date')
                arrival_f_class = request.POST.get('flight2Class')
                round_trip = True
                arrival_flight_obj = Flight.objects.get(id=arrival_flight)

            # Get details of the departure flight
            departure_flight = request.POST.get('flight1')
            departure_flight_date = request.POST.get('flight1Date')
            departure_f_class = request.POST.get('flight1Class')
            # Check if round trip is selected
            round_trip = False

            # Get customer information
            mobile = request.POST['mobile'].strip()
            country_code = request.POST['countryCode'].strip()
            email_address = request.POST['email'].strip()

            # Get Flight objects for the departure and arrival flights
            departure_flight_obj = Flight.objects.get(id=departure_flight)

            # Get passenger count and details of each passenger
            passengers_count = request.POST['passengersCount']
            passengers = []
            for i in range(1, int(passengers_count) + 1):
                first_name = request.POST[f'passenger{i}FName'].strip()
                last_name = request.POST[f'passenger{i}LName'].strip()
                gender = request.POST[f'passenger{i}Gender'].strip().lower()
                passenger = Passenger(first_name=first_name, last_name=last_name, gender=gender)
                passenger.save()
                passengers.append(passenger)

            # Get coupon code, if any
            coupon = request.POST.get('coupon', '').strip()

            # Calculate fare for the flight(s)
            fare_dict = {
                'Economy': departure_flight_obj.economy_fare * int(passengers_count),
                'Business': departure_flight_obj.business_fare * int(passengers_count),
                'First': departure_flight_obj.first_fare * int(passengers_count),
            }
            fare = fare_dict.get(departure_f_class, 0)
            if round_trip:
                fare += fare_dict.get(arrival_f_class, 0)

            # Create tickets for the flight(s) and passenger(s)
            try:
                oneway_ticket = generate_booking(request.user, passengers, passengers_count, departure_flight_obj,
                                                 departure_flight_date, departure_f_class, coupon, country_code,
                                                 email_address, mobile)
                if round_trip:
                    twoway_ticket = generate_booking(request.user, passengers, passengers_count, arrival_flight_obj,
                                                     arrival_flight_date, arrival_f_class, coupon, country_code,
                                                     email_address, mobile)
            except Exception as e:
                return HttpResponse(f"There was an error while creating your ticket: {str(e)}")

            # Render payment page with ticket details and fare
            if round_trip:
                return render(request, "flight/payment.html", {
                    'fare': fare + TAX,
                    'ticket': oneway_ticket.id,
                    'ticket2': twoway_ticket.id
                })
            return render(request, "flight/payment.html", {
                'fare': fare + TAX,
                'ticket': oneway_ticket.id
            })
        else:
            # Redirect to login page if user is not authenticated
            return HttpResponseRedirect(reverse("login"))
    else:
        # Return error message if request method is not POST
        return HttpResponse("Method needs to be defined as a POST method.")


def payment(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            ticket_id = request.POST['ticket']
            t2 = False
            if request.POST.get('ticket2'):
                ticket2_id = request.POST['ticket2']
                t2 = True
            fare = request.POST.get('fare')
            card_number = request.POST['cardNumber']
            card_holder_name = request.POST['cardHolderName']
            exp_month = request.POST['expMonth']
            exp_year = request.POST['expYear']
            cvv = request.POST['cvv']

            try:
                ticket = Ticket.objects.get(id=ticket_id)
                ticket.status = 'CONFIRMED'
                ticket.booking_date = datetime.now()
                ticket.save()
                if t2:
                    ticket2 = Ticket.objects.get(id=ticket2_id)
                    ticket2.status = 'CONFIRMED'
                    ticket2.save()
                    return render(request, 'flight/payment_process.html', {
                        'ticket1': ticket,
                        'ticket2': ticket2
                    })
                return render(request, 'flight/payment_process.html', {
                    'ticket1': ticket,
                    'ticket2': ""
                })
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be post.")
    else:
        return HttpResponseRedirect(reverse('login'))


def ticket_data(request, ref):
    ticket = Ticket.objects.get(ref_no=ref)
    return JsonResponse({
        'ref': ticket.ref_no,
        'from': ticket.flight.origin.code,
        'to': ticket.flight.destination.code,
        'flight_date': ticket.flight_ddate,
        'status': ticket.status
    })


@csrf_exempt
def get_ticket(request):
    ref = request.GET.get("ref")
    ticket1 = Ticket.objects.get(ref_no=ref)
    data = {
        'ticket1': ticket1,
        'current_year': datetime.now().year
    }
    pdf = render_to_pdf('flight/ticket.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


def bookings(request):
    if request.user.is_authenticated:
        tickets = Ticket.objects.filter(user=request.user).order_by('-booking_date')
        return render(request, 'flight/bookings.html', {
            'page': 'bookings',
            'tickets': tickets
        })
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def cancel_ticket(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            ref = request.POST['ref']
            try:
                ticket = Ticket.objects.get(ref_no=ref)
                if ticket.user == request.user:
                    ticket.status = 'CANCELLED'
                    ticket.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({
                        'success': False,
                        'error': "User unauthorised"
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': e
                })
        else:
            return HttpResponse("User unauthorised")
    else:
        return HttpResponse("Method must be POST.")


def resume_booking(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            ref = request.POST['ref']
            ticket = Ticket.objects.get(ref_no=ref)
            if ticket.user == request.user:
                return render(request, "flight/payment.html", {
                    'fare': ticket.total_fare,
                    'ticket': ticket.id
                })
            else:
                return HttpResponse("User unauthorised")
        else:
            return HttpResponseRedirect(reverse("login"))
    else:
        return HttpResponse("Method must be post.")


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "flight/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'mv@uwindsor.ca', [user.email], fail_silently=False)
                        print('Email sent')
                    except BadHeaderError as e:
                        print('Error: {}'.format(e))
                        return HttpResponse('Invalid header found.')
                    except Exception as e:
                        print('Error: {}'.format(e))
                        return HttpResponse('An error occurred while sending the email.')
                return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="flight/password_reset.html",
                  context={"password_reset_form": password_reset_form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            contact_us = Contact(name=name, email=email, subject=subject, message=message)
            contact_us.save()
            return render(request, 'flight/landingPage.html')
    else:
        form = ContactForm()
    return render(request, 'flight/contact.html', {'form': form})


def about_us(request):
    return render(request, 'flight/about.html')


def home(request):
    return render(request, 'flight/landingPage.html')
