import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from calendar import Calendar
from datetime import date, timedelta, time
import calendar

from .models import User, Event, Follower

def index(request):
    if not request.user.is_authenticated:
        return render(request, "share_plans/login.html")
    
    return HttpResponseRedirect(reverse("month_page", args=(request.user.id, )))

def check_access(request, user_id):
    profile_user = User.objects.get(pk=user_id)
    is_follower = Follower.objects.filter(user=profile_user, follower=request.user, is_approve=True)

    if not is_follower and user_id != request.user.id:
        return False
    
    return True

    
@login_required
def month_page(request, user_id):
    try:
        if not check_access(request, user_id):
            return HttpResponseRedirect(reverse("profile_page", args=(user_id, )))

        month_names_nom = [
        "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        list_day_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        if request.method == 'GET' and 'year' in request.GET and 'month' in request.GET:
            year = int(request.GET['year'])
            month = int(request.GET['month'])
            day = 1
            today = date(year, month, 1)
            last_month_date = today - timedelta(days=1)
            days = calendar.monthrange(today.year, today.month)[1]
            next_month_date = today + timedelta(days=days)
        else:
            today = date.today()
            first = today.replace(day=1)
            year, month, day = today.year, today.month, today.day
            last_month_date = first - timedelta(days=1)
            days = calendar.monthrange(today.year, today.month)[1]
            next_month_date = today + timedelta(days=days)

        type_date = {
            "last": {
                "year": last_month_date.year,
                "month": last_month_date.month,
            },
            "now": {
                "year": year,
                "month": month,
            },
            "next": {
                "year": next_month_date.year,
                "month": next_month_date.month,
            }
        }

        current_user = User.objects.get(id=user_id)
        res = set_calendar(type_date, list_day_of_week, current_user)
    except:
        raise Http404("User does not exist")

    return render(request, "share_plans/index.html",  {
        'range': res,
        'year': year,
        'month': month_names_nom[month],
        'month_num': month,
        'current_user': current_user
    })

def set_calendar(type_date, list_day_of_week, current_user) :
    cal = Calendar()
    days_prev = cal.monthdayscalendar(type_date["last"]["year"], type_date["last"]["month"])[-1]
    days_current = cal.monthdayscalendar(type_date["now"]["year"], type_date["now"]["month"])
    days_next = cal.monthdayscalendar(type_date["next"]["year"], type_date["next"]["month"])[0]
    res_days_next = [day for day in days_next if day != 0]
    res = []
    is_inception = True
    all_events = current_user.events.all()
    all_events_repeat = all_events.filter(repeat=True)
    repeat_events = get_repeat_events(all_events_repeat)

    for week in days_current:
        for i, day in enumerate(week):
            day_of_week = list_day_of_week[i]

            if day == 0 and is_inception:
                day = days_prev.pop(0)
                all_events_day = all_events.filter(date=date(type_date["last"]["year"], type_date["last"]["month"], day))
                cur_month = type_date["last"]["month"]
                cur_year = type_date["last"]["year"]
            elif day == 0:
                day = res_days_next.pop(0)
                all_events_day = all_events.filter(date=date(type_date["next"]["year"], type_date["next"]["month"], day))
                cur_month = type_date["next"]["month"]
                cur_year = type_date["next"]["year"]
            elif day != 0:
                all_events_day = all_events.filter(date=date(type_date["now"]["year"], type_date["now"]["month"], day))
                cur_month = type_date["now"]["month"]
                cur_year = type_date["now"]["year"]
                is_inception = False

            if repeat_events.get(i + 1):
                all_events_repeat = all_events.filter(pk=repeat_events[i + 1].id)
                all_events_day = all_events_day.union(all_events_repeat)

            res.append({
                "day": day,
                "month": cur_month,
                "year": cur_year,
                "events": all_events_day.order_by('time'),
                "day_of_week": day_of_week
            })
    
    return res

@login_required
def day_page(request, user_id):
    try:
        year = int(request.GET['year'])
        month = int(request.GET['month'])
        day = int(request.GET['day'])
        user = User.objects.get(id=user_id)
        all_events = user.events.all()
        all_events_day = all_events.filter(date=date(year, month, day))
        all_events_repeat = all_events.filter(repeat=True)
        repeat_events = get_repeat_events(all_events_repeat)
        day_of_week = date(year, month, day).isoweekday()

        if repeat_events.get(day_of_week):
            all_events_repeat = all_events_repeat.filter(pk=repeat_events[day_of_week].id)
            all_events_day = all_events_day.union(all_events_repeat)
    except:
        raise Http404("User does not exist")

    return render(request, "share_plans/day.html",  {
        "year": year,
        "month": month,
        "day": day,
        "all_events": all_events_day.order_by('time')            
    })
        
@login_required
def get_data_month(request):
    if request.method != 'GET':
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)
    
    if request.method == 'GET' and 'year' in request.GET and 'month' in request.GET:
        year = int(request.GET['year'])
        month = int(request.GET['month'])
        today = date(year, month, 1)
        last_month_date = today - timedelta(days=1)
        days = calendar.monthrange(today.year, today.month)[1]
        next_month_date = today + timedelta(days=days)
    elif request.method == 'GET':
        today = date.today()
        first = today.replace(day=1)
        year, month = today.year, today.month
        last_month_date = first - timedelta(days=1)
        days = calendar.monthrange(today.year, today.month)[1]
        next_month_date = today + timedelta(days=days)

    last_year, last_month = last_month_date.year, last_month_date.month
    next_year, next_month = next_month_date.year, next_month_date.month

    return JsonResponse({
        "year": year,
        "month": month,
        "next_year": next_year,
        "next_month": next_month,
        "last_year": last_year,
        "last_month": last_month
    }, status=200)

