from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import *

# Create your views here.

questions = [
    {
        'id': id,
        'title': 'Card title',
        'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore '
                'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut '
                'aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse '
                'cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, '
                'sunt in culpa qui officia deserunt mollit anim id est laborum.',
        'score': f'{id}',
        'tags': ['Tag1', 'Tag2'],
    } for id in range(100)
]

tags = [f'Tag{i}' for i in range(5)]

context = {
    'tags': tags,
}


def pagination(req, page, model):
    paginator = Paginator(model, page)
    page = int(req.GET.get('page', 1))
    if page > paginator.num_pages:
        raise Http404
    content = paginator.get_page(page)
    max_page = int(page) + 5
    contextt = {
        'content': content,
        'max_page': max_page,
    }
    return contextt


def index(req):
    context.update(pagination(req, 5, questions))
    return render(req, 'index.html', context)


def tag_question(req, tag):
    tagged_questions = []
    for q in questions:
        if tag in q['tags']:
            tagged_questions.append(q)
    context.update(pagination(req, 5, tagged_questions))
    context['tag'] = f'{tag}'
    return render(req, 'tags.html', context)


question_comments = [
    {
        'q_id': i,
        'score': f'{i}',
        'author': 'user',
        'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
    } for i in range(10)
]


def is_ajax(request):
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def comments(req, id):
    question = questions[id]
    context['question'] = question
    context.update(pagination(req, 5, question_comments))
    if is_ajax(req):
        return render(req, 'include/_comments.html', context)
    return render(req, 'comments.html', context)


user = {
    'login': 'user',
    'email': 'user@mail.com',
    'nickname': 'user',
}


def settings(request):
    context['user'] = user
    return render(request, 'settings.html', context)


errors = ['Incorrect login', 'Wrong password']


def login(request):
    context['errors'] = errors
    return render(request, 'login.html', context)


def register(request):
    return render(request, 'register.html', context)


def ask(request):
    return render(request, 'ask.html', context)
