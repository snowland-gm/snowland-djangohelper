# snowland-djangohelper API Reference (English, Detailed)

> Version: 0.3.0
> Compatible with: Python 3.6+ / Django 2.0+ (up to 5.1) / DRF 3.11+
> All import paths are rooted at `djangohelper`.

This document describes every public API with four elements: **Functionality / Parameters / Returns / Example**.

---

## 1. Auth & Crypto

### 1.1 `djangohelper.auth.hasher`

**Functionality**: Provides SM3 (Chinese national cryptography standard) based Django password hashers. All subclass `django.contrib.auth.hashers.BasePasswordHasher` and plug directly into Django's password framework (`settings.PASSWORD_HASHERS`, `check_password`, `make_password`, etc.).

| Class | `algorithm` | Key attribute | Description |
| --- | --- | --- | --- |
| `SM3PasswordHasher` | `sm3` | — | Salted SM3 hash, recommended default |
| `UnsaltedSM3PasswordHasher` | `unsalted_sm3` | — | Unsalted SM3 (insecure, kept for legacy data) |
| `PBKDF2_SM3PasswordHasher` | `pbkdf2_sm3` | `iterations=100000` | PBKDF2 iteration + SM3 digest |
| `BCryptSM3PasswordHasher` | `bcrypt_sm3` | `rounds=12` | bcrypt wrapping SM3 (requires `bcrypt`) |
| `SM3KDFPasswordHasher` | `sm3kdf` | `iterations=100000` | SM3 KDF key derivation |

#### Common methods (provided by every subclass)

**`encode(password, salt) -> str`**
- Functionality: encode a plaintext password into a storable hash string.
- Parameters:
  - `password` (str): plaintext password (must not be `None`).
  - `salt` (str): salt value, must not contain `$`.
- Returns: `str`, formatted as `algorithm$salt$hash` (segment count varies slightly per subclass).

**`verify(password, encoded) -> bool`**
- Functionality: verify a plaintext password against a stored hash using constant-time comparison (timing-attack safe).
- Parameters:
  - `password` (str): plaintext to verify.
  - `encoded` (str): stored hash string.
- Returns: `bool`, `True` on match.

**`safe_summary(encoded) -> collections.OrderedDict`**
- Functionality: return summary info for admin display.
- Parameters: `encoded` (str): stored hash string.
- Returns: `OrderedDict` with keys such as `algorithm`, masked `salt`, masked `hash`.

**`must_update(encoded) -> bool`** (provided by some subclasses, e.g. `PBKDF2_SM3PasswordHasher`, `BCryptSM3PasswordHasher`)
- Functionality: returns `True` when the hash's iteration count / rounds differs from the class default, indicating a re-hash is needed.
- Parameters: `encoded` (str).
- Returns: `bool`.

**`harden_runtime(password, encoded)`** (provided by some subclasses)
- Functionality: spend extra compute to reach the current iteration count so verification time is uniform across hashes, mitigating user enumeration.
- Parameters: `password` (str), `encoded` (str).
- Returns: `None`.

#### Configuration example

```python
# settings.py
PASSWORD_HASHERS = [
    'djangohelper.auth.hasher.SM3PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

```python
from django.contrib.auth.hashers import make_password, check_password
h = make_password('secret', hasher='djangohelper.auth.hasher.SM3PasswordHasher')
check_password('secret', h)   # True
```

---

### 1.2 `djangohelper.utils.crypto.pbkdf2`

**Functionality**: thin wrapper over Django's `django.utils.crypto.pbkdf2` using SM3 as the pseudo-random function (PRF) for key derivation.

```python
pbkdf2(password, salt, iterations, dklen=0, digest=pysmx.SM3.SM3Type) -> bytes
```

- Parameters:
  - `password` (str|bytes): master password.
  - `salt` (str|bytes): salt.
  - `iterations` (int): iteration count.
  - `dklen` (int, default `0`): derived key length; `0` uses the digest's default length.
  - `digest` (callable, default `pysmx.SM3.SM3Type`): hash algorithm object.
- Returns: `bytes`, the derived key.
- Example:
  ```python
  from djangohelper.utils.crypto import pbkdf2
  key = pbkdf2('secret', 'salt', 100000)
  ```

---

## 2. Unified Response

### 2.1 `djangohelper.responses.APIResponse`

**Functionality**: subclasses `rest_framework.response.Response` and automatically wraps business data into a unified JSON structure on construction, guaranteeing a consistent response format across all endpoints.

```python
APIResponse(data=None, status=None, template_name=None, headers=None,
            exception=False,
            content_type='application/json; charset=utf-8 ',
            successful=True, code=ERROR_CODE_OPERATION_SUCCESS, message=None)
