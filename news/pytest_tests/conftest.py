import pytest

from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Атвор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_objects(client):
    today = datetime.today()
    url = reverse('news:home')
    News.objects.bulk_create(News(
        title='Заголовок',
        text='Текст новости',
        date=today - timedelta(days=index)
    )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    response = client.get(url)
    news_objects = response.context['object_list']
    return news_objects


@pytest.fixture
def comment_objects(client, news, author, news_id):
    today = datetime.today()
    Comment.objects.bulk_create(Comment(
        news=news,
        author=author,
        text='Текст коммента',
        created=today - timedelta(days=index)
    )
        for index in range(10)
    )
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    news = response.context['news']
    comment_objects = news.comment_set.all()
    return comment_objects


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст коммента'
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def news_id(news):
    return (news.pk,)


@pytest.fixture
def form_data():
    comment_text = 'текст коммента'
    return {'text': comment_text}


@pytest.fixture
def logic_url(news_id):
    url = reverse('news:detail', args=news_id)
    return url