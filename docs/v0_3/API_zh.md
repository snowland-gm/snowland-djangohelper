# snowland-djangohelper API 文档（中文，详细版）

> 版本：0.3.0
> 适用：Python 3.6+ / Django 2.0+（兼容至 5.1）/ DRF 3.11+
> 导入前缀均为 `djangohelper`。

本文档为每个公开 API 提供「功能说明 / 入参 / 出参 / 示例」四要素。

---

## 1. 认证与加密 / Auth & Crypto

### 1.1 `djangohelper.auth.hasher`

**功能**：提供基于国密 **SM3** 的 Django 密码哈希器，全部继承 `django.contrib.auth.hashers.BasePasswordHasher`，可无缝接入 Django 密码框架（`settings.PASSWORD_HASHERS`、`check_password`、`make_password` 等）。

| 类 | `algorithm` | 关键属性 | 说明 |
| --- | --- | --- | --- |
| `SM3PasswordHasher` | `sm3` | — | 带盐 SM3 哈希，推荐默认使用 |
| `UnsaltedSM3PasswordHasher` | `unsalted_sm3` | — | 无盐 SM3（不安全，仅用于兼容历史数据） |
| `PBKDF2_SM3PasswordHasher` | `pbkdf2_sm3` | `iterations=100000` | PBKDF2 迭代 + SM3 摘要 |
| `BCryptSM3PasswordHasher` | `bcrypt_sm3` | `rounds=12` | bcrypt 包裹 SM3（需安装 `bcrypt`） |
| `SM3KDFPasswordHasher` | `sm3kdf` | `iterations=100000` | SM3 KDF 密钥派生 |

#### 通用方法（所有子类均提供）

**`encode(password, salt) -> str`**
- 功能：把明文密码编码为存储哈希串。
- 入参：
  - `password` (str)：明文密码（不能为 `None`）。
  - `salt` (str)：盐值，不含 `$`。
- 出参：`str`，格式为 `algorithm$salt$hash`（不同子类分隔段数略有差异）。

**`verify(password, encoded) -> bool`**
- 功能：校验明文密码与已存储哈希是否匹配（常量时间比较，防时序攻击）。
- 入参：
  - `password` (str)：待校验明文。
  - `encoded` (str)：已存储的哈希串。
- 出参：`bool`，匹配返回 `True`。

**`safe_summary(encoded) -> collections.OrderedDict`**
- 功能：返回用于后台展示的摘要信息。
- 入参：`encoded` (str)：已存储哈希串。
- 出参：`OrderedDict`，含 `algorithm`、`salt`（掩码）、`hash`（掩码）等键。

**`must_update(encoded) -> bool`**（部分子类提供，如 `PBKDF2_SM3PasswordHasher`、`BCryptSM3PasswordHasher`）
- 功能：当哈希的迭代次数 / rounds 与当前类定义不一致时返回 `True`，提示需重新哈希。
- 入参：`encoded` (str)。
- 出参：`bool`。

**`harden_runtime(password, encoded)`**（部分子类提供）
- 功能：补齐到当前迭代次数所需的额外计算开销，使不同哈希的校验耗时一致，抵御用户枚举。
- 入参：`password` (str)、`encoded` (str)。
- 出参：无（`None`）。

#### 配置示例

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

**功能**：基于 Django `django.utils.crypto.pbkdf2` 的封装，使用 SM3 作为伪随机函数（PRF）进行密钥派生。

```python
pbkdf2(password, salt, iterations, dklen=0, digest=pysmx.SM3.SM3Type) -> bytes
```

- 入参：
  - `password` (str|bytes)：主密码。
  - `salt` (str|bytes)：盐。
  - `iterations` (int)：迭代次数。
  - `dklen` (int, 默认 `0`)：派生密钥长度，`0` 表示使用摘要默认长度。
  - `digest` (可调用, 默认 `pysmx.SM3.SM3Type`)：哈希算法对象。
- 出参：`bytes`，派生密钥。
- 示例：
  ```python
  from djangohelper.utils.crypto import pbkdf2
  key = pbkdf2('secret', 'salt', 100000)
  ```

---

## 2. 统一响应 / Unified Response

### 2.1 `djangohelper.responses.APIResponse`

