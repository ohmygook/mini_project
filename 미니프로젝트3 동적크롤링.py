from bs4 import BeautifulSoup as bs
import urllib.request
import re
from selenium import webdriver
import pandas as pd
import datetime
import os
import getpass
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


## riss 페이지 검색창에 검색어를 입력 후 학위 논문 페이지로 넘어간 url 받기
def move_to_riss(query):
    url_RISS='http://www.riss.kr/index.do'
    driver=webdriver.Chrome("C:/Users/rnrgu/Downloads/chromedriver_win32")
    driver.get(url_RISS)
    time.sleep(3)

    # Selenium 패키지로 원하는 페이지까지 이동 & 검색어 입력
    text_box = driver.find_element(By.CSS_SELECTOR,"input#query")
    text_box.send_keys(query)
    text_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # RISS 검색 화면에서 학술 논문으로 넘어가기
    driver.find_element(By.XPATH, '//*[@id="divContent"]/div/div/div[2]/div[1]/div[2]/a/img').click()
    time.sleep(2)

    # KCI 등재 옵션 추가
    
    driver.find_element(
        By.XPATH, '//*[@id="mCSB_3_container"]/li[1]/label/span[1]').click()
    time.sleep(2)
    driver.find_element(
        By.XPATH, '//*[@id="mCSB_3_container"]/li[1]/a').click()
    
    
    # 현재 페이지 url 받기
    current_url = driver.current_url
    return current_url

## 현재 url에서 page 번호를 입력받아 해당 페이지 url return
def get_URL(page):
    current_url=move_to_riss(query)

    # "iStartCount="를 기준으로 앞 부분, page, 그리고 뒷 부분을 합쳐서 새로운 URL 생성
    prefix = current_url.split("iStartCount=")[0] + 'iStartCount='
    suffix = "&".join(current_url.split("iStartCount=")[1].split("&")[1:])

    new_url = prefix + page + suffix
    return new_url  

def get_link(csv_name, page_num):
    
    for i in range(page_num):
        current_page = i*10         # 페이지 당 10개라서 2페이지는 iStartCount=10 
        URL = get_URL(str(current_page))
        try:
            source_code_from_URL = urllib.request.urlopen(URL)    # 페이지 넘버 i를 받아서 urlopen
        except urllib.error.URLError as e:
            print("URL Error",e)
            continue
        soup = bs(source_code_from_URL, 'lxml', from_encoding='utf-8')  # lxml parsing

        try:
            for j in range(10):
                paper_link = soup.select('li > div.cont > p.title > a')[j]['href']      # parsing 하고 class=title인 <p> tag 밑에 있는 <a> 태그에 j 번째 ['href'] 속성값을 갖는 링크 불러옴
                paper_url = "http://riss.or.kr" + paper_link

                try:
                    reference_data = get_reference(paper_url)
                except AttributeError:
                    print("Error: Attribute not found.")
                    break
        
                save_csv(csv_name, reference_data)
        except IndexError:
            print("Error: Index out of range.")

