from django.shortcuts import render,get_object_or_404
from .models import Question
from django.http import HttpResponse
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User  # Import your custom User model
from django.utils import timezone
# from django.template import loader

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {
        "latest_question_list": latest_question_list,
    }
    return render(request, "polls/index.html", context)
def detail(request, question_id):
    #example error 404 not found 
    # try:
        # question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
        # raise Http404("Question does not exist")
    # return render(request, "polls/details.html", {"question": question})
    question=get_object_or_404(Question,pk=question_id)
    return render(request,"polls/detail.html",{"question":question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)



@csrf_exempt
def create_user(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            direction = request.POST.get('direction')

            if not username or not password or not direction:
                return JsonResponse({'error': 'Username, password, and direction are required'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            user = User(username=username, password=password, direction=direction)
            user.save()

            return JsonResponse({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'direction': user.direction,
                    'last_login': user.last_login,
                }
            }, status=201)

        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        # Log the exception
        print(f"Exception: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)