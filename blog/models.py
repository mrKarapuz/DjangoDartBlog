from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class UpdateUser(AbstractUser):
    def __str__(self):
        return self.get_full_name()


class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Tag(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название тега')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tag", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['title']


class Post(models.Model):
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)
    autor = models.ForeignKey(UpdateUser, on_delete=models.CASCADE, related_name='authors', verbose_name='Автор',
                              editable=False)
    content = models.TextField(blank=True, verbose_name='Контент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Опубликовано')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото')
    views = models.IntegerField(default=0, verbose_name='Количество просмотров', editable=False)
    is_published = models.BooleanField(default=1, verbose_name='Статус публикации')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='posts', verbose_name='Категория')
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts', verbose_name='Тег')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("single", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']


class Comments(models.Model):
    name = models.ForeignKey('UpdateUser', on_delete=models.CASCADE, related_name='name_author',
                             verbose_name='Комментатор', null=True)
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Время написания комментария')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments', verbose_name='Пост', null=True)

    def __str__(self):
        return str(self.name)


    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']


class MainHeader(models.Model):
    __instance = None
    title = models.CharField(max_length=30, verbose_name='Заголовок на главной странице')
    content = models.CharField(max_length=500, verbose_name='Контент на главной странице')

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        MainHeader.__instance = None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Главный заголовок'
        verbose_name_plural = 'Главный заголовок'