**功能**：继承 `rest_framework.response.Response`，在构造时自动把业务数据包装为统一 JSON 结构，保证所有接口返回格式一致。

```python
APIResponse(data=None, status=None, template_name=None, headers=None,
            exception=False,
            content_type='application/json; charset=utf-8 ',
            successful=True, code=ERROR_CODE_OPERATION_SUCCESS, message=None)
```

- 入参：
  - `data` (任意, 默认 `None`)：业务数据，最终置于 `data` 字段。
  - `status` (int|str, 默认 `None`)：HTTP 状态码，透传给 DRF。
  - `template_name` (str, 默认 `None`)：模板名（通常不使用）。
  - `headers` (dict, 默认 `None`)：响应头。
  - `exception` (bool, 默认 `False`)：是否为异常响应。
  - `content_type` (str, 默认 `'application/json; charset=utf-8 '`)：响应内容类型。
  - `successful` (bool, 默认 `True`)：业务成功标志。
  - `code` (int, 默认 `ERROR_CODE_OPERATION_SUCCESS=1`)：业务错误码。
  - `message` (str|None, 默认 `None`)：提示信息。
- 出参：`rest_framework.response.Response` 实例；其 `.data` 为：
  ```json
  { "successful": true, "code": 1, "message": null, "data": { } }
  ```
- 示例：
  ```python
  from djangohelper.responses import APIResponse
  return APIResponse(data={"id": 1}, message="ok")
  ```

---

## 3. 分页 / Pagination

### 3.1 `djangohelper.pagination.BasePageNumberPagination`

**功能**：继承 `rest_framework.pagination.PageNumberPagination`，重写 `get_paginated_response`，使分页结果也采用 `APIResponse` 统一结构。

- 入参（方法级）：
  - `get_paginated_response(self, data)`：`data` 为已序列化后的当前页数据列表。
- 出参：`APIResponse`，`.data` 为：
  ```json
  { "successful": true, "code": 1, "message": null,
    "data": { "count": 100, "next": "url", "previous": null, "results": [ ] } }
  ```
- 示例（与 `SelfModelViewSet` 配合即可自动生效，无需手动调用）。

### 3.2 `djangohelper.viewhelper.paginator.generate_paginator_result`

**功能**：对 queryset 进行分页，并返回「当前页对象 + 页码队列」字典，便于在 Django 模板中渲染分页导航。

```python
generate_paginator_result(queryset, per_page, orphans=0,
                          allow_empty_first_page=True,
                          length_pagequeue=5, page=1,
                          key_contacts='contacts', key_index='ind') -> dict
```

- 入参：
  - `queryset` (QuerySet|dict)：待分页数据；为 QuerySet 时内部用 `django.core.serializers` 转 JSON 再分页，为 dict 时直接使用。
  - `per_page` (int)：每页条数。
  - `orphans` (int, 默认 `0`)：允许合并到上一页的孤儿条数。
  - `allow_empty_first_page` (bool, 默认 `True`)：首页是否允许为空。
  - `length_pagequeue` (int, 默认 `5`)：显示的页码数量。
  - `page` (int, 默认 `1`)：目标页码。
  - `key_contacts` (str, 默认 `'contacts'`)：返回字典中「当前页」的键名。
  - `key_index` (str, 默认 `'ind'`)：返回字典中「页码队列」的键名。
- 出参：`dict`，形如：
  ```python
  {'contacts': <Page 对象>, 'ind': [1, 2, 3, 4, 5]}
  ```
  其中 `contacts` 可用于模板 `{{ contacts.object_list }}` 等。
- 示例：
  ```python
  from djangohelper.viewhelper.paginator import generate_paginator_result
  ctx = generate_paginator_result(Article.objects.all(), per_page=10, page=2)
  ```

---

## 4. 视图集 / ViewSets

### 4.1 `djangohelper.viewsets.SelfModelViewSet`

**功能**：继承 `rest_framework.viewsets.ModelViewSet`，将 `list` / `retrieve` / `create` / `update` / `destroy` 五种动作的返回值统一包装为 `APIResponse`，省去在每个视图里手动构造统一响应。

