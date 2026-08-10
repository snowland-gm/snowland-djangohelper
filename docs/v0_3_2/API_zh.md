# snowland-djangohelper API 文档（中文，详细版）

> 版本：0.3.2
> 适用：Python 3.6+ / Django 2.0+（兼容至 5.1）/ DRF 3.11+
> 导入前缀均为 `djangohelper`。

本文档为 0.3.2 相对 0.3.1 的**新增与变更** API 说明，沿用「功能说明 / 入参 / 出参 / 示例」四要素。0.3.1 及更早的通用 API（加密、响应、分页、视图集等）见 `docs/v0_3_1/API_zh.md`。

0.3.2 核心新增：`djangohelper.contrib.snowlandauth` 子模块，提供第三方 OAuth 账户绑定、授权码回调登录、用户资料扩展（含手机号国家码）能力。

---

## 1. 用户模型与资料扩展 / User Models & Profile

### 1.1 `djangohelper.contrib.snowlandauth.models.SnowlandUser`

**功能**：项目默认用户模型（`AUTH_USER_MODEL = 'snowlandauth.SnowlandUser'`），在 Django `AbstractUser` 基础上通过 Mixin 注入手机号（含国家码）与性别字段。

**关键字段**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `username` / `password` / `email` | 继承 `AbstractUser` | 标准 Django 用户字段 |
| `real_name` | `CharField(15)` | 真实姓名，可空 |
| `country_code` | `CharField(5)` | 手机号国家码，**默认 `+86`** |
| `telephone` | `CharField(15)` | 手机号（不含国家码） |
| `gender` | `SmallInteger` | 性别，来自 `GenderMixin` |

#### `SnowlandUser.set_phone(telephone, country_code='')`

- 功能：写入手机号并按需补全国家码（缺省 `+86`）。
- 入参：
  - `telephone` (str)：手机号主体（不含 `+` 前缀国家码）。
  - `country_code` (str, 可选)：国家码，如 `'+86'` / `'+1'`；为空时取 `PhoneMixin.DEFAULT_COUNTRY_CODE`（`'+86'`）。
- 出参：无（`None`）。

#### `SnowlandUser.full_phone`

- 功能：返回完整国际号码 `country_code + telephone`。
- 出参：`str`，如 `'+8613800000000'`。

### 1.2 `djangohelper.contrib.snowlandauth.auth_mixins`

| Mixin | 注入字段 / 能力 | 说明 |
| --- | --- | --- |
| `PhoneMixin` | `country_code`、`telephone`、`set_phone()`、`full_phone` | 手机号 + 国家码；`unique_together=(('country_code','telephone'),)` |
| `GenderMixin` | `gender` | 性别枚举 |

`PhoneMixin.DEFAULT_COUNTRY_CODE = '+86'`，新增账户未显式传入国家码时默认中国大陆。

---

## 2. OAuth 客户端 / OAuth Clients

### 2.1 `djangohelper.contrib.snowlandauth.oauth_mixins`

所有第三方平台通过一个 `OAuthMixin` 抽象基类 + 各平台子类实现，回调逻辑统一委托给 `snowland_authsdk` 的 `BaseOAuthClient`。

**平台 Mixin 一览**：

| Mixin | `OAUTH_TYPE` | 底层客户端 | 说明 |
| --- | --- | --- | --- |
| `QQOAuthMixin` | `qq` | `QQOAuthClient(BaseOAuthClient)` | 本地基于 SDK base 实现，token 为 query-string、openid 经 JSONP `me` 接口解析 |
| `WechatOAuthMixin` | `wechat` | `WeChatOAuthClient` | 来自 `snowland_authsdk.oauth` |
| `CSDNOAuthMixin` | `csdn` | `CSDNOAuthClient` | 来自 `snowland_authsdk.oauth` |
| `GithubOAuthMixin` | `github` | `GitHubOAuthClient` | 来自 `snowland_authsdk.oauth` |
| `AliyunOAuthMixin` | `aliyun` | `AliyunOAuthClient` | 来自 `snowland_authsdk.oauth` |
| `AlipayOAuthMixin` | `alipay` | `AlipayOAuthClient` | 来自 `snowland_authsdk.oauth` |
| `TaobaoOAuthMixin` | `taobao` | `TaobaoOAuthClient(BaseOAuthClient)` | 本地基于 SDK base 实现，无独立 userinfo，openid 取自 token 的 `taobao_user_id` |

