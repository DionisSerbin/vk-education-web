from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import Http404

from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import QuestionForm, AnswerForm, LoginForm, RegistrationForm, UserSettingsForm, ProfileSettingsForm

from .models import Profile, Question, Answer, Tag, QuestionVote, AnswerVote


def pagination(req, page, model):
    paginator = Paginator(model, page)
    page = int(req.GET.get('page', 1))
    if page > paginator.num_pages:
        raise Http404
    content = paginator.get_page(page)
    max_page = int(page) + 5
    context = {
        'content': content,
        'max_page': max_page,
    }
    return context


def index(request):
    # Index page
    questions = Question.objects.new()
    context = pagination(request, 5, questions)
    return render(request, 'index.html', context)


def new_question(request):
    questions = Question.objects.new()
    page = pagination(request, 5, questions)
    return render(request, 'new_questions.html', page)


def hot_questions(request):
    questions = Question.objects.most_popular()
    page = pagination(request, 5, questions)
    return render(request, 'hot_questions.html', page)


def tag_question(req, tag):
    cur_tag = Tag.objects.filter(tag=tag).first()
    if not cur_tag:
        raise Http404
    tag_qs = Question.objects.find_by_tag(tag)

    context = pagination(req, 5, tag_qs)
    context['tag'] = f'{tag}'

    return render(req, 'tags.html', context)


def is_ajax(request):
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def comments(request, question_id):
    question = Question.objects.find_by_id(question_id)
    q_answers = Answer.objects.most_popular(question)
    context = pagination(request, 5, q_answers)
    context['question'] = question
    if request.method == 'GET':
        form = AnswerForm()
    else:
        if request.user.is_authenticated:
            form = AnswerForm(data=request.POST,
                              request=request, question_id=question_id)
            if form.is_valid():
                answer = form.save()
                return redirect(reverse('comments', kwargs={'question_id': question_id}) + f'#{answer.pk}')
        else:
            return redirect(reverse('login') + f'?next={request.path}')
    context['form'] = form
    if is_ajax(request):
        return render(request, 'include/_comments.html', context)
    return render(request, 'comments.html', context)


@login_required
def settings(request):
    if request.method == 'GET':
        user_form = UserSettingsForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=request.user.profile)
    else:
        user_form = UserSettingsForm(
            data=request.POST,
            instance=request.user
        )
        profile_form = ProfileSettingsForm(
            data=request.POST,
            instance=request.user.profile,
            user=request.user,
            FILES=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'settings.html', context)


@login_required
def logout(request):
    auth.logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def login(request):
    if request.GET.get('next'):
        next_url = request.GET.get('next')
    elif request.session.get('next'):
        next_url = request.session.get('next')
    else:
        next_url = ''

    if request.method == 'GET':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                if next_url != '':
                    return redirect(next_url)
                else:
                    return redirect(reverse('home'))

    if request.session.get('next') != next_url:
        request.session['next'] = next_url

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def register(request):
    if request.user.is_authenticated:
        raise Http404
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST, FILES=request.FILES)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(
                username=user.username,
                password=raw_password
            )
            if user is not None:
                auth.login(request, user)
            else:
                return redirect(reverse('signup'))
            return redirect(reverse('home'))
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def ask(request):
    if request.method == 'GET':
        form = QuestionForm()
    else:
        form = QuestionForm(data=request.POST, request=request)
        if form.is_valid():
            question = form.save()
            return redirect(reverse('comments', kwargs={'question_id': question.pk}))
    return render(request, 'ask.html', {'form': form})


@require_POST
@login_required
def vote(request):
    data = request.POST
    return JsonResponse({'qrating': 42})
