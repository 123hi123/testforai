import os
import re

# 獲取所有 HTML 文件
html_files = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.github' in root:
        continue
    for file in files:
        if file.endswith('.html') and file != 'index.html':
            path = os.path.join(root, file)
            # 轉換路徑格式為 URL 格式
            url_path = path.replace('\\', '/').lstrip('./')
            html_files.append((file, url_path))

# 生成 index.html
html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Pages 導覽</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin-bottom: 10px;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>HTML 文件導覽</h1>
    <p>以下是本倉庫中所有可用的 HTML 頁面：</p>
    <ul>
"""

for file_name, file_path in sorted(html_files, key=lambda x: x[1]):
    html_content += f'        <li><a href="{file_path}">{file_path}</a></li>\n'

html_content += """    </ul>
    <p><small>此頁面由 GitHub Actions 自動生成</small></p>
</body>
</html>
"""

# 寫入 index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"成功生成 index.html，包含 {len(html_files)} 個 HTML 文件")