> QQ / Taobao 的 SDK 尚未提供现成客户端，故在包内继承 `snowland_authsdk.oauth.base.BaseOAuthClient` 自定义（端点与解析钩子），与其余平台使用同一套 `get_authorize_url` / `resolve_identity` 流程。

#### `OAuthMixin.get_authorize_url(state='', scope='', **extra) -> str`

- 功能：生成第三方授权页 URL，浏览器应跳转至此。
- 入参：
  - `state` (str)：CSRF 随机串，回调时回传校验。
  - `scope` (str)：请求的 OAuth scope。
  - `extra`：透传给 SDK 客户端的附加参数。
- 出参：`str`，完整授权 URL。
- 异常：`NotImplementedError` —— 未配置 `SDK_CLIENT`。

#### `OAuthMixin.resolve_identity(code, state='', **extra) -> tuple[str, str, dict]`

- 功能：用授权码 `code` 完成回调，换取身份。
- 入参：
  - `code` (str)：provider 回调返回的授权码。
  - `state` (str)：回调回传的 state（由调用方校验）。
- 出参：`(openid, unionid, userinfo)`：
  - `openid` (str)：平台下发的稳定用户标识。
  - `unionid` (str)：跨应用联合 id（平台不支持时为空串）。
  - `userinfo` (dict)：归一化用户信息（或 token 原文）。
- 异常：`RuntimeError` —— 授权失败或返回数据缺少 openid。

#### `get_oauth_client(provider) -> type`

- 功能：根据 `provider` 码（`qq`/`wechat`/`csdn`/`github`/`aliyun`/`alipay`/`taobao`）返回对应 Mixin 类。
- 入参：`provider` (str)。
- 出参：Mixin 类。
- 异常：`AuthFlowError` —— 不支持的平台。

---

## 3. 业务服务层 / Auth Flow

### 3.1 `djangohelper.contrib.snowlandauth.auth_flow`

框架无关的业务逻辑，DRF 视图委托给这些函数，便于脱离 request 进行单元测试。

#### `register_user(username, password, telephone='', country_code='', email='', **extra) -> SnowlandUser`

- 功能：注册全新本地账号（密码以哈希存储）。
- 入参：
  - `username` (str)：登录名。
  - `password` (str)：明文密码。
  - `telephone` (str, 可选)：手机号（不含国家码）。
  - `country_code` (str, 可选)：国家码，缺省 `+86`。
  - `email` (str, 可选)：邮箱。
  - `extra`：其他 `SnowlandUser` 字段（如 `real_name`、`gender`）。
- 出参：新建用户实例。
- 异常：`AuthFlowError` —— 用户名已存在。

#### `login_by_password(request, username, password) -> SnowlandUser`

- 功能：以「用户名 / 邮箱 / 手机号（含 `+86` 或 `+86 xxx` 写法）」+ 密码登录并开启会话。
- 入参：`request` (HttpRequest)、`username` (str)、`password` (str)。
- 出参：已认证用户。
- 异常：`AuthFlowError` —— 凭证错误或被禁用。

#### `bind_or_login_oauth(request, provider, openid, unionid='', telephone='', country_code='', email='', real_name='') -> tuple[SnowlandUser, bool]`

- 功能：**匿名** OAuth 入口：已绑定则刷新并返回原用户，否则自动注册并绑定后登录。
- 入参：
  - `provider` (str)、`openid` (str)、`unionid` (str, 可选)。
  - `telephone` / `country_code` / `email` / `real_name`：仅自动注册新用户时使用。
