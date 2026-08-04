# snowland-djangohelper

[![version](https://img.shields.io/pypi/v/snowland-djangohelper.svg)](https://pypi.python.org/pypi/snowland-djangohelper)
[![gitee](https://gitee.com/snowlandltd/snowland-djangohelper/badge/star.svg)](https://gitee.com/snowlandltd/snowland-djangohelper/stargazers)
[![download](https://img.shields.io/pypi/dm/snowland-djangohelper.svg?cacheSeconds=86400)](https://pypi.org/project/snowland-djangohelper)
[![wheel](https://img.shields.io/pypi/wheel/snowland-djangohelper.svg)](https://pypi.python.org/pypi/snowland-djangohelper)
![status](https://img.shields.io/pypi/status/snowland-djangohelper.svg)

- [English version / 英文版](README_EN.md)

> Django 与 Django REST Framework（DRF）实用工具 / 扩展库。

---

## 目录

- [简介](#简介)
- [特性](#特性)
- [安装](#安装)
- [模块说明](#模块说明)
- [快速上手](#快速上手)
- [依赖](#依赖)
- [参考资料](#参考资料)
- [许可证](#许可证)

---

## 简介

`snowland-djangohelper` 是一套面向 Django / Django REST Framework 的辅助工具集，封装了常用的认证、加密、分页、统一响应、权限以及通用 Model 等功能，帮助开发者快速搭建规范、一致的 Django 后端服务。

---

## 特性

- 支持 **国密 SM3** 系列密码哈希器（兼容 Django 密码框架）
- 统一的 API 响应封装 `APIResponse`
- 扩展的 DRF 分页与 `ModelViewSet`
- 角色化权限控制（管理员 / 审核员 / 操作员 / 超级用户）
- 通用 `BaseModel`（自动时间戳，`new` / `update` / `one` / `all` / `filter` 便捷方法）
- 随机字符串 / 十六进制字符串生成工具
- 项目源码打包工具（用于软著申请等场景）

---

## 安装

### 从 PyPI 安装

```bash
pip install snowland-djangohelper
```

如需使用 `BCrypt-SM3` 密码哈希器，可安装 `bcrypt` 可选依赖：

```bash
pip install snowland-djangohelper[bcrypt]
```

### 从源码安装

```bash
# 从 https://gitee.com/snowlandltd/snowland-djangohelper 下载代码（可选择 release 版本）
pip install .
```

> 注意：本项目需要 Python 3.6+ 与 Django 2.0+（兼容至 Django 5.1）。

---

## 模块说明

| 模块 | 说明 |
| --- | --- |
| `djangohelper.auth` | 基于国密 SM3 的密码哈希器（SM3 / PBKDF2-SM3 / BCrypt-SM3 等）。 |
| `djangohelper.contrib` | 通用业务应用，如 `developer`、`friendlink`、`snowlandauth` 等。 |
| `djangohelper.db` | 对 Django 数据库能力的扩展（连接管理、`BaseModel` 基础模型等）。 |
| `djangohelper.pagination` | 扩展的 DRF 分页（`BasePageNumberPagination`）。 |
| `djangohelper.permissions` | 角色化权限类（`AdminPermission` / `AuditPermission` / `OperatorPermission` / `SuperuserPermission` / `AllPermission`）。 |
| `djangohelper.requests` | HTTP 请求辅助（短信接口等）。 |
| `djangohelper.responses` | 统一的 API 响应封装 `APIResponse`。 |
| `djangohelper.viewhelper` | 分页结果生成工具 `generate_paginator_result`。 |
| `djangohelper.viewsets` | 扩展的 DRF `ModelViewSet`（`SelfModelViewSet`）。 |
| `djangohelper.views` | 通用视图模板。 |
| `djangohelper.utils` | 工具函数：国密 `crypto`、正则辅助 `regex_helper` 等。 |
| `djangohelper.common` | 全局定义（错误码、允许的文件扩展名、JWT payload 示例等）。 |
| `djangohelper.number_tool` | 随机字符串 / 十六进制字符串生成。 |
| `djangohelper.project2lines` | 将项目源码打印为单文件（用于软著申请）。 |

---

## 快速上手

### 统一响应

```python
from djangohelper.responses import APIResponse

def my_view(request):
    data = {"hello": "world"}
    return APIResponse(data=data, message="success")
```

响应结构：

```json
{
  "successful": true,
  "code": 1,
  "message": "success",
  "data": {"hello": "world"}
}
```

### 国密密码哈希

```python
# settings.py
PASSWORD_HASHERS = [
    'djangohelper.auth.hasher.SM3PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

### 扩展视图集

```python
from djangohelper.viewsets import SelfModelViewSet

class MyViewSet(SelfModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

### 通用模型

```python
from djangohelper.db.models import BaseModel

class Article(BaseModel):
    title = models.CharField(max_length=200)

# 便捷方法
Article.new({"title": "Hello"})
Article.one(title="Hello")
Article.filter(title__contains="He")
```

---

## 依赖

运行时依赖：

- `django>=2.0.5`
- `djangorestframework>=3.11.1`
- `snowland-smx>=0.3.1`（国密算法支持）
- `requests`

可选依赖：

- `bcrypt`（`BCrypt-SM3` 密码哈希器所需，对应 `pyproject.toml` 的 `project.optional-dependencies.bcrypt`，通过 `pip install snowland-djangohelper[bcrypt]` 安装）

发布与文档依赖：

- `requirements-upload.txt`: `twine`
- `requirements-doc.txt`: `astar-devopstool`

---

## 参考资料

[1] https://github.com/astar-club/astar-devopstool-python

---

## 许可证

本项目基于 [**BSD License**](LICENSE) 发布。
