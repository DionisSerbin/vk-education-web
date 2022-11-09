from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Sum


class VoteManager(models.Manager):
    def get_likes(self, primary_key):
        return self.filter(rate_object=primary_key, isLike=True).count()

    def get_dislikes(self, primary_key):
        return self.filter(rate_object=primary_key, isLike=False).count()

    def get_rating(self, primary_key):
        return self.get_likes(primary_key) - self.get_dislikes(primary_key)

    def find_by_id(self, id):
        try:
            vote = self.get(pk=id)
        except ObjectDoesNotExist:
            raise Http404
        return vote


class QuestionVote(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    isLike = models.BooleanField()

    rate_object = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name="votes"
    )

    objects = VoteManager()


class AnswerVote(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    isLike = models.BooleanField()

    rate_object = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        related_name="votes"
    )
    objects = VoteManager()


class QuestionManager(models.Manager):
    def most_popular(self):
        return self.all().order_by('-score').prefetch_related('author', 'tags')

    def new(self):
        return self.all().order_by('-date_create').prefetch_related('author', 'tags')

    def find_by_tag(self, tag):
        questions = self.filter(
            tags__tag__iexact=tag).prefetch_related('author')
        if not questions:
            raise Http404
        return questions

    def find_by_id(self, id):
        try:
            question = self.get(pk=id)
        except ObjectDoesNotExist:
            raise Http404
        return question

    def find_by_ids(self, ids):
        try:
            questions = []
            for id in ids:
                question = self.get(pk=id)
                questions.append(question)
        except ObjectDoesNotExist:
            raise Http404
        return questions


class AnswerManager(models.Manager):
    def most_popular(self, question):
        return self.filter(question=question).order_by('-is_correct', '-score')

    def find_by_id(self, id):
        try:
            answer = self.get(pk=id)
        except ObjectDoesNotExist:
            raise Http404
        return answer

    def find_by_ids(self, ids):
        try:
            answers = []
            for id in ids:
                answer = self.get(pk=id)
                answers.append(answer)
        except ObjectDoesNotExist:
            raise Http404
        return answers


class ProfileManager(models.Manager):
    def top_ten(self):
        return self.all().order_by('-score')[:10]


class Question(models.Model):
    title = models.CharField(
        max_length=1024,
        verbose_name='Title'
    )
    text = models.TextField(
        verbose_name='Text'
    )
    date_create = models.DateField(
        auto_now_add=True,
        verbose_name='Date of creation'
    )
    last_modified = models.DateField(
        auto_now=True,
        verbose_name='Last modified'
    )
    tags = models.ManyToManyField('Tag')
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='questions'
    )
    score = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    # Manager
    objects = QuestionManager()


class Answer(models.Model):
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='answers'
    )
    text = models.TextField(
        verbose_name='Text'
    )
    score = models.IntegerField(
        default=0
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )
    is_correct = models.BooleanField(
        verbose_name='Is Correct',
        default=False
    )
    date_create = models.DateField(
        auto_now_add=True,
        verbose_name='Date of creation'
    )
    last_modified = models.DateField(
        auto_now=True,
        verbose_name='Last modified'
    )

    def __str__(self):
        return self.author.profile.nickname

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    # Manager
    objects = AnswerManager()


class Tag(models.Model):
    tag = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='profiles_avatars/',
        blank=True
    )
    nickname = models.CharField(
        max_length=128,
        verbose_name='NickName'
    )
    score = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    # Manager
    objects = ProfileManager()

    def get_score_from_questions(self):
        questions_scores = self.user.questions.aggregate(Sum('score'))
        return questions_scores['score__sum']

    def get_score_from_answers(self):
        answers_scores = self.user.answers.aggregate(Sum('score'))
        return answers_scores['score__sum']

    def update_score(self):
        self.score = self.get_score_from_questions() + self.get_score_from_answers()
        self.save(update_fields=['score'])
        return self.score


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
