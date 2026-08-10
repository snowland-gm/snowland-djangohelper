# snowland-djangohelper API Documentation (English, detailed)

> Version: 0.3.2
> Compatible with: Python 3.6+ / Django 2.0+ (up to 5.1) / DRF 3.11+
> All imports use the `djangohelper` prefix.

This document describes the **new and changed** APIs introduced in 0.3.2 relative to 0.3.1, following the "description / params / returns / example" format. For the general APIs of 0.3.1 and earlier (crypto, responses, pagination, viewsets, etc.), see `docs/v0_3_1/API_en.md`.

The headline addition in 0.3.2 is the `djangohelper.contrib.snowlandauth` submodule, providing third-party OAuth account binding, authorization-code callback login, and user-profile extensions (including a phone country code).

---

## 1. User Models & Profile

### 1.1 `djangohelper.contrib.snowlandauth.models.SnowlandUser`

**Purpose**: The default user model (`AUTH_USER_MODEL = 'snowlandauth.SnowlandUser'`), extending Django `AbstractUser` with phone (with country code) and gender mixins.

**Key fields**:

| Field | Type | Notes |
| --- | --- | --- |
| `username` / `password` / `email` | from `AbstractUser` | standard Django user fields |
| `real_name` | `CharField(15)` | real name, blank |
| `country_code` | `CharField(5)` | phone country code, **defaults to `+86`** |
| `telephone` | `CharField(15)` | phone number (without country code) |
| `gender` | `SmallInteger` | from `GenderMixin` |

#### `SnowlandUser.set_phone(telephone, country_code='')`

- Purpose: store the phone number and fill in the country code (defaults to `+86` if omitted).
- Params:
  - `telephone` (str): phone body (without a `+`-prefixed country code).
  - `country_code` (str, optional): e.g. `'+86'` / `'+1'`; falls back to `PhoneMixin.DEFAULT_COUNTRY_CODE` (`'+86'`).
- Returns: `None`.

#### `SnowlandUser.full_phone`

- Purpose: the full international number `country_code + telephone`.
- Returns: `str`, e.g. `'+8613800000000'`.

### 1.2 `djangohelper.contrib.snowlandauth.auth_mixins`

| Mixin | Fields / capabilities | Notes |
| --- | --- | --- |
| `PhoneMixin` | `country_code`, `telephone`, `set_phone()`, `full_phone` | `unique_together=(('country_code','telephone'),)` |
| `GenderMixin` | `gender` | gender enum |

`PhoneMixin.DEFAULT_COUNTRY_CODE = '+86'`; new accounts without an explicit country code default to mainland China.

---

## 2. OAuth Clients

### 2.1 `djangohelper.contrib.snowlandauth.oauth_mixins`

Every third-party platform is implemented through an `OAuthMixin` abstract base plus a per-platform subclass. The callback logic is delegated to `snowland_authsdk`'s `BaseOAuthClient`.

**Platform mixins**:

| Mixin | `OAUTH_TYPE` | Underlying client | Notes |
| --- | --- | --- | --- |
| `QQOAuthMixin` | `qq` | `QQOAuthClient(BaseOAuthClient)` | local subclass of SDK base; token is query-string, openid parsed from JSONP `me` endpoint |
| `WechatOAuthMixin` | `wechat` | `WeChatOAuthClient` | from `snowland_authsdk.oauth` |
| `CSDNOAuthMixin` | `csdn` | `CSDNOAuthClient` | from `snowland_authsdk.oauth` |
| `GithubOAuthMixin` | `github` | `GitHubOAuthClient` | from `snowland_authsdk.oauth` |
| `AliyunOAuthMixin` | `aliyun` | `AliyunOAuthClient` | from `snowland_authsdk.oauth` |
| `AlipayOAuthMixin` | `alipay` | `AlipayOAuthClient` | from `snowland_authsdk.oauth` |
| `TaobaoOAuthMixin` | `taobao` | `TaobaoOAuthClient(BaseOAuthClient)` | local subclass of SDK base; no standalone userinfo, openid taken from token's `taobao_user_id` |

> The SDK does not yet ship ready-made QQ / Taobao clients, so they subclass `snowland_authsdk.oauth.base.BaseOAuthClient` in-package (with endpoint and parse hooks) and share the same `get_authorize_url` / `resolve_identity` flow as the others.

#### `OAuthMixin.get_authorize_url(state='', scope='', **extra) -> str`

- Purpose: build the provider authorization URL the browser should be redirected to.
- Params:
  - `state` (str): CSRF nonce echoed back by the provider.
  - `scope` (str): requested OAuth scope.
  - `extra`: extra params forwarded to the SDK client.
- Returns: `str`, the full authorization URL.
- Raises: `NotImplementedError` when `SDK_CLIENT` is not configured.

#### `OAuthMixin.resolve_identity(code, state='', **extra) -> tuple[str, str, dict]`

- Purpose: complete the callback for an authorization `code` and resolve the identity.
- Params:
  - `code` (str): authorization code returned by the provider.
  - `state` (str): state echoed back (validated by the caller).
- Returns: `(openid, unionid, userinfo)`:
  - `openid` (str): stable provider user identifier.
  - `unionid` (str): cross-app union id (empty string if unsupported).
  - `userinfo` (dict): normalized user profile (or raw token).
