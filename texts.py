from pathlib import Path

class Template(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
    
    def format(self, **kwargs):
        for key, value in kwargs.items():
            self = self.replace(f"%{key.upper()}%", str(value))
        return self


def get_template(name, html=True):
    with open(Path('templates', name + ('.html' if html else ''))) as f:
        return Template(f.read())
    

INDEX_HTML = get_template('index')
WEB_HTML = get_template('web_form')
UPLOAD_HUMAN_HTML = get_template('upload')
EDIT_FORM_HTML = get_template('edit_form')
ERROR_404_TEXT = get_template('404.txt', False)
