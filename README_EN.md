# snowland-djangohelper

[![version](https://img.shields.io/pypi/v/snowland-djangohelper.svg)](https://pypi.python.org/pypi/snowland-djangohelper)
[![gitee](https://gitee.com/snowlandltd/snowland-djangohelper/badge/star.svg)](https://gitee.com/snowlandltd/snowland-djangohelper/stargazers)
[![download](https://img.shields.io/pypi/dm/snowland-djangohelper.svg?cacheSeconds=86400)](https://pypi.org/project/snowland-djangohelper)
[![wheel](https://img.shields.io/pypi/wheel/snowland-djangohelper.svg)](https://pypi.python.org/pypi/snowland-djangohelper)
![status](https://img.shields.io/pypi/status/snowland-djangohelper.svg)

- [中文版 / Chinese version](README.md)

> A practical toolkit / extension library for Django and Django REST Framework (DRF).

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Modules](#modules)
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [References](#references)
- [License](#license)

---

## Introduction

`snowland-djangohelper` is a collection of helper utilities for Django and Django REST Framework. It packages common features such as authentication, cryptography, pagination, unified responses, permissions, and base models, helping developers build consistent and well-structured Django backends quickly.

---

## Features

- Password hashers based on the Chinese national cryptography standard **SM3** (compatible with Django's password framework)
- Unified API response wrapper `APIResponse`
- Extended DRF pagination and `ModelViewSet`
- Role-based permission control (admin / auditor / operator / superuser)
- Generic `BaseModel` (automatic timestamps, convenience methods `new` / `update` / `one` / `all` / `filter`)
- Random string / hex string generation utilities
- Project source dumper (useful for software copyright filing)

---

## Installation

### Install from PyPI

```bash
pip install snowland-djangohelper
```

To use the `BCrypt-SM3` password hasher, install the optional `bcrypt` dependency:

```bash
pip install snowland-djangohelper[bcrypt]
```

### Install from source

```bash
# Download the code from https://gitee.com/snowlandltd/snowland-djangohelper (choose a release version)
pip install .
```

> Note: This project requires Python 3.6+ and Django 2.0+ (compatible up to Django 5.1).

---

## Modules

| Module | Description |
| --- | --- |
| `djangohelper.auth` | Password hashers based on SM3 (SM3 / PBKDF2-SM3 / BCrypt-SM3, etc.). |
| `djangohelper.contrib` | General business apps such as `developer`, `friendlink`, `snowlandauth`. |
| `djangohelper.db` | Extended Django database capabilities (connection handling, `BaseModel`, etc.). |
| `djangohelper.pagination` | Extended DRF pagination (`BasePageNumberPagination`). |
| `djangohelper.permissions` | Role-based permission classes (`AdminPermission` / `AuditPermission` / `OperatorPermission` / `SuperuserPermission` / `AllPermission`). |
| `djangohelper.requests` | HTTP request helpers (e.g. SMS gateway). |
| `djangohelper.responses` | Unified `APIResponse` wrapper. |
| `djangohelper.viewhelper` | Paginator result helper `generate_paginator_result`. |
| `djangohelper.viewsets` | Extended DRF `SelfModelViewSet`. |
| `djangohelper.views` | Common view templates. |
| `djangohelper.utils` | Utilities: SM3 `crypto`, `regex_helper`, etc. |
| `djangohelper.common` | Global definitions (error codes, allowed extensions, JWT payload demo). |
| `djangohelper.number_tool` | Random / hex string generation. |
| `djangohelper.project2lines` | Dump project source into a single file (for software copyright filing). |

---

## Quick Start

### Unified Response

```python
from djangohelper.responses import APIResponse

def my_view(request):
    data = {"hello": "world"}
    return APIResponse(data=data, message="success")
```

Response structure:

```json
{
  "successful": true,
  "code": 1,
  "message": "success",
  "data": {"hello": "world"}
}
```

### SM3 Password Hasher

```python
# settings.py
PASSWORD_HASHERS = [
    'djangohelper.auth.hasher.SM3PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

### Extended ViewSet

```python
from djangohelper.viewsets import SelfModelViewSet

class MyViewSet(SelfModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

### Base Model

```python
from djangohelper.db.models import BaseModel

class Article(BaseModel):
    title = models.CharField(max_length=200)

# Convenience methods
Article.new({"title": "Hello"})
Article.one(title="Hello")
Article.filter(title__contains="He")
```

---

## Dependencies

Runtime dependencies:

- `django>=2.0.5`
- `djangorestframework>=3.11.1`
- `snowland-smx>=0.3.1` (SM crypto support)
- `requests`

Optional dependencies:

- `bcrypt` (required by the `BCrypt-SM3` password hasher; corresponds to `project.optional-dependencies.bcrypt` in `pyproject.toml`; install via `pip install snowland-djangohelper[bcrypt]`)

Upload & docs dependencies:

- `requirements-upload.txt`: `twine`
- `requirements-doc.txt`: `astar-devopstool`

---

## References

[1] https://github.com/astar-club/astar-devopstool-python

---

## License

This project is released under the [**BSD License**](LICENSE).