- 出参：`(user, created)`，其中 `created=True` 表示本次新建。
- 异常：`AuthFlowError` —— openid 为空或账号被禁用。

#### `bind_oauth_for_authenticated_user(request, user, provider, openid, unionid='') -> dict`

- 功能：**已登录**用户绑定新平台：若无冲突直接绑定；若 `openid` 已被他号占用，则创建合并请求。
- 出参：
  - `{'status': 'bound'}` 绑定成功。
  - `{'status': 'merge_required', 'merge_request_id': <id>}` 需账号合并决策。

#### `resolve_merge_request(request, merge_request_id, keep) -> SnowlandUser`

- 功能：执行账号合并决策。
- 入参：
  - `merge_request_id` (int)。
  - `keep` (str)：`'source'`（保留当前登录用户）或 `'target'`（保留已拥有该身份的他号）。
- 出参：被保留的用户实例（合并后需重新登录）。
- 异常：`AuthFlowError` —— `keep` 非法或请求已处理。

#### `exchange_oauth_code(request, provider, code, state='', scope='', **profile) -> tuple[SnowlandUser, bool]`

- 功能：授权回调统一入口（匿名场景）：内部调用 `resolve_identity(code)` 换取 openid 后转交 `bind_or_login_oauth`，`profile` 为自动注册所需的 `telephone`/`country_code`/`email`/`real_name`。
- 出参：`(user, created)`。

#### `bind_oauth_code_for_authenticated_user(request, user, provider, code, state='') -> dict`

- 功能：授权回调统一入口（已登录场景）：用 `code` 换取 openid 后转交 `bind_oauth_for_authenticated_user`，返回 `{'status': ...}` 字典。

---

## 4. DRF 视图 / Views

### 4.1 `djangohelper.contrib.snowlandauth.views`

薄适配器，将 HTTP 请求翻译为 `auth_flow` 调用，统一返回 `djangohelper.responses.APIResponse`。

| 视图 | 方法 | 路径语义 | 说明 |
| --- | --- | --- | --- |
| `RegisterView` | POST | 注册 | 入参 `username`/`password`/`country_code`(默认`+86`)/`telephone`/`email`/`real_name` |
| `PasswordLoginView` | POST | 密码登录 | 入参 `username`/`password` |
| `OAuthAuthorizeView` | GET | 获取授权 URL | 入参 `provider`/`state`/`scope`，返回 `authorize_url` |
| `OAuthCallbackView` | POST | 授权回调 | 入参 `provider`/`code`/`state`；匿名走 `exchange_oauth_code`，已登录走 `bind_oauth_code_for_authenticated_user` |
| `OAuthBindView` | POST | 已登录绑定 | 入参 `provider`/`openid`（或直接 `code` 回调） |
| `AccountMergeView` | POST | 合并决策 | 入参 `merge_request_id`/`keep` |

---

## 5. 配置 / Settings

在 Django `settings.py` 中声明各平台 client 凭据（键为 `OAUTH_TYPE` 的大写）：

```python
AUTH_USER_MODEL = 'snowlandauth.SnowlandUser'

SNOWLANDAUTH_OAUTH = {
    'QQ':     {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
    'WECHAT': {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
    'CSDN':   {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
    'GITHUB': {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
    'ALIYUN': {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
    'ALIPAY': {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
    'TAOBAO': {'CLIENT_ID': '...', 'CLIENT_SECRET': '...', 'REDIRECT_URI': 'https://example.com/oauth/callback'},
}
```

依赖：`snowland-authsdk>=0.2`（已写入 `requirements.txt` 与 `pyproject.toml` 的 `dependencies`）。

---

## 6. 包元数据 / Package Metadata

- 版本：`0.3.2`
- 新增依赖：`snowland-authsdk>=0.2`
- 构建：PEP 621 / PEP 517（`pyproject.toml`）
