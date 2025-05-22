#!E:\PythonP\Python3.13\python.exe

import os
import sys
import io
import re
import string
import random
from urllib.parse import unquote
import mysql.connector as sq_con
from http import cookies
from hashlib import sha256
from urllib.parse import parse_qs
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

# Функция для генерации случайного пароля
def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Функция для хеширования пароля
def hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()

# Функция для проверки пароля
def check_password(hashed_password, user_password):
    return hashed_password == sha256(user_password.encode('utf-8')).hexdigest()

def ru_to_eng(name):
    translit_dict = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    itog = ""
    for sym in name:
        if sym in translit_dict:
            itog+=translit_dict[sym]
        else:
            itog+="sym"
    return itog
# Функция для создания логина
def create_login(name):
    ran_num = random.randint(1,100)
    new_name = ru_to_eng(name)
    return f"{new_name.lower().replace(' ', '_')}_{ran_num}"

class SQL_con():
        config = {
            'host': 'localhost',       # Адрес сервера БД
            'user': 'root',          # Имя пользователя
            'password': '1234',     # Пароль
            'database': 'web_back',      # Название БД
        }
        @staticmethod
        def post_user(data):

            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                INSERT INTO users1 (fio, phone, email, birth_date, gender, bio, login, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                (data["fio"], data["phone"], data["email"], data["birth_date"], 
                data["gender"],data["bio"], data["login"], data["password_hash"]))
            conn.commit()
            conn.close()
        
        @staticmethod    
        def get_user_id(data):
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                SELECT * FROM users1 WHERE (fio='{data["fio"]}' AND phone = '{data["phone"]}'
                AND email = '{data["email"]}' AND birth_date = '{data["birth_date"]}'
                AND gender = {data["gender"]} AND bio = '{data["bio"]}');
                ''')
            user = curr.fetchall()
            conn.close()
            if(len(user)!=0):
                return user[0][0]
            return -1

        @staticmethod    
        def get_pass_from_log(login):
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                SELECT * FROM users1 WHERE (login = %s);
                ''', (login,))
            user = curr.fetchall()
            conn.close()
            if(len(user)!=0):
                return user[0][0]
            return -1
        @staticmethod

        def post_language(user_id, data):
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute('''DELETE FROM users_languages1 WHERE (user_id = %s);''', (user_id,))
            for i in data:
                curr.execute(f'''
                    INSERT INTO users_languages1 VALUES (%s, %s);
                    ''', (user_id, i))
            conn.commit()
            conn.close()
        
        @staticmethod
        def update_info(id, data):
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                UPDATE users1
                SET fio = %s, phone = %s, email = %s, birth_date = %s, gender = %s, bio = %s
                WHERE users_id = %s;
                ''', (data["fio"], data["phone"], data["email"], data["birth_date"], 
                data["gender"],data["bio"], id))
            conn.commit()
            conn.close()

        @staticmethod
        def get_names():
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                SELECT login FROM users1;
                ''')
            users = curr.fetchall()
            conn.close()
            return users

        