```

- Parameters:
  - `data` (any, default `None`): business payload, placed into the `data` field.
  - `status` (int|str, default `None`): HTTP status code, forwarded to DRF.
  - `template_name` (str, default `None`): template name (rarely used).
  - `headers` (dict, default `None`): response headers.
  - `exception` (bool, default `False`): whether this is an exception response.
  - `content_type` (str, default `'application/json; charset=utf-8 '`): response content type.
  - `successful` (bool, default `True`): business success flag.
  - `code` (int, default `ERROR_CODE_OPERATION_SUCCESS=1`): business error code.
  - `message` (str|None, default `None`): hint message.
- Returns: a `rest_framework.response.Response` instance; its `.data` is:
  ```json
  { "successful": true, "code": 1, "message": null, "data": { } }
  ```
- Example:
  ```python
  from djangohelper.responses import APIResponse
  return APIResponse(data={"id": 1}, message="ok")
  ```

---

## 3. Pagination

### 3.1 `djangohelper.pagination.BasePageNumberPagination`

**Functionality**: subclasses `rest_framework.pagination.PageNumberPagination` and overrides `get_paginated_response` so paginated results also use the `APIResponse` unified structure.

- Parameters (method-level):
  - `get_paginated_response(self, data)`: `data` is the serialized list of the current page.
- Returns: `APIResponse` whose `.data` is:
  ```json
  { "successful": true, "code": 1, "message": null,
    "data": { "count": 100, "next": "url", "previous": null, "results": [ ] } }
  ```
- Example: works automatically with `SelfModelViewSet`; no manual call needed.

### 3.2 `djangohelper.viewhelper.paginator.generate_paginator_result`

**Functionality**: paginate a queryset and return a dict of `{current page object, page-index queue}`, convenient for rendering pagination navigation in Django templates.

```python
generate_paginator_result(queryset, per_page, orphans=0,
                          allow_empty_first_page=True,
                          length_pagequeue=5, page=1,
                          key_contacts='contacts', key_index='ind') -> dict