- 入参：作为 DRF ViewSet 使用，子类需提供 `queryset` 与 `serializer_class`（同 ModelViewSet）。
- 出参：各动作返回 `APIResponse`：
  - `list`：成功 `code=1`，`data` 为序列化列表（分页时含 `count/next/previous/results`）。
  - `retrieve`：`data` 为单条序列化数据。
  - `create`：HTTP `201`，`data` 为新创建对象。
  - `update`：`data` 为更新后对象。
  - `destroy`：HTTP `204`，无 body。
- 示例：
  ```python
  from djangohelper.viewsets import SelfModelViewSet
  class ArticleViewSet(SelfModelViewSet):
      queryset = Article.objects.all()
      serializer_class = ArticleSerializer
  ```

---

## 5. 权限 / Permissions

**功能**：均继承 `rest_framework.permissions.BasePermission`，实现 `has_permission(request, view) -> bool`，可挂在 DRF 视图的 `permission_classes` 上。未登录（`is_anonymous`）统一返回 `False`，除非另有说明。

| 类 | 规则（返回 `True` 的条件） |
| --- | --- |
| `AdminPermission` | 已登录且属于 `管理员` 分组，并且 `user.is_superuser` |
| `AuditPermission` | `user.is_auditor` 或 `user.is_superuser` |
| `OperatorPermission` | `user.is_operator` 或 `user.is_superuser` |
| `SuperuserPermission` | `user.is_superuser` |
| `AllPermission` | 任意已认证（`is_authenticated`）用户 |

- 入参：`has_permission(self, request, view)`
  - `request`：DRF `Request`，通过 `request.user` 取当前用户。
  - `view`：当前视图实例。
- 出参：`bool`，是否放行。
- 示例：
  ```python
  from djangohelper.permissions import AdminPermission
  class MyView(APIView):
      permission_classes = [AdminPermission]
  ```

---

## 6. 数据库模型 / Database Models

### 6.1 `djangohelper.db.models.BaseModel`

**功能**：抽象基类模型（`Meta.abstract = True`），为所有业务模型提供统一的 `created_time` / `updated_time` 时间戳字段，以及一组便捷的查询 / 写入类方法。

- 字段：
  - `created_time` (DateTimeField, `auto_now_add=True`)：记录创建时间。
  - `updated_time` (DateTimeField, `auto_now=True`)：记录更新时间。

类方法：

**`new(cls, form) -> Model`**
- 功能：根据字段字典创建并保存一条记录。
- 入参：`form` (dict)：字段名→值；仅写入值非空的项。
- 出参：新建并 `save()` 后的模型实例。

**`update(cls, id_, **kwargs) -> None`**
- 功能：按主键更新指定字段。
- 入参：`id_` (任意)：主键值；`**kwargs`：待更新字段（值为 list 时取第一个元素）。
- 出参：无。

**`one(cls, **kwargs) -> Model`**
- 功能：等价 `cls.objects.get(**kwargs)`。
- 入参：`**kwargs`：查询条件。
- 出参：匹配的模型实例；不存在则抛 `Model.DoesNotExist`。

**`all(cls) -> QuerySet`**
- 功能：等价 `cls.objects.all()`。
- 出参：`QuerySet`。

**`filter(cls, *args, **kwargs) -> QuerySet`**
- 功能：等价 `cls.objects.filter(...)`。
- 入参：同 `QuerySet.filter`。
- 出参：`QuerySet`。

- 示例：
  ```python
  class Article(BaseModel):
      title = models.CharField(max_length=200)

  a = Article.new({"title": "Hello"})
  Article.update(a.id, title="World")
  obj = Article.one(title="World")
  ```

### 6.2 `djangohelper.db.utils`

**功能**：对 Django 数据库连接层的扩展封装，对外暴露与 `django.db.utils` 同名的连接管理与异常对象，便于在需要使用多数据库 / 自定义后端时直接引用。

导出对象：
- `connections`：`ConnectionHandler` 实例（管理所有 `DATABASES` 连接）。
- `connection`：`DefaultConnectionProxy`，代理默认连接（等价 `connections['default']`）。
- `router`：`ConnectionRouter` 实例（读写路由）。
- `ConnectionHandler` / `ConnectionRouter` / `ConnectionDoesNotExist`：类。
- 异常类：`Error` / `InterfaceError` / `DatabaseError` / `DataError` / `OperationalError` / `IntegrityError` / `InternalError` / `ProgrammingError` / `NotSupportedError`。
- `DatabaseErrorWrapper`：数据库异常包装器，可用作上下文管理器或装饰器，把后端异常转换为 Django 统一异常。
- `load_backend(backend_name)`：
  - 功能：按完整后端名加载数据库后端 `base` 模块。
  - 入参：`backend_name` (str)，如 `'django.db.backends.mysql'`。
  - 出参：后端 `base` 模块。

