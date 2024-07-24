import json
from django.http import HttpResponse, HttpResponseRedirect
from . import urls
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import logout
from django.urls import reverse
from .models import Clue, UserClueScore
from users.models import CustomUser 
from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import ClueForm
from django.db.models import F
from django.http import JsonResponse
from geopy.distance import geodesic
import os
from dotenv import load_dotenv


def index(request):
    return render(request, 'index.html')

def listOfBundles(request):

    return render(request, 'bundleDisplay.html')

def logoutView(request):
    logout(request)
    return redirect("/")

def leaderboard(request):
    return render(request, 'leaderboard.html')



def map(request):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    return render(request, 'map.html', {'API_KEY': api_key})

def adminView(request):
    return render(request, 'admin.html')

def userView(request):
    return render(request, 'user.html')

def bundleView(request, bundle):
    unsolved_clues = {}
    unsolved_clues[bundle] = Clue.objects.filter(
        approved=True,
        bundle=bundle,
    )
    user = request.user
    user_clue_scores = []

    for clue in unsolved_clues[bundle]:
        user_clue_score, created = UserClueScore.objects.get_or_create(user=user, clue=clue)
        user_clue_scores.append(user_clue_score)

    print(user_clue_scores)
    return render(request, 'Bundle.html', {'bundle': bundle, 'active_clues': unsolved_clues, 'user_clue_scores': user_clue_scores})



class submitClue(generic.CreateView):
    model = Clue
    form_class = ClueForm
    template_name = "submittingClue.html"

    def form_valid(self, form):
        form.instance.approved = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("user")
    
def get_solved_clues(request):
    user = request.user
    solved_clues = Clue.objects.filter(
        usercluescore__user=user, usercluescore__solved=True,  
    ).exclude(
        approved=False
    )
    print(solved_clues)
    data = [{'latitude': clue.latitude, 'longitude': clue.longitude} for clue in solved_clues]
    return JsonResponse(data, safe=False)

def display_unapproved_clues(request):
    if request.method == 'POST':
        if 'approve_selected' in request.POST:
            selected_clue_ids = request.POST.getlist('clue_ids')
            clues_to_approve = Clue.objects.filter(id__in=selected_clue_ids)
            for clue in clues_to_approve:
                clue.approved = True
                clue.save()
        elif 'delete_selected' in request.POST:
            selected_clue_ids = request.POST.getlist('clue_ids')
            clues_to_delete = Clue.objects.filter(id__in=selected_clue_ids)
            clues_to_delete.delete()
        return redirect('display_unapproved_clues')        
    else:
        unapproved_clue_list = Clue.objects.filter(approved=False)
    return render(request, 'admin.html', {'unapproved_clue_list': unapproved_clue_list})


def calculate_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            clue_id = data.get('clue_id')
            curr_latitude = data.get('latitude')
            curr_longitude = data.get('longitude')

            user = request.user

            clue = Clue.objects.get(pk=clue_id)
            user_clue_score, created = UserClueScore.objects.get_or_create(user=user, clue=clue)

            user_location = (float(curr_latitude), float(curr_longitude))
            print(f"Current Location: {curr_latitude}, {curr_longitude}")
            clue_location = (float(clue.latitude), float(clue.longitude))
            print(f"Clue Location: {clue.latitude}, {clue.longitude}")
            distance = geodesic(user_location, clue_location).meters
            print(distance)

            if user_clue_score.attempts_left == 0:
                return JsonResponse({'message': 'No Attempts Remaining'})
            elif distance < 35:
                score_to_add = clue.point_value - (user_clue_score.attempts * 10)
                print(score_to_add)
                CustomUser.objects.filter(pk=user.pk).update(score=F('score') + score_to_add)
                user_clue_score.solved = True
                clue.save()
                user_clue_score.save()
                return JsonResponse({'message': 'Check-in successful!'})
            else:
                user_clue_score.attempts += 1
                user_clue_score.attempts_left -= 1
                user_clue_score.save()
                return JsonResponse({'message': 'Wrong Location!'})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'message': 'Invalid request method'}, status=400)
