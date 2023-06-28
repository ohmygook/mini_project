from django.shortcuts import render, redirect
from board.models import Board


# 클라이언트의 요청을 처리하고 응답을 반환하는 함수 또는 클래스 기반의 뷰를 정의

# /home : 홈 화면 return
def home(request):
    return render(request,"home.html")

# board_list.html 렌더링 할 때 rsBoard 변수를 context로 전달해 템플릿에 게시물 목록 표시
def board(request):
    rsBoard = Board.objects.all()

    return render(request,"board_list.html",{
        'rsBoard':rsBoard
    })

def board_write(request):
    return render(request,"board_write.html")

def board_insert(request):
    btitle = request.GET['b_title']
    bnote = request.GET['b_note']
    bwriter = request.GET['b_writer']

    if btitle != "":
        rows = Board.objects.create(b_title=btitle, b_note=bnote, b_writer=bwriter)
        return redirect('/board')
    else:
        return redirect('/board_write')

def board_view(request):
    bno = request.GET['b_no']
    rsDetail = Board.objects.filter(b_no=bno)

    return render(request, "board_view.html", { 
        'rsDetail':rsDetail
    })


def board_edit(request):
    bno = request.GET['b_no']
    rsDetail = Board.objects.filter(b_no=bno)

    return render(request, "board_edit.html", {
        'rsDetail': rsDetail
    })


def board_update(request):
    bno = request.GET['b_no']
    btitle = request.GET['b_title']
    bnote = request.GET['b_note']
    bwriter = request.GET['b_writer']

    try:
        board = Board.objects.get(b_no=bno)
        if btitle != "":
            board.b_title = btitle
        if bnote != "":
            board.b_note = bnote
        if bwriter != "":
            board.b_writer = bwriter

        try:
            board.save()
            return redirect('/board')
        except ValueError:
            return Response({"success": False, "msg": "에러입니다."})

    except ObjectDoesNotExist:
        return Response({"success": False, "msg": "게시글 없음"})
    

def board_delete(request):
    bno = request.GET['b_no']
    rows = Board.objects.get(b_no=bno).delete()

    return redirect('/board')
     