- Raises: `RuntimeError` on failure or missing openid.

#### `get_oauth_client(provider) -> type`

- Purpose: map a `provider` code (`qq`/`wechat`/`csdn`/`github`/`aliyun`/`alipay`/`taobao`) to its mixin class.
- Params: `provider` (str).
- Returns: the mixin class.
- Raises: `AuthFlowError` for unsupported providers.

---

## 3. Service Layer / Auth Flow

### 3.1 `djangohelper.contrib.snowlandauth.auth_flow`

Framework-agnostic business logic that the DRF views delegate to, keeping the rules testable without a request object.

#### `register_user(username, password, telephone='', country_code='', email='', **extra) -> SnowlandUser`

- Purpose: register a brand-new local account (password stored hashed).
- Params:
  - `username` (str): login name.
  - `password` (str): plaintext password.
  - `telephone` (str, optional): phone (without country code).
  - `country_code` (str, optional): country code, defaults to `+86`.
  - `email` (str, optional): email.
  - `extra`: other `SnowlandUser` fields (e.g. `real_name`, `gender`).
- Returns: the created user instance.
- Raises: `AuthFlowError` when the username already exists.

#### `login_by_password(request, username, password) -> SnowlandUser`

- Purpose: log in with "username / email / phone (with `+86` or `+86 xxx`)" + password and start a session.
- Params: `request` (HttpRequest), `username` (str), `password` (str).
- Returns: the authenticated user.
- Raises: `AuthFlowError` on bad credentials or a disabled account.

#### `bind_or_login_oauth(request, provider, openid, unionid='', telephone='', country_code='', email='', real_name='') -> tuple[SnowlandUser, bool]`

- Purpose: **anonymous** OAuth entry — refresh and return the existing user if already bound, otherwise auto-register, bind and log in.
- Params:
  - `provider` (str), `openid` (str), `unionid` (str, optional).
  - `telephone` / `country_code` / `email` / `real_name`: only used when auto-registering a new user.
- Returns: `(user, created)` where `created=True` means a new user was created.
- Raises: `AuthFlowError` on empty openid or a disabled account.

#### `bind_oauth_for_authenticated_user(request, user, provider, openid, unionid='') -> dict`

- Purpose: **authenticated** user binding a new platform — binds directly if free, otherwise creates a merge request when the `openid` is owned by another account.
- Returns:
  - `{'status': 'bound'}` on success.
  - `{'status': 'merge_required', 'merge_request_id': <id>}` when a merge decision is required.

#### `resolve_merge_request(request, merge_request_id, keep) -> SnowlandUser`

- Purpose: apply an account-merge decision.
- Params:
  - `merge_request_id` (int).
  - `keep` (str): `'source'` (keep the current logged-in user) or `'target'` (keep the account that already owns the identity).
- Returns: the kept user instance (must log in again after merging).
- Raises: `AuthFlowError` on invalid `keep` or an already-resolved request.

#### `exchange_oauth_code(request, provider, code, state='', scope='', **profile) -> tuple[SnowlandUser, bool]`

- Purpose: unified OAuth callback entry (anonymous) — internally resolves `code` to an openid via `resolve_identity` then delegates to `bind_or_login_oauth`; `profile` carries `telephone`/`country_code`/`email`/`real_name` for auto-registration.
- Returns: `(user, created)`.

#### `bind_oauth_code_for_authenticated_user(request, user, provider, code, state='') -> dict`

- Purpose: unified OAuth callback entry (authenticated) — resolves `code` to an openid then delegates to `bind_oauth_for_authenticated_user`, returning a `{'status': ...}` dict.

---

## 4. DRF Views

### 4.1 `djangohelper.contrib.snowlandauth.views`

Thin adapters translating HTTP requests into `auth_flow` calls, returning `djangohelper.responses.APIResponse` uniformly.

| View | Method | Purpose | Notes |
| --- | --- | --- | --- |
| `RegisterView` | POST | register | body: `username`/`password`/`country_code`(default `+86`)/`telephone`/`email`/`real_name` |
| `PasswordLoginView` | POST | password login | body: `username`/`password` |
| `OAuthAuthorizeView` | GET | get authorize URL | query: `provider`/`state`/`scope`, returns `authorize_url` |
| `OAuthCallbackView` | POST | OAuth callback | body: `provider`/`code`/`state`; anonymous -> `exchange_oauth_code`, authenticated -> `bind_oauth_code_for_authenticated_user` |
| `OAuthBindView` | POST | authenticated bind | body: `provider`/`openid` (or `code` callback) |
| `AccountMergeView` | POST | merge decision | body: `merge_request_id`/`keep` |

---

## 5. Settings

Declare each platform's client credentials in Django `settings.py` (keyed by the upper-cased `OAUTH_TYPE`):

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

Dependency: `snowland-authsdk>=0.2` (added to `requirements.txt` and `pyproject.toml` `dependencies`).

---

## 6. Package Metadata

- Version: `0.3.2`
- New dependency: `snowland-authsdk>=0.2`
- Build: PEP 621 / PEP 517 (`pyproject.toml`)
