from django import template

from askapp.models import AnswerVote, QuestionVote

register = template.Library()


@register.simple_tag
def has_vote(votes, rate_object_id, user_id):
    try:
        vote = votes.get(author_id=user_id, rate_object_id=rate_object_id)
        vote = vote.isLike
        vote = 1 if vote else -1
    except (AnswerVote.DoesNotExist, QuestionVote.DoesNotExist):
        vote = 0
    return vote
