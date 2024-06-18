import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# 사이트 URL
url = "https://burnfit.io/exercise_library/"

# 요청 및 응답 받기
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 최종 데이터를 저장할 리스트
data_list = []

# 모든 운동 카테고리 링크 추출
categories = soup.find_all("div", class_="wp-block-columns is-layout-flex wp-container-12 wp-block-columns-is-layout-flex")

for category in categories:
    exercises = category.find_all("a")
    for exercise in exercises:
        exercise_name = exercise.text.strip()
        exercise_link = exercise.get('href')
        
        # 각 운동 페이지로 이동하여 GIF 이미지 및 운동 방법 추출
        if exercise_link:
            exercise_response = requests.get(exercise_link)
            exercise_soup = BeautifulSoup(exercise_response.text, 'html.parser')
            
            # 카테고리 추출
            category_details = exercise_soup.find("p", class_="has-text-color")
            category_name = category_details.text.split(" |")[0].strip() if category_details else "Category not found"
            
            # GIF 이미지 URL 추출
            gif_image_figure = exercise_soup.find("figure", id="library_exercise_image")
            gif_url = gif_image_figure.find("img")['data-src'] if gif_image_figure and gif_image_figure.find("img") and 'data-src' in gif_image_figure.find("img").attrs else (gif_image_figure.find("img")['src'] if gif_image_figure and gif_image_figure.find("img") else None)
            
            # Only append if GIF URL is found
            if gif_url:
                # 자세 방법 추출 (자세는 이렇게 하세요.)
                exercise_description = []
                exercise_details = exercise_soup.find("ol")
                if exercise_details:
                    description_items = exercise_details.find_all("li")
                    for item in description_items:
                        exercise_description.append(item.text.strip())

                # 데이터 저장
                data_list.append({
                    "category": category_name,
                    "exercise_name": exercise_name,
                    "gif_url": gif_url,
                    "description": " ".join(exercise_description) if exercise_description else "No description available"
                })

# JSON으로 결과 출력
json_data = json.dumps(data_list, indent=4, ensure_ascii=False)
print(json_data)

# JSON 데이터를 DataFrame으로 변환
data_frame = pd.read_json(json.dumps(data_list))

# DataFrame을 CSV 파일로 저장
data_frame.to_csv('exercise_data.csv', index=False, encoding='utf-8-sig')
