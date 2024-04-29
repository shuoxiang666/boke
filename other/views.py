from django.shortcuts import render, redirect
from .models import Friend, SiteMessage, Timeline
from .models import Message
from .forms import MessageForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
def about(request):
    return render(request, "other/about.html")


def friends(request):
    friends = Friend.objects.all()
    contaxt = {"friends": friends}
    return render(request, "other/friend.html", contaxt)


def messages(request):
    messages = SiteMessage.objects.all().last()
    contaxt = {"messages": messages}
    return render(request, "article/list.html", contaxt)


def timeline(request):
    ts = Timeline.objects.all()
    contaxt = {"ts": ts}
    return render(request, "other/timeline.html", contaxt)


@login_required(login_url='/userprofile/login/')
def message_board(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('other:comment')
    else:
        form = MessageForm()
    messages = Message.objects.all().order_by('-created_at')  # 按创建时间逆序排列留言
    return render(request, 'other/comment.html', {'form': form, 'messages': messages})
