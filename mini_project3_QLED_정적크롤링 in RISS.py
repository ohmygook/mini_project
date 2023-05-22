from bs4 import BeautifulSoup as bs
import urllib.request
import re
from selenium import webdriver
import pandas as pd
import datetime
import os
import getpass

def get_URL(page):
    url_before_page = 'http://www.riss.kr/search/Search.do?isDetailSearch=N&searchGubun=true&viewYn=OP&queryText=&strQuery=%ED%88%AC%EB%AA%85+qled&exQuery=&exQueryText=&order=%2FDESC&onHanja=false&strSort=RANK&p_year1=&p_year2=&iStartCount='
    
    url_after_page = '&orderBy=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&ccl_code=&inside_outside=&fric_yn=&image_yn=&gubun=&kdc=&ttsUseYn=&l_sub_code=&fsearchMethod=search&sflag=1&isFDetailSearch=N&pageNumber=1&resultKeyword=&fsearchSort=&fsearchOrder=&limiterList=&limiterListText=&facetList=&facetListText=&fsearchDB=&icate=bib_t&colName=bib_t&pageScale=10&isTab=Y&regnm=&dorg_storage=&language=&language_code=&clickKeyword=&relationKeyword=&query=ZnO+QLED'

    URL=url_before_page + page + url_after_page
    
    return URL


def get_link(csv_name, page_num):

    for i in range(page_num):
        current_page = i*10
        URL = get_URL(str(current_page))
        try:
            source_code_from_URL = urllib.request.urlopen(URL)
        except urllib.error.URLError as e:
            print("URL Error",e)
        soup = bs(source_code_from_URL, 'lxml', from_encoding='utf-8')

        try:
            for j in range(10):
                paper_link = soup.select('li > div.cont > p.title > a')[j]['href']
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
        'C:/Users/rnrgu/Downloads/chromedriver_win32', "chromedriver")
    driver = webdriver.Chrome(
        driver_path, options=webdriver.ChromeOptions().add_argument("headless"))
    driver.get(URL)

    # 중복 항목 걸러내기
    if os.path.isfile(csv_path):
        existing_data = pd.read_csv(csv_path)
        is_duplicate = existing_data["링크"].str.contains(URL).any()
        if is_duplicate:
            driver.close()
            return None

    html = driver.page_source
    soup = bs(html, "html.parser")

    title = soup.find("h3", "title")
    
    title_kor = ''
    title_eng = ''
    #title_txt = title.get_text("", strip=True).split("=")
    title_txt = title.get_text("", strip=True)
    if "=" in title_txt:
        title_txt=title_txt.split("=")
        try:
            title_kor = re.sub("\n\b", "", str(title_txt[0]).strip())
            title_eng = str(title_txt[1]).strip()
        except IndexError:
            pass
    else:
        title_eng = str(title_txt).strip()

    
    txt_box = []
    text=soup.find("div", "text")
    txt = text.get_text("", strip=True)
    txt_box.append(txt)
    txt_summary = txt_box[0]

    # 카테고리에 해당되는 내용 가져오기 
    detail_box = []
    detail_info = soup.select(
        "#soptionview > div > div.thesisInfo > div.infoDetail.on > div.infoDetailL > ul > li > div > p"
    )
    for detail in detail_info:
        detail_content = detail.get_text("", strip=True)
        detail_wrap = []
        detail_wrap.append(detail_content)

        detail_box.append(detail_wrap)  # 2차원 리스트
    
    # 카테고리 가져와서 주제들이 존재 하는지 비교.
    detail_box_span = []
    detail_info_span = soup.select(
        "#soptionview > div > div.thesisInfo > div.infoDetail.on > div.infoDetailL > ul > li > span.strong ")
    for span in detail_info_span:
        span_content = span.get_text("", strip=True)
        #span_wrap = []
        #span_wrap.append(span_content)

        #detail_box_span.append(span_wrap)#2차원 리스트
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
            elif "학위논문사항" in subject:
                book += detail_box[2][0]
            elif "발행연도" in subject:
                book += detail_box[3][0]
            elif "일반주기명" in subject:
                book += detail_box[-3][0]
            elif "주제어" in subject:
                keyword = ",".join(detail_box[5])
            else: continue
    except IndexError:
        pass


    

    # 엑셀에 항목 옮기기
    reference_data = pd.DataFrame(
        {
            "저자": [author],
            "국문 제목": [title_kor],
            "영문 제목": [title_eng],
            "수록지": [book],
            "주제어": [keyword],
            "요약": [txt_summary],
            #"영문 요약": [txt_eng],
            "링크": [URL],
        }
    )

    driver.close()

    return reference_data


def save_csv(csv_path,data):
    csv =csv_path.replace("/","\\")

    if os.path.isfile(csv_path):
        data.to_csv(csv, mode='a', header = False, index=False)

    else:
        data.to_csv(csv, mode = 'w', header = True, index=False)

def make_folder(folder_name):

    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
       

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    user_name = getpass.getuser()
    folder_root = 'C:/Users/rnrgu/Desktop/mini_project3'        # your_root
    path = folder_root + now
    make_folder(path)

    filename = input('저장할 csv 이름을 입력해주세요. :')
    csv_path = path + "/" + filename + ".csv"
    page_num = input("크롤링할 페이지 수를 입력 해주세요. :")
    get_link(csv_path, int(page_num))


#URL=get_URL('0')
#get_link('crawling about QLED',1)
#save_csv("C:/Users/rnrgu/Desktop/mini_project3",get_reference)
#make_folder('NewCrawl')
