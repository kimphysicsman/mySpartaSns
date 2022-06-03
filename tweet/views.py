from django.shortcuts import render, redirect
from .models import TweetModel, TweetComment
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView


def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/tweet')
    else:
        return redirect('/sign-in')


def tweet(request):
    if request.method == 'GET':
        user = request.user.is_authenticated

        if user:
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'tweet': all_tweet})
        else:
            return redirect('/sign-in')
    elif request.method == 'POST':
        user = request.user
        content = request.POST.get('my-content', '')
        tags = request.POST.get('tag', '').split(',')

        if content == '':
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'error': '글은 공백일 수 없습니다!',
                                                       'tweet': all_tweet})
        else:
            my_tweet = TweetModel.objects.create(author=user, content=content)
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    my_tweet.tags.add(tag)
            my_tweet.save()
            return redirect('/tweet')


@login_required()
def delete_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    my_tweet.delete()
    return redirect('/tweet')


def tweet_detail(request, id):
    detail_tweet = TweetModel.objects.get(id=id)
    all_comments = TweetComment.objects.filter(tweet=detail_tweet).order_by('-created_at')
    return render(request, 'tweet/tweet_detail.html', {'tweet': detail_tweet, 'comment': all_comments})


def write_comment(request, id):
    if request.method == 'POST':
        user = request.user
        detail_tweet = TweetModel.objects.get(id=id)
        my_comment = TweetComment()
        my_comment.tweet = detail_tweet
        my_comment.author = user
        my_comment.comment = request.POST.get('comment', '')
        my_comment.save()

        return redirect(f'/tweet/detail/{id}')


@login_required()
def delete_comment(request, id):
    my_comment = TweetComment.objects.get(id=id)
    tweet_id = my_comment.tweet.id
    my_comment.delete()

    return redirect(f'/tweet/detail/{tweet_id}')


class TagCloudTV(TemplateView):
    template_name = 'taggit/tag_cloud_view.html'


class TaggedObjectLV(ListView):
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context