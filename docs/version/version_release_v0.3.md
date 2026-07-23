# snowland-djangohelper-0.3.0 发布说明

**Version: 0.3.0**

**Auth:    ASTARTOOL ROBOT**

| 信息 | 值 |
| :--: | :--: |
| 版本 | 0.3.0 |
| 授权协议 | BSD License |
| 开发语言 | PYTHON |
| 操作系统 | 跨平台 |
| 分类 | web 开发、工具包 |
| 开源地址-gitee | [https://gitee.com/snowlandltd/snowland-djangohelper](https://gitee.com/snowlandltd/snowland-djangohelper) |
| 开源下载-pypi | [https://pypi.org/project/snowland-djangohelper/](https://pypi.org/project/snowland-djangohelper/) |

## 更新内容 / Changelog

### 修复 / Fixes

1. `PBKDF2_SM3PasswordHasher.encode` 原将 `pysmx.SM3` 模块（不可调用）作为 `digest` 传给 `pbkdf2`，运行时抛 `TypeError`；现改为 hashlib 兼容的 `pysmx.SM3.SM3Type`。
2. `SM3KDFPasswordHasher.encode` 原使用 `isinstance(password, 'str')`（字符串而非类型），运行时抛 `TypeError`；并修正 `SM3.KDF` 调用：密码转为十六进制串作为 `Z`、固定 32 字节密钥长度（原误将 password 直接传入且以 `iterations` 作为长度）。
3. `SM3KDFPasswordHasher.safe_summary` 原调用 `encoded.splite('$')`（拼写错误，运行时 `AttributeError`），修正为 `encoded.split('$')`。
4. `djangohelper.auth` 包 `__init__.py` 原从不存在的 `djangohelper.contrib.hasher` 重定向导入，修正为 `djangohelper.contrib.auth.hasher`。

### 新增 / Added

1. `setup.py` 增加 `extras_require={'bcrypt': ['bcrypt']}`，使用者可通过 `pip install snowland-djangohelper[bcrypt]` 安装 `BCryptSM3PasswordHasher` 所需依赖。
2. 提供中英双语 `README.md` / `README_EN.md`。
3. 提供中英双语详细 API 文档 `docs/v0_3/API_zh.md` / `docs/v0_3/API_en.md`（对应 0.3.0），并保留 `docs/v0_2/` 历史文档（0.2.0）。
4. 新增 CI 流水线：`.github/workflows/publish.yml`（Release 时打包上传 PyPI）、`.github/workflows/docs.yml`（合并到主分支且 `docs/**` 变动时部署 GitHub Pages）。

### 测试 / Tests

- 新增 `tests/` 单元测试用例（基于 `unittest` + `pytest-django`），覆盖 `common` / `number_tool` / `project2lines` / `crypto` / `auth.hasher` / `responses` / `permissions` / `pagination` / `db.models` / `viewsets` 等模块。
- 全部用例通过（36 passed）；`bcrypt` 可选依赖安装后 `BCryptSM3PasswordHasher` 相关用例亦通过。
