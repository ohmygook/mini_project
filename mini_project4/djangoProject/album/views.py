from django.shortcuts import render, redirect
from album.models import Album

# FileSystemStorage를 import 해 파일을 저장할 경로를 지정
# 파일 시스템에 파일을 저장하고 관리하기 위한 다양한 메서드와 옵션 제공
from django.core.files.storage import FileSystemStorage

import datetime
import random
import sys
import os

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# home 화면에 database로부터 받은 데이터를 반환하기 위해 rsAlbum context로 전달 

# 수정 후 코드, rsAlbum을 컨텍스트에 추가하여 템플릿에 활용
def home(request):
    rsAlbum = Album.objects.all().filter(a_usage='1')
    
    return render(request, "home.html", {
        'rsAlbum': rsAlbum
    })

def album(request):
    rsAlbum = Album.objects.all().filter(a_usage='1')
    return render(request, "album_list.html", {
        'rsAlbum': rsAlbum
    })


def album_write(request):
    return render(request, "album_write.html")


def album_insert(request):

    atitle = request.POST['a_title']
    atype = request.POST['a_type']
    anote = request.POST['a_note']

    name_date = str(datetime.datetime.today().year) + '_' + \
        str(datetime.datetime.today().month) + \
        '_' + str(datetime.datetime.today().day)

    uploaded_file = request.FILES['ufile']
    name_old = uploaded_file.name
    name_ext = os.path.splitext(name_old)[1]
    name_new = 'A' + name_date + '_' + \
        str(random.randint(1000000000, 9999999999))

    fs = FileSystemStorage(location='static/board/photos')

    name = fs.save(name_new + name_ext, uploaded_file)

    rows = Album.objects.create(
        a_title=atitle, a_note=anote, a_type=atype, a_image=name, a_usage='1')

    return redirect('/album')
 
# request.GET['key'] : URL 쿼리 문자열에서 특정 key에 해당하는 값을 가져온다.
def album_view(request):
    ano = request.GET['a_no']

    rsData = Album.objects.get(a_no=ano)
    rsData.a_count += 1
    rsData.save()

    rsDetail = Album.objects.filter(a_no=ano)

    return render(request, "album_view.html", {
        'rsDetail': rsDetail,
        'a_no': ano,
    })

# 'a_no'에 해당되는 값을 서버로부터 요청하여 ano 변수에 할당
# ano에 할당된 값으로 필터링을 통해 해당 데이터만 불러와서 rsDetail 변수에 할당
def album_edit(request):
    ano = request.GET['a_no']
    rsDetail = Album.objects.filter(a_no=ano)

    return render(request, "album_edit.html", {
        'rsDetail': rsDetail,
        'a_no': ano,
    })


# request.POST 메서드를 이용하여 사용자로부터 서버에 데이터를 제출
def album_update(request):

    ano = request.POST['a_no']
    atitle = request.POST['a_title']
    atype = request.POST['a_type']
    anote = request.POST['a_note']

    # request.FILES: 파일 업로드와 관련된 데이터를 담고있는 객체
    if 'ufile' in request.FILES:
        name_date = str(datetime.datetime.today().year) + '_' + str(
            datetime.datetime.today().month) + '_' + str(datetime.datetime.today().day)

        uploaded_file = request.FILES['ufile']
        name_old = uploaded_file.name
        name_ext = os.path.splitext(name_old)[1]
        name_new = 'A' + name_date + '_' + \
            str(random.randint(1000000000, 9999999999))

        # 파일 업로드 및 다운로드 관리
        fs = FileSystemStorage(location='static/board/photos')
        fname = fs.save(name_new + name_ext, uploaded_file)

        album = Album.objects.get(a_no=ano)
        album.a_title = atitle
        album.a_type = atype
        album.a_note = anote
        album.a_image = fname
        album.save()
    else:
        album = Album.objects.get(a_no=ano)
        album.a_title = atitle
        album.a_type = atype
        album.a_note = anote
        album.save()

    return redirect('/album')


def album_delete(request):
    ano = request.GET['a_no']
    album = Album.objects.get(a_no=ano)
    album.a_usage = '0'
    album.save()

    return redirect('/album')
