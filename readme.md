# Сервис авторизации по номеру телефона 
## Решаемые задачи:     
В рамках данного проекта разработана простая и удобная реферальная система, которая позволяет пользователям регистрироваться и авторизовываться по номеру телефона, а также использовать и распространять инвайт-коды.    

### Цель проекта — обеспечить простые и надежные механизмы авторизации и применения реферальной системы, которые можно будет легко интегрировать в другие сервисы.   
  
## Использование:  
    
Авторизация по номеру телефона: 
- Пользователь вводит свой номер телефона для авторизации.  
- Система отправляет 4-значный код авторизации.   
- Пользователь вводит полученный код для завершения процесса авторизации.     
- Если пользователь ранее не авторизовывался, его данные записываются в базу данных.     

Запрос на профиль пользователя:    
    
- При первой авторизации пользователю присваивается случайно сгенерированный 6-значный инвайт-код, состоящий из цифр и   символов.
- В профиле у пользователя должна быть возможность ввести чужой инвайт-код, при этом проверяется его существование в системе.     
В профиле можно активировать только один инвайт-код. Если пользователь уже активировал инвайт-код, он должен отображаться в    соответствующем поле при запросе профиля пользователя.   
      
В профиле выводится список пользователей (номеров телефона), которые ввели инвайт-код текущего пользователя.   

### Требования:  
- Настройте свой сервер (система Ubuntu 22.04)   
- Создайте на сервере ssh ключ, запульте из репозитория на github   
- Установите Docker (подробная инструкция по установке на сайте https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) и docker-compose с помощью команд:   
$ sudo apt update   
$ sudo apt install docker docker-compose   


### Запуск проекта:   
- заполнить файл .env.sample, переименовать его в .env;    
- в терминале выполнить команду:   
$ docker-compose up -d --build
- Для интеграции с сервисом smsaero зарегистрируйтесь на https://smsaero.ru/ и получите API-ключ  
      
### Автоматическая документация    
http://127.0.0.1:8000/swagger/   
http://127.0.0.1:8000/redoc/    
   
# Эндпоинты:    
request:   
   
POST /users/auth/get_code/   
{   
  "phone": "79000000000"   
}   
response:   
   
{   
  "phone": "79000000000"   
}   
Описание: Принимает в теле запроса номер телефона и отправляет по нему код аутентификации   
   
request:   
    
POST /users/auth/send_code/   
{   
  "phone": "79000000000",   
  "password": "0000"   
}   
response:   
   
{   
  "access": "some_strange_symbols_but_this_is_a_token",  
  "refresh": "this_is_token_too_but_for_update_access_token"   
}   
Описание: Принимает в теле запроса номер телефона и код аутентификации. Возвращает два токена: один для доступа, второй для обновления токена доступа.   
   
request:  
   
POST /users/auth/refresh/   
{   
  "refresh": "this_is_refresh_token_from_previous_request"   
}   
response:   
   
{  
  "access": "this_a_new_access_token"  
}   
Описание: Принимает в теле запроса refresh токен. Возвращает новый токен доступа   
   
request:   
    
GET /users/retrieve/   
response:   
   
{
    "phone": "79444444446",
    "referrals": ["+79000000002", "+79000000003"],
    "invite_code": "vIIaww",
    "invited_by_phone": "+79000000001",
    "invite_code_referer": "cAXcJR"
}  
   
Описание: Возвращает данные текущего пользователя, в том числе его рефералов    

request:   
    
POST /users/set_referrer/    
{    
    "invite_code": "7hjCdO"    
}     
response:    
    
{    
  "message": "You have become referral of user with invite code 0aA0Bb0"    
}    
or    
   
{    
  "message": "You have already been referral of user with invite code 0aA0Bb0"    
}    
or    
     
{    
  "message": "You cannot enter your own invite code"    
}     
Описание: Принимает инвайт код другого пользователя, возвращает сообщение о становлении рефералом другого пользователя или     сообщение о текущем реферере    



