from django.shortcuts import render
from .models import Friend, SiteMessage, Timeline


# Create your views here.
def about(request):
    return render(request, "other/about.html")


def friends(request):
    friends = Friend.objects.all()
    contaxt = {"friends": friends}
    return render(request, "other/friend.html", contaxt)


def blog_comment(request):
    return render(request, "other/comment.html")


def messages(request):
    messages = SiteMessage.objects.all().last()
    contaxt = {"messages": messages}
    return render(request, "article/list.html", contaxt)


def timeline(request):
    ts = Timeline.objects.all()
    contaxt = {"ts": ts}
    return render(request, "other/timeline.html", contaxt)