def get_repeat_events(all_events_repeat):
    repeat_events = {}

    for event in all_events_repeat:
        repeat_events[event.date.isoweekday()] = event

    return repeat_events

def add_event(request):
    if request.method == "POST":
        hours, minutes = [int(i) for i in request.POST["time-event"].split(':')]
        hours_to, minutes_to = [int(i) for i in request.POST["time-event_to"].split(':')]     
        description = request.POST['description']
        day = int(request.POST['day'])
        month = int(request.POST['month'])
        year = int(request.POST['year'])
        is_repeat = bool(request.POST.get('is-repeat', False))

        if request.POST['event-id']:
            event = Event.objects.get(pk=request.POST['event-id'])
            event.description = description
            event.date = date(year, month, day)
            event.time = time(hours, minutes)
            event.time_to = time(hours_to, minutes_to)
            event.repeat = is_repeat
        else:
            event = Event.objects.create(
                user = request.user,
                description = description,
                date = date(year, month, day),
                time = time(hours, minutes),
                time_to = time(hours_to, minutes_to),
                repeat = is_repeat
            )
        
        event.save()
        return HttpResponseRedirect(f'/user/{request.user.id}/date?year={year}&month={month}&day={day}')
    
    return HttpResponseNotAllowed(["POST"], "Method not allowed. Use POST.")
    
def delete_event(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        event_id = data.get("event_id")
        
        return JsonResponse({
            "event_id": event_id,
        })
    
    return JsonResponse({
        "error": "Only PUT method."
    }, status=400)

@login_required
def profile_page(request, user_id):
    try:
        user_profile = User.objects.get(pk=user_id)
        followers_not_approved = Follower.objects.filter(user=user_profile, is_approve=False)
        followers = Follower.objects.filter(user=user_profile, is_approve=True)
        following = Follower.objects.filter(follower=user_profile)
        is_follower = check_follower(request, user_profile)
        is_approved = check_access(request, user_id)

        is_author = (request.user.id == user_id)
    except:
        raise Http404("User does not exist")

    return render(request, "share_plans/profile.html", {
        "user_profile": user_profile,
        "followers_not_approved": followers_not_approved,
        "followers": followers,
        "following": following,
        "is_follower": is_follower,
        "is_author": is_author,
        "is_approved": is_approved
    })

@login_required
def following(request):
    data = json.loads(request.body)
    user = User.objects.get(pk=int(data.get("user_id")))
    is_follower = check_follower(request, user)

    if is_follower:
        Follower.objects.filter(user=user, follower=request.user).delete()
        
    else:
        new_user = Follower(user=user, follower=request.user)
        new_user.save()

    return JsonResponse({
        "is_follower": is_follower,
        "user_id": request.user.id,
        "username": request.user.username
    })

def check_follower(request, user_profile):
    following_user = Follower.objects.filter(user=user_profile, follower=request.user)
    is_follower = False

    if following_user:
        is_follower  = True

    return is_follower

def change_follower(request, user_id):
    if request.user.id != user_id:
        follow_user = User.objects.get(pk=user_id)
        follower = Follower.objects.get(user=request.user, follower=follow_user)

        if request.method == "PUT":
            if not follower.is_approve:
                follower.is_approve = True
                follower.save()

            return JsonResponse({
                "user_id": user_id,
                "is_approved": follower.is_approve
            })
        else:
            return JsonResponse({
                "error": "Only PUT method."
            }, status=400)
        
def search(request):
    if request.method == "GET":
        username = request.GET['username']
        suggestions = [user.username for user in User.objects.all()]

        matching = [s for s in suggestions if username in s]

        return JsonResponse({
            "matching": matching
        })
        
def search_input(request):
    if request.method == "GET":
        username = request.GET['username']
        try:
            user = User.objects.get(username=username)
            return JsonResponse({
                "user_id": user.id,
            })
        except:
            return JsonResponse({
                "error": 'user not found',
            })

def delete_follower(request):
    if request.method == 'DELETE':
        data = json.loads(request.body)
        user_id = int(data.get('user_id'))

        try:
            follower = Follower.objects.get(user=request.user.id, follower=user_id)
            follower.delete()
            return JsonResponse({
                "status": f'follower with id {user_id} deleted',
            })
        except:
            return JsonResponse({
                "error": 'User not found',
            })
        
    return JsonResponse({
        "error": "Only DELETE method."
    }, status=400)

def change_profile_page(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        user = request.user
        user.avatar = image
        user.save()

    return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "share_plans/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "share_plans/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "share_plans/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "share_plans/register.html")