```

- Parameters:
  - `queryset` (QuerySet|dict): data to paginate; if a QuerySet it is serialized via `django.core.serializers` then paginated, if a dict it is used directly.
  - `per_page` (int): items per page.
  - `orphans` (int, default `0`): number of orphan items allowed to merge into the previous page.
  - `allow_empty_first_page` (bool, default `True`): whether the first page may be empty.
  - `length_pagequeue` (int, default `5`): number of page numbers to display.
  - `page` (int, default `1`): target page.
  - `key_contacts` (str, default `'contacts'`): key name for the current page in the result dict.
  - `key_index` (str, default `'ind'`): key name for the page-index queue in the result dict.
- Returns: `dict`, e.g.
  ```python
  {'contacts': <Page object>, 'ind': [1, 2, 3, 4, 5]}
  ```
  `contacts` can be used in templates as `{{ contacts.object_list }}` etc.
- Example:
  ```python
  from djangohelper.viewhelper.paginator import generate_paginator_result
  ctx = generate_paginator_result(Article.objects.all(), per_page=10, page=2)
  ```

---

## 4. ViewSets

### 4.1 `djangohelper.viewsets.SelfModelViewSet`

**Functionality**: subclasses `rest_framework.viewsets.ModelViewSet` and wraps the return values of the `list` / `retrieve` / `create` / `update` / `destroy` actions into `APIResponse`, removing the need to build unified responses manually in each view.

- Parameters: used like a standard DRF ViewSet; subclasses must provide `queryset` and `serializer_class`.
- Returns: `APIResponse` for each action:
  - `list`: success `code=1`, `data` is the serialized list (with `count/next/previous/results` when paginated).
  - `retrieve`: `data` is the single serialized object.
  - `create`: HTTP `201`, `data` is the newly created object.
  - `update`: `data` is the updated object.
  - `destroy`: HTTP `204`, empty body.
- Example:
  ```python
  from djangohelper.viewsets import SelfModelViewSet
  class ArticleViewSet(SelfModelViewSet):
      queryset = Article.objects.all()
      serializer_class = ArticleSerializer
  ```

---

## 5. Permissions

**Functionality**: all subclass `rest_framework.permissions.BasePermission` and implement `has_permission(request, view) -> bool`, attachable to a DRF view's `permission_classes`. Anonymous users (`is_anonymous`) uniformly return `False` unless noted otherwise.

| Class | Rule (returns `True` when) |
| --- | --- |
| `AdminPermission` | logged in, member of the `管理员` group, and `user.is_superuser` |
| `AuditPermission` | `user.is_auditor` or `user.is_superuser` |
| `OperatorPermission` | `user.is_operator` or `user.is_superuser` |
| `SuperuserPermission` | `user.is_superuser` |
| `AllPermission` | any authenticated (`is_authenticated`) user |

- Parameters: `has_permission(self, request, view)`
  - `request`: DRF `Request`; current user via `request.user`.
  - `view`: the current view instance.
- Returns: `bool`, whether to allow.
- Example:
  ```python
  from djangohelper.permissions import AdminPermission
  class MyView(APIView):
      permission_classes = [AdminPermission]
  ```

---

## 6. Database Models

### 6.1 `djangohelper.db.models.BaseModel`

**Functionality**: abstract base model (`Meta.abstract = True`) providing uniform `created_time` / `updated_time` timestamp fields and a set of convenience query / write classmethods for all business models.

- Fields:
  - `created_time` (DateTimeField, `auto_now_add=True`): record creation time.
  - `updated_time` (DateTimeField, `auto_now=True`): record update time.

Class methods:

**`new(cls, form) -> Model`**
- Functionality: create and save a record from a field dict.
- Parameters: `form` (dict): field name → value; only non-empty values are written.
- Returns: the newly created and `save()`d model instance.

**`update(cls, id_, **kwargs) -> None`**
- Functionality: update specified fields by primary key.
- Parameters: `id_` (any): primary key value; `**kwargs`: fields to update (list values take their first element).
- Returns: `None`.

**`one(cls, **kwargs) -> Model`**
- Functionality: equivalent to `cls.objects.get(**kwargs)`.
- Parameters: `**kwargs`: lookup conditions.
- Returns: the matching model instance; raises `Model.DoesNotExist` if absent.

**`all(cls) -> QuerySet`**
- Functionality: equivalent to `cls.objects.all()`.
- Returns: `QuerySet`.

**`filter(cls, *args, **kwargs) -> QuerySet`**
- Functionality: equivalent to `cls.objects.filter(...)`.
- Parameters: same as `QuerySet.filter`.
- Returns: `QuerySet`.

- Example:
  ```python
  class Article(BaseModel):
      title = models.CharField(max_length=200)

  a = Article.new({"title": "Hello"})
  Article.update(a.id, title="World")
  obj = Article.one(title="World")
  ```

### 6.2 `djangohelper.db.utils`

**Functionality**: extended wrapper over Django's DB connection layer, exposing the same connection-management and exception objects as `django.db.utils`, useful when working with multiple databases / custom backends.

Exported objects:
- `connections`: a `ConnectionHandler` instance (manages all `DATABASES` connections).
- `connection`: a `DefaultConnectionProxy` proxying the default connection (equivalent to `connections['default']`).
- `router`: a `ConnectionRouter` instance (read/write router).
- `ConnectionHandler` / `ConnectionRouter` / `ConnectionDoesNotExist`: classes.
- Exceptions: `Error` / `InterfaceError` / `DatabaseError` / `DataError` / `OperationalError` / `IntegrityError` / `InternalError` / `ProgrammingError` / `NotSupportedError`.
- `DatabaseErrorWrapper`: DB exception wrapper usable as a context manager or decorator, converting backend exceptions into Django's unified exceptions.
- `load_backend(backend_name)`:
  - Functionality: load a database backend's `base` module by its full name.
  - Parameters: `backend_name` (str), e.g. `'django.db.backends.mysql'`.
  - Returns: the backend `base` module.

---

## 7. Utilities

### 7.1 `djangohelper.number_tool`

**`random_string(n: int = 32) -> str`**
- Functionality: generate a random alphanumeric string from `qwertyuiopasdfghjklzxcvbnm1234567890` (delegates to `astartool`).
- Parameters: `n` (int, default `32`): length.
- Returns: `str`, a random string of length `n`.

**`random_hex_string`**
- Functionality: SM3 hex random string (references `astartool.random.random_hex_string` directly).
- Parameters: same as `astartool`.
- Returns: a hex random string.

### 7.2 `djangohelper.common`

**Functionality**: global constants, error codes, and JWT / response demos reused by other modules and business code.

- Error code constants (int):
  - `ERROR_CODE_UNKNOWN = -1` unknown error
  - `ERROR_CODE_OPERATION_FAILED = 0` operation failed
  - `ERROR_CODE_OPERATION_SUCCESS = 1` operation succeeded
  - `ERROR_CODE_PARTNER_ERROR = 2` invalid parameter
  - `ERROR_CODE_TOKEN_ERROR = 3` token expired
  - `ERROR_CODE_DATABASE_ERROR = 4` database error
  - `ERROR_CODE_LOGINED_ERROR = 5` logged in on another device
  - `ERROR_CODE_ACCOUNT_LOCKED_ERROR = 6` account locked / disabled
  - `ERROR_CODE_IP_TRY_TIME_LIMITED_ERROR = 7` IP login attempts exceeded
  - `ERROR_CODE_ACCOUNT_TRY_TIME_LIMITED_ERROR = 8` account login attempts exceeded
  - `ERROR_CODE_SERVER_ERROR = 99` server under maintenance
- `JSON_DEMO` (dict): response body demo `{successful, data, code, message}`.
- `PAYLOAD_DEMO` (dict): JWT payload demo with `iss`/`sub`/`aud`/`exp`/`nbf`/`iat`/`jti` (all `None`).
- `list_allow_extension` (list): allowed extensions for source dumping (`.py`/`.js`/`.java`/`.html`/`.cpp`/`.c`/`.h`/`.php`, etc.).
- `list_ignore` (list): files/dirs ignored by source dumping (`.git`/`__pycache__/`/`*.egg-info`/`venv/`, etc.).

### 7.3 `djangohelper.requests.requests_helper.request`

**Functionality**: generic HTTP request helper, defaulting to the 253 SMS gateway, for sending SMS / querying balance, etc.

```python
request(method='post', host='smssh1.253.com', port=80,
         service='/msg/balance/json', params={},
         headers={"Content-type": "application/json"}, prefix='http://') -> str
