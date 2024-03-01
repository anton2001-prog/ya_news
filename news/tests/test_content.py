from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone

from news.models import News, Comment
from news.forms import CommentForm

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.news = News.objects.create(
            title='Тестовая новость', text='Просто текст.'
        )
        cls.author = User.objects.create(username='Комментатор')
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        # Запоминаем текущее время:
        now = datetime.now()
        # Создаём комментарии в цикле.
        for index in range(10):
            # Создаём объект и записываем его в переменную.
            comment = Comment.objects.create(
                news=cls.news,
                author=cls.author,
                text=f'Текст {index}'
            )
            comment.created = now - timedelta(days=index)
            comment.save()

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_comments_order(self):
        response = self.client.get(self.detail_url)
        # Проверяем, что объект новости находится в словаре контекста
        # под ожидаемым именем - названием модели.
        self.assertIn('news', response.context)
        # Получаем объект новости.
        news = response.context['news']
        all_comments = news.comment_set.all()
        # Собираем временные метки всех новостей.
        all_timestamps = [
            comment.created for comment in all_comments
        ]
        sorted_timestamps = sorted(all_timestamps)
        # Проверяем, что id первого комментария меньше id второго.
        self.assertEqual(all_timestamps, sorted_timestamps)


class TestContent(TestCase):
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        today = datetime.today()
        News.objects.bulk_create(News(
            title=f'Новость {index}',
            text=f'Просто текст {index}',
            date=today - timedelta(days=index)
        )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    def test_news_count(self):
        # Загружаем главную страницу.
        response = self.client.get(self.HOME_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        news_count = object_list.count()
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_dates = [news.date for news in object_list]
        # Сортируем полученный список по убыванию.
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)