def main():
    if method=='GET':
        cookie = cookies.SimpleCookie()
        if 'HTTP_COOKIE' in os.environ:
            cookie.load(os.environ['HTTP_COOKIE'])
            corrupted_bio = cookie["fio"].value
            bytes_bio = corrupted_bio.encode('latin-1')
            decoded_bio = bytes_bio.decode('utf-8')
            cookie["fio"] = decoded_bio
            corrupted_bio = cookie["bio"].value
            bytes_bio = corrupted_bio.encode('latin-1')
            decoded_bio = bytes_bio.decode('utf-8')
            cookie["bio"] = decoded_bio
        env = Environment(
            loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
        )
        template = env.get_template('index.html')
        output = template.render(**cookie)
        #Выводим страницу
        print("Status: 200 OK")
        print("Content-Type: text/html; charset=utf-8")
        print()  # Пустая строка между заголовками и телом
        print(output)
    elif method=="POST":
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        post_data = sys.stdin.read(content_length)
        new_data = parse_qs(post_data)
        
        #Валидация
        errors = {}

        #Поля для вставки
        fields = {}

        #Имя
        try:
            fio = new_data['field-fio'][0]
            fields["fio"] = fio
            if fio == '':
                errors['er_fio'] = "ФИО обязательно для заполнения"
            elif not re.match(r'^[A-Za-zА-Яа-яёЁ\s-]{1,150}$', fio):
                errors['er_fio'] = 'ФИО должно содержать только буквы, пробелы и дефисы (макс. 150 символов)'
        except:
            errors['er_fio'] = "Поле Фио не может быть пустым"
            fields["fio"] = ""

        #email
        try:
            email = new_data['field-email'][0]
            fields["email"] = email
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                errors['er_email'] = 'Введите корректный email'
        except:
            errors['er_email'] = "Поле email не может быть пустым"
            fields["email"] = ""

        #ЯП
        try:
            languages = new_data["languages"]
            fields["languages"] = languages 
        except:
            errors['er_languages'] = 'Выберете хотя бы 1 язык программирования'
            fields["languages"] = "" 

        #Дата рождения
        try:
            birth_date = datetime.strptime(new_data['field-birthday'][0], '%Y-%m-%d').date()
            fields["birth_date"] = birth_date
            if birth_date > datetime.now().date():
                errors['birth_date'] = 'Дата рождения не может быть в будущем'
        except ValueError:
            errors['er_birth_date'] = 'Некорректный формат даты. Используйте ГГГГ-ММ-ДД'
            fields["birth_date"] = new_data['field-birthday'][0]
        except KeyError:
            errors['er_birth_date'] = 'Поле даты не может быть пустым'
            fields["birth_date"] = " "

        #Телефон
        try:
            phone = new_data['field-tel'][0]
            fields["phone"] = phone
            cleaned_phone = re.sub(r'[^\d]', '', phone)
            # Проверяем основные форматы для России
            if not re.fullmatch(r'^(\+7|8)\d{10}$', cleaned_phone):
                errors['er_phone'] = "Введите корректный номер телефона(Россия)"
        except:
            errors["er_phone"] = "Поле email не может быть пустым"
            fields["phone"] = ""

        #Cогласие
        try:
            if not new_data["check-1"]:
                errors['er_contract_agreed'] = "Ознакомьтесь с контрактом для отправки"
        except:
            errors['er_contract_agreed'] = "Ознакомьтесь с контрактом для отправки" 

        #Пол
        gender = new_data["radio-group-1"][0]
        fields["checked"+gender] = "checked"
        #Биография
        try:
            bio = new_data["bio"][0]
        except:
            bio = ""
        fields["bio"] = bio

        #Подключаем печеньки
        cookie = cookies.SimpleCookie()
        if 'HTTP_COOKIE' in os.environ:
            cookie.load(os.environ['HTTP_COOKIE'])
        
        #Проверка на ошибки
        if errors:
            for field, error in fields.items():
                try:
                    del cookie["er_"+field]
                except Exception as e:
                    ...
            expires = datetime.now() + timedelta(days=365)
            for field, error in errors.items():
                cookie[field] = error
            for field, value in fields.items():
                if field != 'contract_agreed':
                    if field != "languages":
                        cookie[field] = value
                    else:
                        cookie[field] = ''.join(value)
                    cookie[field]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            env = Environment(
            loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
            )
            template = env.get_template('index.html')
            output = template.render(**cookie)
            for field, error in errors.items():
                del cookie[field]
            #Выводим страницу
            print("Status: 200 OK")
            print("Content-Type: text/html; charset=utf-8")
            print(cookie.output())  # Печатаем заголовки Set-Cookie
            print()  # Пустая строка между заголовками и телом
            print(output)
        else:
            expires = datetime.now() + timedelta(days=365)
            for field, error in fields.items():
                try:
                    del cookie["er_"+field]
                except Exception as e:
                    ...
            for field, value in fields.items():
                if field != 'contract_agreed':
                    if field != "languages":
                        cookie[field] = value
                    else:
                        cookie[field] = ''.join(value)
                    cookie[field]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            #Переделываем данные
            new_data = {
                    "fio": fio,
                    "phone": phone,
                    "email": email,
                    "birth_date": birth_date,
                    "gender": gender,
                    "bio": bio,
                }
            if not ("id" in cookie):
                logins = [a[0] for a in SQL_con.get_names()]
                login = create_login(fio.split()[0])
                while login in logins:
                    login+=str(random.randint(1,1000))
                password = generate_password()
                hashed_password = hash_password(password)
                new_data["password_hash"] = hashed_password
                new_data["login"] = login
                SQL_con().post_user(new_data)
                SQL_con().post_language(SQL_con().get_user_id(new_data), languages)
                phrase = "Форма успешно отправлена"
                print("Status: 200 OK")
                print("Content-Type: text/html; charset=utf-8")
                print()
                env = Environment(
                    loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
                )
                template = env.get_template('index.html')
                output = template.render(mess = phrase, login = login, password = password)
                print(output)
            else:
                id = cookie["id"].value
                SQL_con.update_info(id, new_data)
                SQL_con.post_language(id, languages)
                phrase = "Форма успешно обновлена"
                print("Status: 200 OK")
                print("Content-Type: text/html; charset=utf-8")
                print(cookie.output())
                print()
                env = Environment(
                    loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
                )
                template = env.get_template('index.html')
                output = template.render(**cookie, mess = phrase)
                print(output)
    else:
        print("Status: 404 Not Found")
        print("Content-Type: text/html; charset=utf-8")
        print("Wrong url (Change url to '/' pls)")
method = os.environ.get('REQUEST_METHOD', '')
sys.stdout.reconfigure(encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
try:
    main()
except Exception as e:
    error_msg = f"Critical error: {e}"
    file = open("logs.txt", "w")
    file.write(error_msg)
    file.close()
    print("Status: 200 OK")
    print("Content-Type: text/html; charset=utf-8")
    print()
    print(e)