```

- Parameters:
  - `method` (str, default `'post'`): `'get'` or `'post'` (case-insensitive).
  - `host` (str, default `'smssh1.253.com'`): hostname.
  - `port` (int, default `80`): port.
  - `service` (str, default `'/msg/balance/json'`): service path.
  - `params` (dict, default `{}`): request params (query for GET, JSON body for POST).
  - `headers` (dict, default `{"Content-type": "application/json"}`): request headers.
  - `prefix` (str, default `'http://'`): URL scheme prefix.
- Returns: `str`; on success the string form of `res.json()`, otherwise `'it is not a json response'`.
- Example:
  ```python
  from djangohelper.requests.requests_helper import request
  print(request(params={'account': 'xx', 'password': 'xx'}))
  ```

---

## 8. Project Dumper

### 8.1 `djangohelper.project2lines`

**Functionality**: aggregate project source (or a single file / directory) into one text file, convenient for software-copyright filing.

**`file_to_lines(src_file, to_file='out.txt', start_file='\n', end_file='\n')`**
- Functionality: append a single source file's contents to the target file (auto-detecting gbk / utf-8).
- Parameters:
  - `src_file` (str): source file path.
  - `to_file` (str, default `'out.txt'`): output file.
  - `start_file` (str, default `'\n'`): content prepended before the file.
  - `end_file` (str, default `'\n'`): content appended after the file.

**`walk(root, to_file='out.txt', start_file='\n', end_file='\n', allow_extension=list_allow_extension, ignore=list_ignore)`**
- Functionality: recursively walk a directory, calling `file_to_lines` on each matching file.
- Parameters: besides the above, `root` (str) is the root dir; `allow_extension` / `ignore` come from `djangohelper.common`.

**`project_to_lines(src_project, to_file='out.txt', start_file='\n', end_file='\n', allow_extension=list_allow_extension, ignore=list_ignore)`**
- Functionality: dump an entire project into a single file (entry point for copyright filing).
- Parameters: `src_project` (str) is the project root; if `to_file` exists, it interactively asks whether to delete it.
- Returns: `None` (writes `to_file`).

---

## 9. Contrib Apps

### 9.1 `djangohelper.contrib.snowlandauth`

- `SnowlandUser(AbstractUser)`: extended user model.
  - Fields: `telephone` (CharField, max_length=15, unique), `sex` (CharField, max_length=2, default `'F'`), `real_name` (CharField, max_length=15, blank), and role choices `USER_ROLE_CHOICES = (('SU','SuperUser'), ('GA','GroupAdmin'), ('CU','CommonUser'))`.
  - Functionality: adds a unique phone constraint plus real-name / gender info on top of `AbstractUser`.
- `TitleChoice(Enum)`: title enum `SUPERUSER=0` / `ADMIN=1` / `AUDIT=2` / `OPERATOR=3`.
- `CustomBackend(ModelBackend)`:
  - Method `authenticate(self, request, username=None, password=None, **kwargs) -> User|None`
  - Functionality: allow login via `username` / `email` / `telephone`; returns `None` on failure.
  - Parameters: `username` may be username/email/phone; `password` is plaintext.
  - Returns: the matched `SnowlandUser` on success, else `None`.

### 9.2 `djangohelper.contrib.developer`

Developer-platform models built on `BaseModel`:

- `Application(BaseModel)`: an application. Fields `owner` (FK→User), `name`, `access_key`, `access_secret`, `icon` (ImageField, nullable), `create_time`, `update_time`.
- `ApplicationChangeList(BaseModel)`: key-change history. `app_id` (FK→Application), `access_key_before/after`, `access_secret_before/after`, `change_time`.
- `KeyStore(BaseModel)`: public-key storage. `app_id` (FK→Application), `public_key`, `change_time`.

> All three inherit `BaseModel`, so they get `created_time/updated_time` and the `new/update/one/all/filter` convenience methods for free.

---

## 10. CLI

- **`djangohelper/bin/djangohelper-admin.py`**: in-package management command entry, equivalent to `django-admin`, executing `management.execute_from_command_line()`.
- **Root `dh-admin.py`**: scaffolding script that calls system `django-admin startproject/startapp` to generate a `snowland_`-prefixed project and app, and writes `django_socket.xml` (uwsgi config). Parameter: `sys.argv[1]` is the product name.

---

## 11. Package Metadata

### 11.1 `djangohelper.__init__`

- `VERSION = (0, 3, 0, 'final', 0)`: version tuple.
- `__version__` (str): produced by Django `get_version(VERSION)`, currently `'0.3.0'`.
- `setup(set_prefix=True)`:
  - Functionality: configure Django settings, logging and populate the app registry (equivalent to `django.setup`).
  - Parameters: `set_prefix` (bool, default `True`): whether to set the URL resolver prefix.
  - Returns: `None`.
