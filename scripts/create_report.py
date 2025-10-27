
# -*- coding: utf-8 -*-


from astar_devopstool.version_announcement import version_release_announcement_template
from astar_devopstool.common import License, LICENSE_SHORT, Language, Plantform

import djangohelper

version_dict = {
    'project_name': 'snowland-djangohelper',
    'version': djangohelper.__version__,
    '版本': djangohelper.__version__,
    '日期': '2025-10-28',
    '授权协议': LICENSE_SHORT[License.BSD],
    '开发语言': Language.PYTHON.value,
    '操作系统': "跨平台",
    '分类': "web开发、工具包",
    '开源地址-gitee': '[https://gitee.com/snowlandltd/snowland-djangohelper](https://gitee.com/snowlandltd/snowland-djangohelper)',
    '开源下载-pypi': '[https://pypi.org/project/snowland-djangohelper/](https://pypi.org/project/snowland-djangohelper/)'
}

content = """
### 新增

1. pagination 增加分页基类（辅助SelfModelViewSet分页）

### 修复

1. number_tool 基于系统提供更安全的随机数

### 删除

1. 删除一些非必要的系统文件


"""

version_release_announcement_template(version_dict, content=content, file_name="../docs/version/version_release_v{}.md".format(djangohelper.__version__))
