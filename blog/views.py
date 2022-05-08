from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, CreateView, RedirectView
from .models import *
from django.db.models import F
from blog.utils import PostsAndPostsByCategory
from .forms import CommentForm, ContactForm, UserLoginForm, UserRegisterForm
from random import shuffle
from django.core.mail import send_mail
from django.contrib.auth import login, logout


class Home(PostsAndPostsByCategory, ListView):

    def get_queryset(self):
        queryset = Post.objects.all()
        if queryset.count() > 1:
            return queryset[1:]
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['first'] = Post.objects.all().first()
        context["title"] = 'Главная'
        context['main_text'] = MainHeader.objects.all().first()
        return context


class PostByCategory(PostsAndPostsByCategory, ListView):

    def get_queryset(self):
        queryset = Post.objects.filter(category__slug=self.kwargs['slug'])
        if queryset.count() > 1:
            return queryset[1:]
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = Category.objects.get(slug=self.kwargs['slug'])
        context["first"] = Post.objects.filter(category__slug=self.kwargs['slug']).first()
        context['main_text'] = MainHeader.objects.all().first()
        return context


class GetPost(DetailView, FormView):
    model = Post
    template_name = 'blog/single.html'
    context_object_name = 'post'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super(GetPost, self).get_context_data(**kwargs)
        self.object.views = F('views') + 1
        self.object.save()
        self.object.refresh_from_db()
        comments = Comments.objects.filter(post__slug=self.kwargs['slug'])
        if comments.count() > 5:
            context["comments"] = comments[:5]
        else:
            context["comments"] = comments
        context['popular'] = Post.objects.order_by('-views')[:5]
        tags = list(Tag.objects.all()[:15])
        shuffle(tags)
        context['tags'] = tags
        context["title"] = Post.objects.get(slug=self.kwargs['slug'])
        context['contact_form'] = ContactForm
        return context

    def post(self, request, *args, **kwargs):
        self_post = Post.objects.get(slug=self.kwargs['slug'])
        if request.user.pk:
            self_user = UpdateUser.objects.get(pk=request.user.pk)
        main_page_url = '<a href="http://127.0.0.1:8000/">\nГлавная страница</a>'
        if self.request.POST.get('id'):
            form = ContactForm(self.request.POST)
            if form.is_valid():
                if request.user.is_authenticated:
                    subject_ = f'Из тестового сайта от {self_user.get_full_name()}'
                    message_ = f"{form.cleaned_data['message']} \nот {self_user.email}"
                    mail = send_mail(subject_, message_, 'iamiskonov@gmail.com', ['iamiskonov@gmail.com'],
                                     fail_silently=False)
                    if mail:
                        messages.success(request, 'Сообщение было успешно отправлено')
                        return redirect(self_post)
                    else:
                        messages.error(request, 'При отправке сообщения возникла ошибка')
                        return redirect(self_post)
                else:
                    messages.error(request, 'Для отправки сообщений, пожалуйста, авторизуйтесь')
                    return redirect(self_post)
            else:
                messages.error(request, 'При отправке сообщения возникла ошибка')
                return redirect(self_post)
        else:
            form = CommentForm(self.request.POST)
            if form.is_valid():
                if request.user.is_authenticated:
                    self.object = form.save(commit=False)
                    self.object.name = self_user
                    self.object.post = self_post
                    self.object.save()
                    messages.success(request, 'Комментарий был успешно опубликован')
                    return redirect(self_post)
                else:
                    messages.error(request, 'Для публикации комментариев, пожалуйста, авторизуйтесь')
                    return redirect(self_post)
            else:
                messages.error(request, 'При публикации комментария возникла ошибка')
                return redirect(self_post)


class PostByTag(PostsAndPostsByCategory, ListView):
    def get_queryset(self):
        queryset = Post.objects.filter(tags__slug=self.kwargs['slug'])
        if queryset.count() > 1:
            return queryset[1:]
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Записи по тегу: ' + str(Tag.objects.get(slug=self.kwargs['slug']))
        context["first"] = Post.objects.filter(tags__slug=self.kwargs['slug']).first()
        context['main_text'] = MainHeader.objects.all().first()
        return context


class RegisterUser(CreateView):
    model = UpdateUser
    template_name = 'blog/register_user.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Пользователь был успешно создан, пожалуйста, авторизуйтесь')
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginUser(FormView):
    template_name = 'blog/login.html'
    form_class = UserLoginForm

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
        else:
            messages.error(request, 'Неверный логин или пароль')
            return redirect('login')


class LogoutUser(RedirectView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