def get_reference(URL):
    driver_path = os.path.join(
        'C:/Users/rnrgu/Downloads/chromedriver_win32', "chromedriver")  # 경로 설정
    driver = webdriver.Chrome(
        driver_path, options=webdriver.ChromeOptions().add_argument("headless"))    # 크롬 브라우저 실행. headless 모드(브라우저 창 표시 x)
    
    driver.get(URL)
    html = driver.page_source
    soup = bs(html, "html.parser")      # html parsing
    title = soup.find("h3", "title")    # <h3 class='title'> 첫 번째 요소 가져옴.
    
    title_kor = ''      # 영문, 국문 제목 중 하나만 있는 경우 존재 -> 없을 때는 빈 문자열로 출력하기 위해서
    title_eng = ''

    title_txt = title.get_text("", strip=True)  # strip은 문자열 앞 뒤 공백을 제거해주는 파이썬 문자열 메소드
    if "=" in title_txt:        # 국문제목 = 영문제목 식으로 나열
        title_txt=title_txt.split("=")  # "="를 통해 split한 후 인덱싱을 통해 할당.         ## Q) 페이지마다 국문,영문 제목 순서가 반대라면?
        try:
            title_kor = re.sub("\n\b", "", str(title_txt[0]).strip())
            title_eng = str(title_txt[1]).strip()
        except IndexError:
            pass
    else:   # 국문 제목 없이 영문 제목만 있을 때
        title_eng = str(title_txt).strip()   

    # 카테고리에 해당되는 내용 가져오기 
    detail_box = []
    detail_info = soup.select(
        "#soptionview > div > div.thesisInfo > div.infoDetail.on > div.infoDetailL > ul > li > div > p")    # 반복문 안에 들어가기 때문에 select로 찾아준다.
    
    for detail in detail_info:
        detail_content = detail.get_text("", strip=True)
        detail_wrap = []
        detail_wrap.append(detail_content)

        detail_box.append(detail_wrap)  # 2차원 리스트
    
    # 카테고리 가져오기
    detail_box_span = []
    detail_info_span = soup.select(
        "#soptionview > div > div.thesisInfo > div.infoDetail.on > div.infoDetailL > ul > li > span.strong ")
    for span in detail_info_span:
        span_content = span.get_text("", strip=True)
        detail_box_span.append(span_content)

    # 항목 별 내용 정리
    # span에 항목 있는지 check 하고 p 값 할당하는 방식으로 해볼까??
    book = ''
    author=''
    keyword=''
    try:
        for subject in detail_box_span:
            if "저자" in subject:
                author = ','.join(detail_box[0])
                
            elif "학술지명" in subject:
                book += detail_box[2][0]+''
                
            elif "권호사항" in subject:
                book += detail_box[3][0]+''
                
            elif "수록면" in subject:
                book += detail_box[-3][0]+''
                
            elif "주제어" in subject:
                keyword = ",".join(detail_box[6])
                
            else: continue
    except IndexError:
        pass

    # 초록 항목 불러오기.
    txt_box = []
    text = soup.find("div", "text")
    # bs를 통해 parsing한 html을 text로 전환           ## Q) 영문, 국문 abstarct가 나눠졌을 때는? 이것 또한 순서가 뒤죽박죽이라 인덱싱으로 불가능할 땐?
    txt = text.get_text("", strip=True)
    txt_box.append(txt)

    # 엑셀에 항목 옮기기
    
    df=reference_data = pd.DataFrame(
        {
            "저자": [author],
            "국문 제목": [title_kor],
            "영문 제목": [title_eng],
            "수록지": [book],
            "주제어": [keyword],
            "초록": [txt_box],
            "링크": [URL],
        }
    
    )
    
    driver.close()
    return reference_data

def save_csv(csv_path,data):
    csv = csv_path.replace("/", "\\")     # 경로 가져올 때 \(=한화 표시) 많이 사용되기 때문에 인식 가능한 "/"로 대체해준다.

    if os.path.isfile(csv_path):        # csv_path 경로에 파일이 존재하는 지 확인 (=isfile)
        data.to_csv(csv, mode='a', header = False, index=False)     # to_csv: data가 csv 파일로 저장하는 기능 수행; mode = 'a' : 데이터를 기존 내용에 추가.
    else:   #새로운 파일 생성                                        # header = False : 헤더(열 이름)을 추가하지 않는다. ; index = False : 인덱스를 추가하지 않는다.
        data.to_csv(csv, mode = 'w', header = True, index=False)    

def make_folder(folder_name):   # folder_name에 해당하는 폴더가 존재(=isdir)하지 않을 때 폴더를 만든다(=make directory)

    if not os.path.isdir(folder_name):  
        os.mkdir(folder_name)

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    user_name = getpass.getuser()
    folder_root = 'C:/Users/rnrgu/Desktop/mini_project3'
    path = folder_root + now
    make_folder(path)

    query=input('검색할 논문의 주제를 입력해주세요. :')
    filename = input('저장할 csv 이름을 입력해주세요. :')
    csv_path = path + "/" + filename + ".csv"
    page_num = input("크롤링할 페이지 수를 입력 해주세요. :")
    get_link(csv_path, int(page_num))
