import pytest

from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news_id):
    url = reverse('news:detail', args=news_id)
    response = author_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_news_count(news_objects):
    news_count = news_objects.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(news_objects):
    all_dates = [news.date for news in news_objects]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(comment_objects):
    all_timestamps = [comment.created for comment in comment_objects]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
