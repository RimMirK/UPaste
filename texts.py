INDEX_HTML = """
<style>
    body { font-family: monospace; padding: 20px; max-width: 900px; margin: 0 auto; }
    h1 { color: #333; }
    h3 { color: #555; margin-top: 25px; }
    .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-left: 3px solid #007bff; }
    .code { background: #f9f9f9; padding: 8px; border-radius: 4px; font-size: 12px; }
    .example { background: #f0f0f0; padding: 12px; margin: 10px 0; border-left: 3px solid #28a745; }
    ul { line-height: 1.8; }
    a { color: #007bff; text-decoration: none; }
    a:hover { text-decoration: underline; }
</style>

<h1>📋 Paste — Simple Text Hosting</h1>

<p>No registration required. Share code, text, and markdown with easy-to-share links.</p>

<h3>🚀 Quick Start</h3>
<div class="endpoint">
    <b>Web Upload:</b> <a href="/web">Go to upload form</a>
</div>

<h3>📤 Upload Endpoints</h3>
<div class="endpoint">
    <b>POST /upload</b> — API upload (JSON or multipart)<br>
    <div class="example">
        <code>curl -X POST %BASE_URL%upload \</code><br>
        <code>&nbsp;&nbsp;-F "content=hello world" \</code><br>
        <code>&nbsp;&nbsp;-F "ext=txt"</code>
    </div>
</div>

<div class="endpoint">
    <b>GET /web</b> — Web form for uploading<br>
    <a href="/web">Click here to upload</a>
</div>

<h3>📖 View & Access</h3>
<div class="endpoint">
    <b>GET /{paste_id}</b> — View formatted paste<br>
    Supports syntax highlighting for: html, md, markdown, js, py, cpp, java, etc.
</div>

<div class="endpoint">
    <b>GET /raw/{paste_id}</b> — Get raw content<br>
    Perfect for downloading or piping to other tools
</div>

<h3>✏️ Edit & Manage</h3>
<div class="endpoint">
    <b>GET /edit/{paste_id}?token={token}</b> — Edit form<br>
    Use the token provided after upload
</div>

<div class="endpoint">
    <b>POST /edit/human/{paste_id}</b> — Save edits via web form<br>
    Requires valid token
</div>

<div class="endpoint">
    <b>GET /delete/{paste_id}?token={token}</b> — Delete paste<br>
    Requires the delete token
</div>

<h3>💡 Usage Examples</h3>
<div class="example">
    <b>Share code (Python):</b><br>
    <code>curl -F "content=@script.py" -F "ext=py" %BASE_URL%upload</code>
</div>

<div class="example">
    <b>Share JSON:</b><br>
    <code>curl -X POST %BASE_URL%upload \</code><br>
    <code>&nbsp;&nbsp;-H "Content-Type: application/json" \</code><br>
    <code>&nbsp;&nbsp;-d '{"content":"hello","ext":"json"}'</code>
</div>

<div class="example">
    <b>Download raw content:</b><br>
    <code>curl %BASE_URL%raw/{paste_id} -o file.txt</code>
</div>

<h3>📝 Supported Formats</h3>
<ul>
    <li><code>html</code> — Rendered as HTML</li>
    <li><code>md, markdown, mdown</code> — Rendered as Markdown</li>
    <li><code>js, py, cpp, java, etc.</code> — Syntax highlighted code</li>
    <li>Plain text files (auto-detected)</li>
</ul>

<hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
<p style="font-size: 12px; color: #666;">Free and open source • No account needed</p>
"""


with open('templates/web_form.html') as f:
    WEB_HTML = f.read()


ERROR_404_TEXT = """
           a8      ,a888a,            a8   
         ,d88    ,8P"' `"Y8,        ,d88   
        a8P88   ,8P       Y8,      a8P88   
      ,d8" 88   88         88    ,d8" 88   
     a8P'  88   88         88   a8P'  88   
   ,d8"    88   88         88 ,d8"    88   
   888888888888 88         88 888888888888 
           88   `8b       d8'         88   
           88    `8ba, ,ad8'          88   
           88      "Y888P"            88   

         The paste not found, sorry
"""

UPLOAD_HUMAN_HTML = """
<style>
    body {{ font-family: monospace; }}
    .box {{ margin-top:20px; padding:15px; border:1px solid #ccc; }}
</style>

<h2>Paste {status} successfully</h2>

<div class="box">
    <b>View:</b><br>
    <a href="{base_url}/{paste_id}">{base_url}/{paste_id}</a>
</div>

<div class="box">
    <b>Raw:</b><br>
    <a href="{base_url}/raw/{paste_id}">{base_url}/raw/{paste_id}</a>
</div>

<div class="box">
    <b>Delete URL:</b><br>
    <a href="{base_url}/delete/{paste_id}?token={token}">
    {base_url}/delete/{paste_id}?token={token}
    </a>
</div>

<div class="box">
    <b>Edit URL:</b><br>
    <a href="{base_url}/edit/{paste_id}?token={token}">
    {base_url}/edit/{paste_id}?token={token}
    </a>
</div>

<div class="box">
    <b>Token:</b><br>
    {token}
</div>

<div class="box">
    <a href="/web">Upload another paste</a>
</div>
"""


EDIT_FORM_HTML = """
<style>
    body {{ font-family: monospace; }}
    textarea {{ width:100%; height:400px; }}
</style>

<h2>Edit paste</h2>

<form method="post" action="/edit/human/{paste_id}">
    <textarea name="content">{content}</textarea><br><br>
    <input type="text" name="ext" value="{ext}" placeholder="ext: html, md, js, py, cpp, etc.">
    <input type"text" name="token" value="{token}" placeholder="Token" size="24">
    <input type="submit" value="Save">
</form>
"""