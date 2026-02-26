"""
Максимально навороченный рендерер Markdown.
Зависимости: pip install markdown pymdown-extensions pygments
"""

import os
import re
import markdown
import pymdownx.superfences
import pymdownx.slugs
import pymdownx.emoji
from pygments.formatters import HtmlFormatter
from texts import MARKDOWN_TEMPLATE

# ── Pygments CSS ────────────────────────────────────────────────────────────
# Pygments генерирует `.highlight { ... }` — это бьёт и по блокам (div.highlight)
# и по инлайн коду (code.highlight). Переписываем все `.highlight` → `div.highlight`
# чтобы инлайн code.highlight не получал блочные стили (background, pre { }, etc.)
_raw_pygments_css = HtmlFormatter(
    style="one-dark",
    cssclass="highlight",
).get_style_defs(".highlight")

def _scope_pygments_css(css: str) -> str:
    """
    Меняет все вхождения .highlight на div.highlight,
    и убирает глобальный `pre { ... }` который Pygments добавляет в начало.
    """
    import re
    # убираем голый `pre { ... }` — он ломает всё
    css = re.sub(r'\bpre\s*\{[^}]*\}', '', css)
    # .highlight → div.highlight (но не трогаем .highlight внутри уже специфичных селекторов)
    css = re.sub(r'(?<!\w)\.highlight\b', 'div.highlight', css)
    return css

PYGMENTS_CSS = _scope_pygments_css(_raw_pygments_css)


# ── Расширения ──────────────────────────────────────────────────────────────
EXTENSIONS = [
    # ── Код ─────────────────────────────────────────────────────────────────
    "pymdownx.superfences",       # Вложенные/именованные фенсы + Mermaid
    "pymdownx.highlight",         # Подсветка синтаксиса (pygments)
    "pymdownx.inlinehilite",      # Inline: `#!python code`

    # ── Текстовые украшения ──────────────────────────────────────────────────
    "pymdownx.betterem",          # Умный em/strong (избегает конфликтов)
    "pymdownx.tilde",             # ~~зачёрк~~ и H~2~O (sub)
    "pymdownx.caret",             # ^^надстрочный^^ и x^2^ (sup)
    "pymdownx.mark",              # ==выделение==
    "pymdownx.smartsymbols",      # (c) → ©, --> → →, etc.
    "pymdownx.critic",            # CriticMarkup: {++ добавлено ++} {-- удалено --}

    # ── Типографика ──────────────────────────────────────────────────────────
    "smarty",                     # «умные» кавычки и тире

    # ── Медиа и ссылки ───────────────────────────────────────────────────────
    "pymdownx.emoji",             # :tada: :rocket: (Twemoji SVG)
    "pymdownx.magiclink",         # Автолинки URL, @mentions, #issues
    "pymdownx.keys",              # ++ctrl+alt+del++

    # ── Прогресс-бар ────────────────────────────────────────────────────────
    "pymdownx.progressbar",       # [=50% "Половина"]

    # ── Блоки контента ───────────────────────────────────────────────────────
    "pymdownx.blocks.admonition", # /// note \n text \n ///
    "pymdownx.blocks.details",    # /// details | Заголовок \n text \n ///
    "pymdownx.blocks.tab",        # /// tab | Python \n code \n ///
    "pymdownx.blocks.html",       # /// html \n <div>...</div> \n ///
    "pymdownx.tabbed",            # === "Tab" === (alternate style)
    "admonition",                 # !!! note / !!! warning / etc.

    # ── Списки ───────────────────────────────────────────────────────────────
    "pymdownx.tasklist",          # - [x] / - [ ]
    "pymdownx.fancylists",        # a. b. c. / I. II. III. / A) B) C)
    "sane_lists",                 # Не смешивать ul/ol без пустой строки

    # ── Структура ────────────────────────────────────────────────────────────
    "toc",                        # [TOC] + якоря у заголовков
    "pymdownx.saneheaders",       # Заголовок только с пробелом после #

    # ── Таблицы и определения ────────────────────────────────────────────────
    "tables",                     # GFM-таблицы
    "def_list",                   # Списки определений
    "abbr",                       # Аббревиатуры *[HTML]: HyperText...
    "footnotes",                  # Сноски[^1]

    # ── Атрибуты и вставки ───────────────────────────────────────────────────
    "attr_list",                  # {.class #id attr=val} на элементах
    "md_in_html",                 # markdown="1" внутри HTML
    "pymdownx.snippets",          # --8<-- "file.md" (вставка файлов)
    "meta",                       # YAML-метаданные в начале файла

    # ── WikiLinks ─────────────────────────────────────────────────────────────
    "wikilinks",                  # [[ссылка]] / [[ссылка|Текст]]

    # ── Математика (KaTeX/MathJax) ───────────────────────────────────────────
    "pymdownx.arithmatex",        # $inline$ и $$block$$

    # ── Разное ───────────────────────────────────────────────────────────────
    "nl2br",                      # Перенос строки → <br>
]

