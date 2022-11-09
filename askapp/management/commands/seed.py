from django.core.management.base import BaseCommand, CommandError
from askapp.models import Question, Answer, Tag, User, QuestionVote, AnswerVote, Profile
from random import choice, sample, randint
from faker import Faker

ratio = 10000
batchSizeBig = 10000
batchSizeSmall = 1000
ratios = {
    'users': ratio,
    'questions': ratio * 10,
    'answers': ratio * 100,
    'tags': ratio,
    'answersVote': ratio * 100,
    'questionsVote': ratio * 100
}

f = Faker()


def find_el(arr, el):
    ret = []
    for i in range(0, len(arr)):
        if el == arr[i]:
            ret.append(i)
    return ret


def find_dupl(arr1, arr2):
    for i in range(len(arr1)):
        if arr1[i] in arr2:
            return True
    return False


class Command(BaseCommand):

    def fill_answer_likes(self, count):
        answer_ids = list(
            Answer.objects.values_list('id', flat=True)
        )
        user_ids = list(
            User.objects.values_list('id', flat=True)
        )
        temp_data_likes = []
        q_ids = []
        a_ids = []
        for i in range(count):
            a_id = choice(user_ids)
            q_id = choice(answer_ids)
            print(f"USER QL: {a_id}")
            print(f"QUESTION QL: {q_id}, i = {i}")
            places_a = find_el(a_ids, a_id)
            places_q = find_el(q_ids, q_id)
            if not (not (len(places_a) == 0 or len(places_q) == 0) and find_dupl(places_a, places_q)):

                q_ids.append(q_id)
                a_ids.append(a_id)

                temp_data_likes.append(AnswerVote(
                    author_id=a_id,
                    rate_object_id=q_id,
                    isLike=choice([True, False])
                ))
                if (i + 1) % batchSizeBig == 0:
                    AnswerVote.objects.bulk_create(temp_data_likes, batch_size=batchSizeBig)
                    qs = Answer.objects.find_by_ids(q_ids[i - (batchSizeBig - 1): i + 1])
                    for j in range(0, len(qs)):
                        dig = qs[j].score
                        dig += (1 if temp_data_likes[j % batchSizeBig].isLike == True else 0)
                        qs[j].score = dig
                    Answer.objects.bulk_update(qs, ['score'], batch_size=batchSizeBig)
                    temp_data_likes = []

    def fill_question_likes(self, count):
        question_ids = list(
            Question.objects.values_list('id', flat=True)
        )
        user_ids = list(
            User.objects.values_list('id', flat=True)
        )
        temp_data_likes = []
        q_ids = []
        a_ids = []
        for i in range(count):
            a_id = choice(user_ids)
            q_id = choice(question_ids)
            print(f"USER AL: {a_id}")
            print(f"QUESTION AL: {q_id}, i = {i}")
            places_a = find_el(a_ids, a_id)
            places_q = find_el(q_ids, q_id)
            if not (not (len(places_a) == 0 or len(places_q) == 0) and find_dupl(places_a, places_q)):

                q_ids.append(q_id)
                a_ids.append(a_id)

                temp_data_likes.append(QuestionVote(
                    author_id=a_id,
                    rate_object_id=q_id,
                    isLike=choice([True, False])
                ))
                if (i + 1) % batchSizeBig == 0:
                    QuestionVote.objects.bulk_create(temp_data_likes, batch_size=batchSizeBig)
                    qs = Question.objects.find_by_ids(q_ids[i - (batchSizeBig - 1): i + 1])
                    for j in range(0, len(qs)):
                        dig = qs[j].score
                        dig += (1 if temp_data_likes[j % batchSizeBig].isLike == True else 0)
                        qs[j].score = dig
                    Question.objects.bulk_update(qs, ['score'], batch_size=batchSizeBig)
                    temp_data_likes = []


    def fill_users(self, count):
        temp_data_user = []
        temp_data_profile = []

        for i in range(count):
            profile = {"username": f.unique.user_name(), "mail": f.email()}

            temp_data_user.append(User(
                is_superuser=False,
                username=profile['username'],
                email=profile['mail'],
                password='password'
            ))

            print(f"Profile: {temp_data_user[-1]}, i={i}")

            if (i + 1) % batchSizeSmall == 0:

                print("!!!!!!!!!!!!!!!!!!!!!")

                User.objects.bulk_create(temp_data_user, batch_size=batchSizeSmall)

                u = User.objects.all()[i - (batchSizeSmall - 1): i + 1]

                for j in range(0, len(temp_data_user)):
                    temp_data_profile.append(Profile(
                        nickname=u[j].username,
                        user=u[j]
                    ))

                Profile.objects.bulk_create(temp_data_profile, batch_size=batchSizeSmall)

                temp_data_user = []
                temp_data_profile = []

    def fill_questions(self, count):
        author_ids = list(
            User.objects.values_list(
                'id', flat=True
            )
        )
        tags_ids = list(
            Tag.objects.values_list(
                'id', flat=True
            )
        )
        temp_data_quest = []
        for i in range(count):
            temp_data_quest.append(Question(
                author_id=choice(author_ids),
                text='. '.join(f.sentences(f.random_int(min=2, max=100))),
                title=f.sentence()[:50]
            ))
            print(f"Question: {temp_data_quest[-1]}, i = {i}")
            if (i + 1) % batchSizeBig == 0:
                Question.objects.bulk_create(temp_data_quest, batch_size=batchSizeBig)
                temp_data_quest = []
                q = Question.objects.all()[i - (batchSizeBig - 1) : i + 1]
                for j in range(0, len(q)):
                    q[j].tags.set(sample(tags_ids, k=randint(1, 5)))
                    q[j].save()

    def fill_answers(self, count):
        author_ids = list(
            User.objects.values_list(
                'id', flat=True
            )
        )
        q_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )
        temp_data_ans = []
        for i in range(count):
            temp_data_ans.append(Answer(
                author_id=choice(author_ids),
                question_id=choice(q_ids),
                text='. '.join(f.sentences(randint(2, 100)))
            ))
            print(f"Answer: {temp_data_ans[-1]} i= {i}",)
            if (i + 1) % batchSizeBig == 0:
                Answer.objects.bulk_create(temp_data_ans, batch_size=batchSizeBig)
                temp_data_ans = []

    def fill_tags(self, count):
        temp_data_tsg = []
        for i in range(count):
            profile = {"tag": f.unique.user_name()}
            temp_data_tsg.append(Tag(
                tag=profile["tag"]
            ))
            print(f"Tags: {temp_data_tsg[-1].tag} i = {i}")
            if (i + 1) % batchSizeSmall == 0:
                Tag.objects.bulk_create(temp_data_tsg, batch_size=batchSizeSmall)
                temp_data_tsg = []

    def handle(self, *args, **options):
        print(ratios)
        self.fill_users(ratios['users'])
        self.fill_tags(ratios['tags'])
        self.fill_questions(ratios['questions'])
        self.fill_answers(ratios['answers'])
        self.fill_question_likes(ratios['questionsVote'])
        self.fill_answer_likes(ratios['answersVote'])

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--size',
            nargs='?',
            type=str,
            action='store',
            default='ratio'
        )
