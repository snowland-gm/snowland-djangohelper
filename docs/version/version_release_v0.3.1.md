# snowland-djangohelper-0.3.1 发布说明

**Version: 0.3.1**

**Auth:    A.Star**

| 信息 | 值 |
| :--: | :--: |
| 版本 | 0.3.1 |
| 授权协议 | BSD License |
| 开发语言 | PYTHON |
| 操作系统 | 跨平台 |
| 分类 | web 开发、工具包 |
| 开源地址-gitee | [https://gitee.com/snowlandltd/snowland-djangohelper](https://gitee.com/snowlandltd/snowland-djangohelper) |
| 开源下载-pypi | [https://pypi.org/project/snowland-djangohelper/](https://pypi.org/project/snowland-djangohelper/) |

## 更新内容 / Changelog

### 新增 / Added

1. 新增数据库模型 mixin（`djangohelper.db.models.mixins`）：
   - `UUIDMixin`：注入 `uuid` 字段（`unique=True`，对外唯一标识，非主键）。
   - `TimestampMixin`：注入 `created_time` / `updated_time` 时间戳字段。
   - `SoftDeleteMixin`：注入 `is_deleted` 软删除标志（`db_index=True`），并提供 `active` / `deleted` 管理器、`delete(soft=True)` / `hard_delete()` 方法。
2. `SelfModelViewSet` 增强：
   - `get_queryset()` 自动过滤 `is_deleted=False`（对 `SoftDeleteMixin` 模型），`list` / `retrieve` / `update` 默认隐藏已删记录。
   - `retrieve` 命中已删或不存在对象时统一返回 `code=404` 的 `APIResponse`。
   - `destroy` 对 `SoftDeleteMixin` 模型执行软删除；返回 `HTTP 200` 并携带被删对象标识（`uuid` 或 `id`），替代原 `204` 空响应。
   - 未声明 `serializer_class` 时自动构建 `ModelSerializer`，并按 mixin 调整字段（`UUIDMixin` 排除 `id`、`SoftDeleteMixin` 排除 `is_deleted`）。
3. 从 `setup.py` 迁移到 `pyproject.toml`（PEP 621 / PEP 517）配置构建，CI 发布流水线改用 `python -m build`。
4. 提供中英双语最新 API 文档 `docs/v0_3_1/API_zh.md` / `docs/v0_3_1/API_en.md`（对应 0.3.1）。

### 重构 / Changed

1. 去除 `astartool` 依赖，改用标准库与 Django 自带实现：
   - `number_tool`：`random_string` / `random_hex_string` 改用 `secrets.SystemRandom`（新增 `upper` 参数）。
   - `common`：`list_allow_extension` / `list_ignore` 内联为常量。
   - `hasher`：`force_bytes` / `force_text` 直接取自 `django.utils.encoding`。
   - `setup.py` 的 `load_install_requires` 逻辑内联进 `pyproject.toml` 的静态依赖声明。
2. `requirements.txt` 移除 `astartool`；`README` / `README_EN` 及 API 文档同步更新。

### 测试 / Tests

- 新增 `tests/test_models_mixin.py` 与 `tests/testapp/models.py` 测试模型，覆盖 mixin 与 `SelfModelViewSet` 软删除 / 动态序列化器行为。
- 全部用例通过（52 passed）；`bcrypt` 可选依赖安装后 `BCryptSM3PasswordHasher` 相关用例亦通过。