---

## 7. 通用工具 / Utilities

### 7.1 `djangohelper.number_tool`

**`random_string(n: int = 32) -> str`**
- 功能：生成由 `qwertyuiopasdfghjklzxcvbnm1234567890` 组成的随机字母数字串（基于标准库 `secrets.SystemRandom` 实现）。
- 入参：`n` (int, 默认 `32`)：长度。
- 出参：`str`，长度 `n` 的随机串。

**`random_hex_string(n: int = 32, upper: bool = False) -> str`**
- 功能：生成十六进制随机串（基于标准库 `secrets.SystemRandom` 实现）。
- 入参：`n` (int, 默认 `32`)：长度；`upper` (bool, 默认 `False`)：是否输出大写。
- 出参：十六进制随机串。

### 7.2 `djangohelper.common`

**功能**：存放全局常量、错误码与 JWT/响应示例，供其他模块与业务代码复用。

- 错误码常量（int）：
  - `ERROR_CODE_UNKNOWN = -1` 未知错误
  - `ERROR_CODE_OPERATION_FAILED = 0` 操作失败
  - `ERROR_CODE_OPERATION_SUCCESS = 1` 操作成功
  - `ERROR_CODE_PARTNER_ERROR = 2` 参数有误
  - `ERROR_CODE_TOKEN_ERROR = 3` token 失效
  - `ERROR_CODE_DATABASE_ERROR = 4` 数据库错误
  - `ERROR_CODE_LOGINED_ERROR = 5` 已在其他设备登录
  - `ERROR_CODE_ACCOUNT_LOCKED_ERROR = 6` 账户被锁定/禁用
  - `ERROR_CODE_IP_TRY_TIME_LIMITED_ERROR = 7` 同终端登录失败次数超限
  - `ERROR_CODE_ACCOUNT_TRY_TIME_LIMITED_ERROR = 8` 同账户登录失败次数超限
  - `ERROR_CODE_SERVER_ERROR = 99` 后台维护中
- `JSON_DEMO` (dict)：响应体示例 `{successful, data, code, message}`。
- `PAYLOAD_DEMO` (dict)：JWT payload 示例，含 `iss`/`sub`/`aud`/`exp`/`nbf`/`iat`/`jti`（均为 `None`）。
- `list_allow_extension` (list)：源码打包允许的后缀（`.py`/`.js`/`.java`/`.html`/`.cpp`/`.c`/`.h`/`.php` 等）。
- `list_ignore` (list)：源码打包忽略的文件/目录（`.git`/`__pycache__/`/`*.egg-info`/`venv/` 等）。

### 7.3 `djangohelper.requests.requests_helper.request`

**功能**：通用 HTTP 请求辅助函数，默认指向 253 短信网关，用于发送短信 / 查询余额等。

```python
request(method='post', host='smssh1.253.com', port=80,
         service='/msg/balance/json', params={},
         headers={"Content-type": "application/json"}, prefix='http://') -> str
```

- 入参：
  - `method` (str, 默认 `'post'`)：`'get'` 或 `'post'`（不区分大小写）。
  - `host` (str, 默认 `'smssh1.253.com'`)：主机名。
  - `port` (int, 默认 `80`)：端口。
  - `service` (str, 默认 `'/msg/balance/json'`)：服务路径。
  - `params` (dict, 默认 `{}`)：请求参数（GET 为 query，POST 为 JSON body）。
  - `headers` (dict, 默认 `{"Content-type": "application/json"}`)：请求头。
  - `prefix` (str, 默认 `'http://'`)：URL 协议前缀。
- 出参：`str`；成功返回 `res.json()` 的字符串形式，非 JSON 响应返回 `'it is not a json response'`。
- 示例：
  ```python
  from djangohelper.requests.requests_helper import request
  print(request(params={'account': 'xx', 'password': 'xx'}))
  ```

---

## 8. 源码打包 / Project Dumper

### 8.1 `djangohelper.project2lines`

