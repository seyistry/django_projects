from django.shortcuts import render, get_object_or_404
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity
)
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from .models import Post
from django.http import Http404
from django.views.decorators.http import require_POST
from django.views import generic
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

# Create your views here.


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # pagination with three post per page
    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if page is not an integer
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html',
                  {
                      'posts': posts,
                      'tag': tag
                  })


def post_detail(request, year, month, day, post):
    # post = Post.published.get(id=id)
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()
    # list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags_count=Count('tags')
    ).order_by('-same_tags_count', '-publish')[:4]

    return render(request, 'blog/post/detail.html',
                  {
                      'post': post,
                      'comments': comments,
                      "form": form,
                      'similar_posts': similar_posts
                  }
                  )


class PostListView(generic.ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'


class PostDetailView(generic.DetailView):
    # model = Post
    context_object_name = 'post'
    template_name = 'blog/post/detail.html'

    def get_object(self):
        # Get the parameters from the URL
        slug = self.kwargs.get('post')
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')

        # Query using both slug and dat
        return get_object_or_404(
            Post,
            slug=slug,
            publish__year=year,
            publish__month=month,
            publish__day=day
        )

    def get_context_data(self, **kwargs):
        # Get the default context data (the post object)
        context = super().get_context_data(**kwargs)

        # Add comments to the context
        post = self.get_object()
        context['comments'] = post.comments.filter(active=True)
        context['form'] = CommentForm()
        return context


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # send mail
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you to read {post.title}"
            )

            message = (
                f"Read {post.title} at {post_url}\n\n"
            )

            send_mail(subject=subject, message=message,
                      from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    comment = None

    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )


def post_search(request):
    form = SearchForm
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector(
            #     'title', weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            results = (
                Post.published.annotate(
                    # search=search_vector,
                    # rank=SearchRank(search_vector, search_query
                    #                 )
                    similarity=TrigramSimilarity('title', query),
                ).filter(similarity__gte=0.1).order_by('-similarity')
            )

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'result': results
        }
    )
