from .models import Post


class PostsAndPostsByCategory:
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 4
