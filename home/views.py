from django.shortcuts import render, redirect
from django.views import View
from .models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyForm
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    # def get(self, request):
    #     posts = Post.objects.all()
    #     return render(request, 'home/post.html', {'posts': posts})
    def get(self, request):
        posts = Post.objects.prefetch_related('pcomments').all()
        return render(request, 'home/post.html', {'posts': posts, 'form': self.form_class, 'reply_form': self.form_class_reply})

    @method_decorator(login_required)
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post_id = request.POST.get('post_id')
            new_comment.save()
            messages.success(request, 'Your comment has been submitted successfully!', 'success')

        return redirect('home:home')


class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        comments = self.post_instance.pcomments.filter(is_reply=False)
        return render(request, 'home/detail.html', {'post': self.post_instance, 'comments': comments, 'form': self.form_class, 'reply_form': self.form_class_reply})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, 'your comment submitted successfully', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, 'home/create.html', {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'you created a new post', 'success')
            return redirect('home:home')


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.get(id=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request, 'your reply send', 'success')
        return redirect('home:post_detail', post.id, post.slug)
