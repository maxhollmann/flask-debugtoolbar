import itertools
import os.path
import sys

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import SqlLexer
    from pygments.styles import get_style_by_name
    PYGMENT_STYLE = get_style_by_name('colorful')
    HAVE_PYGMENTS = True
except ImportError:
    HAVE_PYGMENTS = False


from flask import current_app, Markup


def format_fname(value):
    # If the value has a builtin prefix, return it unchanged
    if value.startswith(('{', '<')):
        return value

    value = os.path.normpath(value)

    # If the file is absolute, try normalizing it relative to the project root
    # to handle it as a project file
    if os.path.isabs(value):
        value = _shortest_relative_path(value, [current_app.root_path], os.path)

    # If the value is a relative path, it is a project file
    if not os.path.isabs(value):
        return os.path.join('.', value)

    # Otherwise, normalize other paths relative to sys.path
    return '<%s>' % _shortest_relative_path(value, sys.path, os.path)


def _shortest_relative_path(value, paths, path_module):
    relpaths = _relative_paths(value, paths, path_module)
    return min(itertools.chain(relpaths, [value]), key=len)


def _relative_paths(value, paths, path_module):
    for path in paths:
        try:
            relval = path_module.relpath(value, path)
        except ValueError:
            # on Windows, relpath throws a ValueError for
            # paths with different drives
            continue
        if not relval.startswith(path_module.pardir):
            yield relval


def format_sql(query, args):
    if not HAVE_PYGMENTS:
        return query

    return Markup(highlight(
        query,
        SqlLexer(encoding='utf-8'),
        HtmlFormatter(encoding='utf-8', noclasses=True, style=PYGMENT_STYLE)))
