from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import Category, Question, Choice, QuizResult
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegisterForm 


@login_required
def index(request):
    categories = Category.objects.all()
    return render(request, 'quizz/index.html', {"categories": categories})


@login_required
def quiz(request, category_slug):
    
    category = get_object_or_404(Category, slug=category_slug)
    questions_qs = category.questions.all().order_by('id')  

    
    question_list = list(questions_qs)


    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(question_list, 1)
    page = paginator.get_page(page_num)

    
    if page.object_list:
        question_obj = page.object_list[0]
    else:
        
        return redirect('index')

    
    sess_key = f'quiz_answers_{category_slug}'
    answers = request.session.get(sess_key, {})  

    selected_id = None
    correct_id = None

    if request.method == 'POST':
        
        try:
            selected_id = int(request.POST.get('answer'))
        except (TypeError, ValueError):
            selected_id = None

        if selected_id:
            
            answers[str(question_obj.id)] = selected_id
            request.session[sess_key] = answers
            request.session.modified = True

        
        if page_num < paginator.num_pages:
            next_page = page_num + 1
            return redirect(f"{reverse('quiz', kwargs={'category_slug': category_slug})}?page={next_page}")
        else:
            
            return redirect('submit_quiz', category_slug=category_slug)

    
    if str(question_obj.id) in answers:
        try:
            selected_id = int(answers[str(question_obj.id)])
        except:
            selected_id = None

    
    correct_choice = question_obj.choices.filter(is_correct=True).first()
    if correct_choice:
        correct_id = correct_choice.id

    
    progress = int((page_num - 1) / paginator.num_pages * 100) if paginator.num_pages else 0
    
    time_limit = getattr(question_obj, 'time_limit', 10) or 10

    return render(request, 'quizz/question_page.html', {
        'category': category,
        'question': question_obj,
        'selected_id': selected_id,
        'correct_id': correct_id,
        'page': page_num,
        'total_pages': paginator.num_pages,
        'progress': progress,
        'time_limit': time_limit,
    })


@login_required
def submit_quiz(request, category_slug=None):
    
    if request.method != 'GET' and request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    
    if not category_slug:
        return redirect('index')

    sess_key = f'quiz_answers_{category_slug}'
    answers = request.session.get(sess_key, {})

    
    if not answers:
        return render(request, 'quizz/result.html', {
            'score': 0,
            'total': 0,
            'category_slug': category_slug,
            'message': 'No answers submitted.'
        })

    score = 0
    total = 0
    results = {}  

    for qid_str, selected_id in answers.items():
        try:
            qid = int(qid_str)
            total += 1
            correct = Choice.objects.filter(question_id=qid, is_correct=True).first()
            correct_id = correct.id if correct else None
            selected_id_int = int(selected_id)
            results[qid] = {'selected': selected_id_int, 'correct': correct_id}
            if correct_id and selected_id_int == correct_id:
                score += 1
        except Exception:
            continue

    
    category = get_object_or_404(Category, slug=category_slug)
    QuizResult.objects.create(
        user=request.user,
        category=category,
        score=score,
        total=total
    )

    
    try:
        del request.session[sess_key]
        request.session.modified = True
    except KeyError:
        pass

    return render(request, 'quizz/result.html', {
        'score': score,
        'total': total,
        'results': results,
        'category': category,
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            if User.objects.filter(username=username).exists():
                form.add_error('username', "Username already taken")
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                login(request, user)
                return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'quizz/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')  
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "quizz/login.html")


@login_required
def leaderboard(request):
    results = QuizResult.objects.all().order_by('-score', 'created_at')[:10]
    return render(request, "quizz/leaderboard.html", {"results": results})


@login_required
def final_result(request):
    score = request.session.get("score", 0)
    total = request.session.get("total", 1)
    QuizResult.objects.create(
        user=request.user,
        score=score,
        total=total
    )

    return render(request, "final_result.html", {
        "score": score,
        "total": total
    })

