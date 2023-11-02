## Agricola-Team4/be
- 2023년도 1학기 | 소프트웨어공학 | Team 4 | Back-end Part
<br>

## 💻 프로젝트 소개
- '아그리콜라' 보드게임을 응용 소프트웨어나 온라인 서비스로 개발
- 프로토타입(초기 데모) 개발
<br>

## 🗓 개발 기간
- 2023.0.0 ~ 2023.6.13
<br>

## 👨‍👨‍👧‍👦 BE 멤버 구성
- 손윤석 | 제선명 | 한동연 | 홍예희
<br>

## ⚙️ 개발 환경
- Python 3.10.9  
```pip install django```  
```pip install djangorestframework```  
```pip install drf-yasg```  
```pip install django-cors-headers```  
```pip install pymysql```  
```pip install mysql-client```  
```python3 manage.py runserver```  
<br>

## 📍 주요 기능
- 선플레이어 결정
  
  ![image](https://github.com/Agricola-Team4/be/assets/65332747/9198b0ce-1b22-460d-9ad9-c6e77ae6cdb4)
  - ```/player/choose_first_player/```
- 행동칸 이동
  
  ![image](https://github.com/Agricola-Team4/be/assets/65332747/c4a7e25d-c4d6-4610-9776-19724a76608c)
  - ```/familyposition/take_action/```
- 농지 만들기

  ![image](https://github.com/Agricola-Team4/be/assets/65332747/9639f986-08f0-4d40-b4a9-e7532c82960c)
  - ```/boardposition/construct_land/```
- 울타리 만들기

  ![image](https://github.com/Agricola-Team4/be/assets/65332747/b9d2d6b5-1841-45fd-b09c-497db3109205)

  - ```/fenceposition/build_fence/```
- 주요설비 활성화

  ![image](https://github.com/Agricola-Team4/be/assets/65332747/a8859306-7f5b-4e0c-a26f-6a996e33c307)

  - ```/mainfacilitycard/activate_card/```
