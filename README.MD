# Secure Python Web API

## Описание проекта

Данный проект представляет собой учебное backend‑сервис на Python, реализующий REST API с упором на базовые **меры информационной безопасности**. Проект используется для демонстрации защиты веб‑приложений от распространённых уязвимостей (SQL Injection, XSS), а также корректной реализации аутентификации и анализа безопасности в CI/CD (Bandit, OWASP Dependency‑Check).

---

## API

### 1. Аутентификация

#### `POST /auth/login`
Аутентификация пользователя и получение JWT‑токена.

**Запрос:**
```json
  {
    "username": "user",
    "password": "password"
  }
```

**Ответ:**
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer",
  "expiresAt": "2025-12-17T00:00:00"
}
```

### 2. Регистрация

#### `POST /auth/register`
Создание нового пользователя в системе.

**Запрос:**
```json
  {
    "username": "user",
    "password": "password",
    "email": "user@example.com"
  }
```

**Ответ:**
```json
{
  "msg": "user created",
  "username": "user",
  "email": "user@example.com"
}
```

---

### 3. Получение данных

#### `GET /api/data`
Возвращает список постов (защищённый эндпоинт).

**Требуется аутентификация (JWT)**:

Headers: Authorization: Bearer "JWT_TOKEN"

**Ответ:**
```json
[
    {
        "id": 1,
        "title": "Post title",
        "content": "Post content",
        "author": "user"
    }
]
```

---

### 4. Создание данных

#### `POST /items`
Создание нового поста (защищённый эндпоинт).

**Требуется аутентификация (JWT)**:
```
Headers: Authorization: Bearer "JWT_TOKEN"
```

**Запрос:**
```json
{
    "title": "Post title",
    "content": "Post content",
    "author": "user"
}
```

**Ответ:**
```json
  {
      "id": 1,
      "title": "Post title",
      "content": "Post content",
      "author": "user"
  }
```
---

## Реализованные меры защиты

### 1. Защита от SQL Injection

SQL‑инъекции предотвращаются за счёт :
- использования **ORM (SQLAlchemy)** вместо ручной генерации SQL‑запросов (это преобразует вызовы Python в параметризованные SQL-запросы).
- отсутствия конкатенации пользовательского ввода в SQL.
- автоматического экранирования параметров

Пример в коде:
```python
# app/auth.py:39
user = db.query(models.User).filter(models.User.username == login_req.username).first()

# app/data.py:33
posts = db.query(models.Post).offset(skip).limit(limit).all()
```

Пользовательский ввод никогда не вставляется напрямую в SQL‑строку.

---

### 2. Защита от XSS (Cross‑Site Scripting)

Реализована с использованием кастомных валидаторов Pydantic.
Все пользовательские текстовые поля (username, title, content)
проходят HTML-экранирование через стандартную библиотеку `html.escape`
до сохранения в базе данных.

Примеры в коде:

```python
# app/schemas.py:11
@field_validator('username', 'password')
def sanitize_string(cls, v):
    return html.escape(v) if isinstance(v, str) else v
```

---

### 3. Защита от Broken Authentication

JWT токены: Безопасная аутентификация с временными токенами, которые клиент передает в
заголовке каждого запроса
- Реализована выдача JWT-токенов при успешном логине
- Секретный ключ хранится в переменных окружения
- Если некорректном токене, FastAPI
возвращает Unauthorized (401)

Хеширование паролей: Использование bcrypt для хеширования
Middleware: Автоматическая проверка токенов на защищенных endpoints


Реализация в коде:

```python

# app/security.py:15
def get_password_hash(password: str) -> str:
    truncated = password[:72]
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta = None) -> (str, datetime):
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt, expire


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
```

---

### 4. Безопасная конфигурация

- CORS: Настройка разрешенных источников
- Секретные ключи вынесены в переменные окружения


---

## CI/CD

Пайплайн GitHub Actions включает при каждом push и pull-request:
1. Установку зависимостей
2. Запуск Bandit (SAST)
3. Запуск OWASP Dependency‑Check
4. Сохранение отчётов как artifacts

Отчет Bandit (SAST):


Отчет OWASP Dependency-Check:


Ссылка на последний успешный запуск pipeline в репозитории:

## Установка проекта

1. Скопировать `.env.example` в `.env` и заполнить значения
2. Создать venv и установить:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```
3. Запустить:
```bash
uvicorn app.main:app --reload
```
API доступно по http://127.0.0.1:8000. Swagger UI: http://127.0.0.1:8000/docs
---

## Проверка API

1. Аутентификация с токеном:

```bash
curl `
  -Method POST `
  -Uri "http://localhost:8000/auth/login" `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"username":"user","password":"password"}'
```

2. Регистрация:
```bash
curl `
  -Method POST `
  -Uri "http://localhost:8000/auth/register" `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"username":"user","password":"password","email":"user@example.com"}'
```

3. Получение данных:
```bash
curl `
-Method GET `
-Uri "http://localhost:8000/api/data" `
-Headers @{ "Authorization: Bearer <ваш_токен>" }
```

4. Запись данных:
```bash
curl `
  -Method POST `
  -Uri "http://localhost:8000/api/data" `
  -Headers @{
      "Authorization" = "Bearer <ваш_токен>";
      "Content-Type"  = "application/json"
  } `
  -Body '{
      "title": "Post title",
      "content": "Post content",
      "author": "user"
  }'
```


