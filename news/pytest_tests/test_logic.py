import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, logic_url, form_data):
    client.post(logic_url, form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author_client, author, form_data, logic_url, news
        ):
    response = author_client.post(logic_url, form_data)
    assertRedirects(response, f'{logic_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, logic_url):
    bad_words_data = {'text': f'какйо-то текст {BAD_WORDS[0]}, ущу текст'}
    response = author_client.post(logic_url, bad_words_data)
    print(WARNING)
    print(response.context['form']['errors'])
