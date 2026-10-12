# snowland-djangohelper-0.3.2.post1 发布说明

**Version: 0.3.2.post1**

**Auth:    A.Star**

| 信息 | 值 |
| :--: | :--: |
| 版本 | 0.3.2.post1 |
| 授权协议 | BSD License |
| 开发语言 | PYTHON |
| 操作系统 | 跨平台 |
| 分类 | web 开发、工具包 |
| 开源地址-gitee | [https://gitee.com/snowlandltd/snowland-djangohelper](https://gitee.com/snowlandltd/snowland-djangohelper) |
| 开源下载-pypi | [https://pypi.org/project/snowland-djangohelper/](https://pypi.org/project/snowland-djangohelper/) |

## 更新内容 / Changelog

### 新增 / Added

1. 新增 `djangohelper.contrib.snowlandauth` 子模块，提供第三方账号绑定与授权登录能力：
   - 用户模型扩展 Mixin：`PhoneMixin`（手机号 + 国家码，**默认 `+86`**，`unique_together=(('country_code','telephone'),)`）、`GenderMixin`，由 `SnowlandUser` 组合（`AUTH_USER_MODEL = 'snowlandauth.SnowlandUser'`）。
   - OAuth 平台 Mixin：`OAuthMixin` 抽象基类 + `QQ` / `WeChat` / `CSDN` / `GitHub` / `Aliyun` / `Alipay` / `Taobao` 子类，回调统一委托 `snowland_authsdk` 的 `BaseOAuthClient`。其中 `QQOAuthClient` / `TaobaoOAuthClient` 在包内基于 SDK 的 `BaseOAuthClient` 继承实现（QQ token 为 query-string、openid 经 JSONP `me` 接口解析；Taobao 无独立 userinfo，openid 取自 token 的 `taobao_user_id`）。
   - 授权回调流程：`OAuthMixin.get_authorize_url` / `resolve_identity`，以及业务服务层 `auth_flow.exchange_oauth_code` / `bind_oauth_code_for_authenticated_user` / `bind_or_login_oauth` / `bind_oauth_for_authenticated_user` / `resolve_merge_request` / `register_user` / `login_by_password`，覆盖匿名自动注册登录、已登录绑定、账号冲突合并等场景。
   - DRF 视图适配器：`RegisterView` / `PasswordLoginView` / `OAuthAuthorizeView` / `OAuthCallbackView` / `OAuthBindView` / `AccountMergeView`，统一返回 `APIResponse`。
   - 数据模型：`OAuthAccount`（第三方绑定，`provider` + `openid`）、`AccountMergeRequest`（账号合并请求）。
   - 迁移文件：`0001_initial` / `0002_remove_oauthaccount_telephone` / `0003_accountmergerequest_country_code_and_more`。
2. 提供中英双语 API 文档 `docs/v0_3_2/API_zh.md` / `docs/v0_3_2/API_en.md`（对应 0.3.2）。

### 依赖 / Dependencies

1. `requirements.txt` 与 `pyproject.toml` 的 `dependencies` 新增 `snowland-authsdk>=0.2`。
2. 版本号统一提升至 `0.3.2.post1`：`pyproject.toml` 的 `version`（`0.3.2.post1`）与 `djangohelper/__init__.py` 的 `VERSION`（`(0, 3, 2, 'post', 1)`，即 `0.3.2.post1`）同步，修正代码内版本号仍停留在 `0.3.1` 的不一致问题。

### 测试 / Tests

- 新增 `tests/test_auth_flow.py`，覆盖注册 / 密码登录 / 国家码 / OAuth 匿名回调自动注册 / 已登录绑定 / 冲突合并 / QQ 与微信回调流程，全部用例通过（19 passed）。
