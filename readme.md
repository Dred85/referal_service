# Сервис авторизации по номеру телефона 
## Решаемые задачи:     
В рамках данного проекта разработана простая и удобная реферальная система, которая позволяет пользователям регистрироваться и авторизовываться по номеру телефона, а также использовать и распространять инвайт-коды.    

## Цель проекта — обеспечить простые и надежные механизмы авторизации и применения реферальной системы, которые можно будет легко интегрировать в другие сервисы.   
  
### Использование:  
    
Авторизация по номеру телефона: 
- Пользователь вводит свой номер телефона в формате:79000000001, для авторизации.  
- Система отправляет 4-значный код авторизации.   
- Пользователь вводит полученный код для завершения процесса авторизации.     
- Если пользователь ранее не авторизовывался, его данные записываются в базу данных.     

Запрос на профиль пользователя:    
    
- При первой авторизации пользователю присваивается случайно сгенерированный 6-значный инвайт-код, состоящий из цифр и символов.    
- В профиле у пользователя отображается один инвайт-код, который он активировал ранее.     
В профиле может быть только один инвайт-код.     
- В профиле выводится список пользователей (номеров телефона), которые ввели инвайт-код текущего пользователя.     

### Требования:  
- Настройте свой сервер (система Ubuntu 22.04)   
- Создайте на сервере ssh ключ, запульте из репозитория на github   
- Установите Docker (подробная инструкция по установке на сайте https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) и docker-compose с помощью команд:   
$ sudo apt update   
$ sudo apt install docker docker-compose   


### Запуск проекта:   
- Для интеграции с сервисом smsaero зарегистрируйтесь на https://smsaero.ru/ и получите API-ключ;    
- заполните файл .env.sample,после чего переименуйте его в .env;    
- в терминале выполнить команду:   
$ docker-compose up -d --build

      
### Автоматическая документация    
http://<IP-адрес вашего сервера>:8000/swagger/  
http://<IP-адрес вашего сервера>:8000/redoc/ 
   
# Эндпоинты API:    
    
### 1. request: POST /users/auth/get_code/  
Описание: Принимает в теле запроса номер телефона 11 цифр(пример: 79000000001) и на этот номер отправляется 4-х значный код аутентификации         
   
{   
  "phone": "79000000000"   
}   
    
response:   
   
{    
    "serializer": {    
        "phone": "79444444448"    
    },    
    "message": "На указанный номер телефона выслан код для авторизации."    
}        
 или если пользователь уже в базе данных    
{   
    "serializer": {    
        "phone": "79444444448"    
    },    
    "message": "Код отправлен повторно."    
}    
          
### 2. request: POST /users/auth/send_code/   
Описание: Принимает в теле запроса номер телефона и код аутентификации. Возвращает два токена: один временный (access) для доступа, второй (refresh) для обновления    временного токена доступа.      
{     
 "phone": "79000000000",     
 "password": "1234"     
}     
      
response:     
{    
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.    eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyOTUxNDUyNCwiaWF0IjoxNzI5NDI4MTI0LCJqdGkiOiJlOGIxNzNiZTM0MTE0NGVlYTBhNzIzZDQxMmQyNGU3YiIsInVzZXJfaWQiOjUsInBob25lIjoiNzk0DQ0NDQ0NDgifQ.PxR0gQhdppJHLYaXZoHojJ9XYjA7BobtGlCEfrkBGYM",    
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.   eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NDM4OTI0LCJpYXQiOjE3Mjk0MjgxMjQsImp0aSI6IjBiNTQxMmJhNzIzMzQ4NDNhZGM2YzlmNDg0OWM3ZDgwIiwidXNlcl9pZCI6NSwicGhvbmUiOiI3OTQ0NDQ0NDQ0OCJ9.PG2u5kZ6tMoyY6C2SsDf6qMTafFnBRuE9-cKUHboEsM"    
}   
     
### 3. request: POST /users/auth/refresh/     
Описание: Принимает в теле запроса refresh токен. Возвращает новый access токен доступа     
     
{   
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.    eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyOTUxNDUyNCwiaWF0IjoxNzI5NDI4MTI0LCJqdGkiOiJlOGIxNzNiZTM0MTE0NGVlYTBhNzIzZDQxMmQyNGU3YiIsInVzZXJfaWQiOjUsInBob25lIjoiNzk0NDQ0NDQ0NDgifQ.PxR0gQhdppJHLYaXZoHojJ9XYjA7BobtGlCEfrkBGYM"    
}     
      
response:     
   
{   
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.   eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NDM5MDU4LCJpYXQiOjE3Mjk0MjgxMjQsImp0aSI6ImFkNmZkNWZlZGY5MjRhMDliM2IxMDJmN2JmOWFkYzMxIiwidXNlcl9pZCI6NSwicGhvbmUiOiI3OTQ0NDQ0NDQ0OCJ9.qBiETqz0xNG1lpfsnaVj1xVFsiRNtoN24ivcG8MWhk4"   
}  
     
### request: GET /users/retrieve/    
Описание: Возвращает данные текущего пользователя, в том числе его рефералов      
  
response:     
   
{
    "phone": "79444444448",
    "invite_code": "2T7QkF",
    "invited_by_phone": "+79000000001",
    "invite_code_referer": "cAXcJR",
    "referrals": [
        "79000000000",
        "79000000001",
        "79444444447"
    ]
}   
    
### 5. request: POST /users/set_referrer/     
Описание: Принимает инвайт код другого пользователя, возвращает сообщение о становлении рефералом другого пользователя          
     
{      
    "invite_code": "7hjCdO"      
}       
response:      
    
{    
    "message": "Вы стали рефералом пользователя с инвайт-кодом cAXcJR"    
}    
    
или   
     
{    
    "message": "Вы не можете ввести свой собственный инвайт-код"   
}    
     
или   
      
{   
    "message": "Вы уже являетесь рефералом пользователя с инвайт-кодом cAXcJR"   
}    

# Интерфейс:
## Реализован минималистичный интерфейс на Django Templates для базового тестирования функционала.   
### 1. Получение  кода на номер телефона    
Введите в поисковой строке браузера: http://<IP-адрес вашего сервера>:8000/users/auth/get_code/      
Вернется HTML-форма для ввода номера телефона. Введите номер телефона и нажмите кнопку "Получить код",       
на указанный номер телефона придет 4-х значный код.      
На экране отобразится надпись "На указанный номер телефона выслан код для авторизации." или "Код отправлен повторно."     
### 2. Регистрация по номеру телефона и полученному коду   
Введите в поисковой строке браузера: http://<IP-адрес вашего сервера>:8000/users/auth/send_code/   
Вернется HTML-форма для ввода номера телефона и полученного кода. Введите номер телефона и полученный код.   
Вернутся токены access и refresh   
### 3. Для просмотра профиля пользователя   
Введите в поисковой строке браузера: http://<IP-адрес вашего сервера>:8000/users/retrieve/
### 4. Обновление токена   
Введите в поисковой строке браузера: http://<IP-адрес вашего сервера>:8000/users/auth/refresh/   
В поле Refresh Token: введите токен refresh, после чего вернется access токен  