**功能**：将项目源码（或单个文件 / 目录）汇总输出为单个文本文件，便于申请软件著作权时提交材料。

**`file_to_lines(src_file, to_file='out.txt', start_file='\n', end_file='\n')`**
- 功能：把单个源文件内容追加写入目标文件（自动识别 gbk / utf-8 编码）。
- 入参：
  - `src_file` (str)：源文件路径。
  - `to_file` (str, 默认 `'out.txt'`)：输出文件。
  - `start_file` (str, 默认 `'\n'`)：文件头附加内容。
  - `end_file` (str, 默认 `'\n'`)：文件尾附加内容。

**`walk(root, to_file='out.txt', start_file='\n', end_file='\n', allow_extension=list_allow_extension, ignore=list_ignore)`**
- 功能：递归遍历目录，对符合条件的文件逐一调用 `file_to_lines`。
- 入参：除上述外，`root` (str) 为根目录；`allow_extension` / `ignore` 见 `djangohelper.common`。

**`project_to_lines(src_project, to_file='out.txt', start_file='\n', end_file='\n', allow_extension=list_allow_extension, ignore=list_ignore)`**
- 功能：将整个项目打包为单文件（申请软著入口）。
- 入参：`src_project` (str) 为项目根目录；若 `to_file` 已存在会交互询问是否删除。
- 出参：无（写入 `to_file`）。

---

## 9. 业务应用 / Contrib Apps

### 9.1 `djangohelper.contrib.snowlandauth`

- `SnowlandUser(AbstractUser)`：扩展用户模型。
  - 字段：`telephone` (CharField, max_length=15, 唯一)、`sex` (CharField, max_length=2, 默认 `'F'`)、`real_name` (CharField, max_length=15, 可空)；角色选项 `USER_ROLE_CHOICES = (('SU','SuperUser'), ('GA','GroupAdmin'), ('CU','CommonUser'))`。
  - 功能：在 `AbstractUser` 基础上增加手机号唯一约束与实名/性别信息。
- `TitleChoice(Enum)`：职务枚举 `SUPERUSER=0` / `ADMIN=1` / `AUDIT=2` / `OPERATOR=3`。
- `CustomBackend(ModelBackend)`：
  - 方法 `authenticate(self, request, username=None, password=None, **kwargs) -> User|None`
  - 功能：支持用 `username` / `email` / `telephone` 任一字段登录；校验失败返回 `None`。
  - 入参：`username` 可为用户名/邮箱/手机号；`password` 明文。
  - 出参：匹配且密码正确返回 `SnowlandUser`，否则 `None`。

### 9.2 `djangohelper.contrib.developer`

基于 `BaseModel` 的开发者平台模型：

- `Application(BaseModel)`：应用。字段 `owner` (FK→User)、`name`、`access_key`、`access_secret`、`icon` (ImageField，可空)、`create_time`、`update_time`。
- `ApplicationChangeList(BaseModel)`：密钥变更记录。`app_id` (FK→Application)、`access_key_before/after`、`access_secret_before/after`、`change_time`。
- `KeyStore(BaseModel)`：公钥存储。`app_id` (FK→Application)、`public_key`、`change_time`。

> 三个模型均继承 `BaseModel`，自带 `created_time/updated_time` 与 `new/update/one/all/filter` 便捷方法。

---

## 10. 命令行 / CLI

- **`djangohelper/bin/djangohelper-admin.py`**：包内管理命令入口，等价于 `django-admin`，执行 `management.execute_from_command_line()`。
- **仓库根 `dh-admin.py`**：脚手架脚本，调用系统 `django-admin startproject/startapp` 生成带 `snowland_` 前缀的项目与应用，并写出 `django_socket.xml`（uwsgi 配置）。入参：`sys.argv[1]` 为产品名。

---

## 11. 包元数据 / Package Metadata

### 11.1 `djangohelper.__init__`

- `VERSION = (0, 3, 0, 'final', 0)`：版本元组。
- `__version__` (str)：由 Django `get_version(VERSION)` 生成，当前为 `'0.3.0'`。
- `setup(set_prefix=True)`：
  - 功能：配置 Django settings、日志并填充 app 注册表（等价 `django.setup`）。
  - 入参：`set_prefix` (bool, 默认 `True`)：是否设置 URL 解析前缀。
  - 出参：无。
