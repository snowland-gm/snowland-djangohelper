# import HTMLParser
import html.parser as HTMLParser

from bs4 import BeautifulSoup
import os
import re

trans_list = ['.html', '.htm']


def trans_file(file, encoding='utf-8'):
    splitext = os.path.splitext(file)
    with open(file, "r", encoding=encoding) as f1, open("{}.bak".format(splitext[0]), "w", encoding=encoding) as f2:
        for line in f1:
            if "<title>" in line:
                f2.write("{% load staticfiles %}\n")
            n_line = trans_href(line)
            n_line = trans_src(n_line)
            f2.write(n_line)

    os.remove(file)
    os.rename("{}.bak".format(splitext[0]), file)


def trans_href(s):
    pattern_href = re.compile('href=[\"|\'].*?\.css[\"|\']')
    str_href = re.findall(pattern_href, s)
    if str_href:
        str_href = str_href[0][6:-1]
        s = s.replace(str_href, "{%static '" + str_href + "'%}")
    return s


def trans_src(s):
    pattern_src = re.compile('src=".*?[\.js|\.css|\.png\.jpg|\.bmp|\.gif]"')
    str_src = re.findall(pattern_src, s)
    if str_src:
        str_src = str_src[0][5:-1]
        if str(str_src).startswith("http"):
            return s
        s = s.replace(str_src, "{%static '" + str_src + "'%}")
    return s


def trans(root):
    files = [root + '/' + i for i in os.listdir(root) if
             os.path.isfile(root + '/' + i) and os.path.splitext(i)[1] in trans_list]
    [trans_file(file) for file in files]


if __name__ == '__main__':
    trans('html_test/static/resources')