EXTENSION_CONFIGS = {
    # ── Подсветка синтаксиса ────────────────────────────────────────────────
    "pymdownx.highlight": {
        "use_pygments":         True,
        "pygments_style":       "one-dark",
        "noclasses":            False,
        "linenums":             True,           # Номера строк
        "linenums_style":       "pymdownx-inline",
        "anchor_linenums":      True,           # Кликабельные номера
        "line_spans":           "__span",
        "pygments_lang_class":  True,
    },
    "pymdownx.superfences": {
        "preserve_tabs": True,
        "custom_fences": [
            # Mermaid-диаграммы
            {
                "name":   "mermaid",
                "class":  "mermaid",
                "format": pymdownx.superfences.fence_code_format,
            },
            # PlantUML (рендерится через публичный сервер)
            {
                "name":   "plantuml",
                "class":  "plantuml",
                "format": pymdownx.superfences.fence_code_format,
            },
            # Math-блоки
            {
                "name":   "math",
                "class":  "arithmatex",
                "format": pymdownx.superfences.fence_code_format,
            },
        ],
    },
    "pymdownx.inlinehilite": {
        "style_plain_text": True,
    },
    # ── Emoji ───────────────────────────────────────────────────────────────
    "pymdownx.emoji": {
        "emoji_index":     pymdownx.emoji.twemoji,
        "emoji_generator": pymdownx.emoji.to_svg,
        "alt":             "unicode",
        "options": {
            "attributes": {"loading": "lazy"},
        },
    },
    # ── Magiclinks ──────────────────────────────────────────────────────────
    "pymdownx.magiclink": {
        "hide_protocol":       True,
        "repo_url_shortener":  True,
        "repo_url_shorthand":  True,
        "social_url_shorthand": True,
        "user":                "myuser",       # дефолтный пользователь для @mentions
        "repo":                "myrepo",       # дефолтный репо для #issues
    },
    # ── Tasklist ────────────────────────────────────────────────────────────
    "pymdownx.tasklist": {
        "custom_checkbox":    True,
        "clickable_checkbox": True,
    },
    # ── Tabbed ──────────────────────────────────────────────────────────────
    "pymdownx.tabbed": {
        "alternate_style": True,
        "slugify": pymdownx.slugs.slugify(case="lower"),
    },
    # ── Arithmatex (KaTeX) ──────────────────────────────────────────────────
    "pymdownx.arithmatex": {
        "generic": True,   # Вывод для KaTeX/MathJax (не зашитый скрипт)
    },
    # ── TOC ─────────────────────────────────────────────────────────────────
    "toc": {
        "permalink":       True,
        "permalink_title": "Ссылка на раздел",
        "toc_depth":       "1-4",
        "slugify":         pymdownx.slugs.slugify(case="lower"),
        "separator":       "-",
    },
    # ── Critic ──────────────────────────────────────────────────────────────
    "pymdownx.critic": {
        "mode": "view",   # "view" | "accept" | "reject"
    },
    # ── Keys ────────────────────────────────────────────────────────────────
    "pymdownx.keys": {
        "separator":         "+",
        "strict":            False,
        "camel_case":        True,
    },
    # ── Quotes (smarty alternative) ─────────────────────────────────────────
    "pymdownx.quotes": {
        "primary":        "«»",
        "primary_spaces": True,
        "secondary":      "„",
    },
    # ── Snippets ────────────────────────────────────────────────────────────
    "pymdownx.snippets": {
        "base_path":        ["."],
        "check_paths":      False,
        "auto_append":      [],
    },
    # ── Progressbar ─────────────────────────────────────────────────────────
    "pymdownx.progressbar": {
        "level_class":    True,
        "add_classes":    "",
        "progress_increment": 20,
    },
    # ── Smarty ──────────────────────────────────────────────────────────────
    "smarty": {
        "smart_quotes":  True,
        "smart_dashes":  True,
        "smart_ellipses": True,
        "smart_angled_quotes": False,
    },
    # ── Meta ────────────────────────────────────────────────────────────────
    # (нет конфигов, но Meta-данные доступны через md.Meta после convert())
    # ── WikiLinks ────────────────────────────────────────────────────────────
    "wikilinks": {
        "base_url":    "/wiki/",
        "end_url":     "/",
        "html_class":  "wikilink",
    },
    # ── nl2br ───────────────────────────────────────────────────────────────
    # (нет конфигов)
}

def fix_mermaid(html_str: str) -> str:
    """
    pymdownx.superfences с fence_code_format генерирует:
        <pre class="mermaid"><code>flowchart LR\n    A --&gt; B</code></pre>
    Mermaid.js ожидает:
        <div class="mermaid">flowchart LR\n    A --> B</div>
    Конвертируем и разэскейпим HTML-entities.
    """
    def replacer(m):
        inner = (m.group(1)
                 .replace("&amp;",  "&")
                 .replace("&lt;",   "<")
                 .replace("&gt;",   ">")
                 .replace("&quot;", '"')
                 .replace("&#39;",  "'"))
        return f'<div class="mermaid">{inner}</div>'

    return re.sub(
        r'<pre class="mermaid"><code>(.*?)</code></pre>',
        replacer,
        html_str,
        flags=re.DOTALL,
    )

def render_markdown(content: str) -> str:
    md = markdown.Markdown(
        extensions=EXTENSIONS,
        extension_configs=EXTENSION_CONFIGS,
    )

    rendered_body = md.convert(content)
    
    rendered_body = fix_mermaid(rendered_body)

    # Метаданные из YAML-шапки (если есть)
    meta = getattr(md, "Meta", {})
    title    = " ".join(meta.get("title",       ["Документ"]))
    lang     = " ".join(meta.get("lang",        ["ru"]))
    toc_html = getattr(md, "toc", "")

    # Собираем итоговый HTML из шаблона
    template = MARKDOWN_TEMPLATE
    html = (
        template
        .replace("%TITLE%",       title)
        .replace("%LANG%",        lang)
        .replace("%BODY%",        rendered_body)
        .replace("%TOC%",         toc_html)
        .replace("%PYGMENTS_CSS%", PYGMENTS_CSS)
    )
    return html
