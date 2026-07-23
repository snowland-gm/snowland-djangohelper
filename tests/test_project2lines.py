"""Tests for djangohelper.project2lines (source dumper)."""
import os
import tempfile

from djangohelper.project2lines import file_to_lines, project_to_lines, walk


def test_file_to_lines():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'a.py')
        with open(src, 'w', encoding='utf-8') as f:
            f.write('print(1)\n')
        out = os.path.join(d, 'out.txt')
        file_to_lines(src, to_file=out)
        with open(out, encoding='utf-8') as f:
            content = f.read()
        assert 'a.py' in content
        assert 'print(1)' in content


def test_walk(tmp_path):
    src = tmp_path / 'b.txt'
    src.write_text('hello\n', encoding='utf-8')
    out = tmp_path / 'out.txt'
    walk(str(tmp_path), to_file=str(out), allow_extension=['.txt'], ignore=[])
    assert 'hello' in out.read_text(encoding='utf-8')


def test_project_to_lines():
    with tempfile.TemporaryDirectory() as d:
        proj = os.path.join(d, 'proj')
        os.makedirs(proj)
        with open(os.path.join(proj, 'c.py'), 'w', encoding='utf-8') as f:
            f.write('x = 1\n')
        out = os.path.join(d, 'result.txt')
        project_to_lines(
            src_project=proj, to_file=out, allow_extension=['.py'], ignore=[]
        )
        assert os.path.exists(out)
        assert 'x = 1' in open(out, encoding='utf-8').read()
