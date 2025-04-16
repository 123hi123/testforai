import os
import re
import json
import subprocess
from datetime import datetime

# 格式化文件大小的函數
def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024*1024):.1f} MB"

# 從Git獲取文件的最後修改時間
def get_git_modified_time(file_path):
    try:
        # 獲取文件最後一次修改的Git提交時間
        git_time = subprocess.check_output(
            ['git', 'log', '-1', '--format=%at', file_path], 
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()
        
        if git_time:
            return int(git_time)
    except:
        pass
    
    # 如果Git信息獲取失敗，則使用文件系統的修改時間
    return os.path.getmtime(file_path)

# 從Git獲取文件的創建時間（首次提交時間）
def get_git_creation_time(file_path):
    try:
        # 獲取文件首次提交的Git時間
        git_time = subprocess.check_output(
            ['git', 'log', '--follow', '--format=%at', '--reverse', file_path], 
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip().split('\n')[0]
        
        if git_time:
            return int(git_time)
    except:
        pass
    
    # 如果Git信息獲取失敗，則使用文件系統的創建時間（如果可用）或修改時間
    try:
        return os.path.getctime(file_path)  # Windows支持，但在某些Unix系統上可能是元數據更改時間
    except:
        return os.path.getmtime(file_path)

# 從HTML文件中提取預覽內容
def extract_preview(file_path, max_length=200):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 移除HTML標籤、腳本和樣式
            content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', content, flags=re.DOTALL)
            content = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', content, flags=re.DOTALL)
            content = re.sub(r'<[^>]*>', ' ', content)
            
            # 移除多餘空白
            content = re.sub(r'\s+', ' ', content).strip()
            
            # 截取預覽文本
            preview = content[:max_length]
            if len(content) > max_length:
                preview += "..."
                
            return preview
    except:
        return "無法生成預覽"

# 獲取所有 HTML 文件及其元數據
html_files = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.github' in root:
        continue
    for file in files:
        if file.endswith('.html') and file != 'index.html':
            path = os.path.join(root, file)
            # 轉換路徑格式為 URL 格式
            url_path = path.replace('\\', '/').lstrip('./')
            
            # 獲取文件大小
            size_bytes = os.path.getsize(path)
            
            # 獲取Git提交時間
            mod_time = get_git_modified_time(path)
            create_time = get_git_creation_time(path)
            
            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            create_time_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
            
            # 嘗試從文件中提取標題
            title = file
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1)
            except:
                pass  # 如果讀取失敗，使用文件名作為標題
            
            # 提取預覽內容
            preview = extract_preview(path)
            
            html_files.append({
                "name": file,
                "path": url_path,
                "title": title,
                "preview": preview,
                "size": size_bytes,
                "size_formatted": format_size(size_bytes),
                "modified": mod_time,
                "modified_formatted": mod_time_str,
                "created": create_time,
                "created_formatted": create_time_str
            })

# 生成 index.html
html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML 文件導航</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #6f8ab7;
            --text-color: #333;
            --bg-color: #f8f9fa;
            --card-bg: #fff;
            --border-color: #e1e4e8;
            --hover-color: #f1f8ff;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        header .container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        h1 {
            margin: 0;
            font-size: 2.2rem;
            font-weight: 300;
            text-align: center;
        }
        
        .subtitle {
            margin-top: 5px;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .search-container {
            width: 100%;
            max-width: 600px;
            margin: 20px 0;
            position: relative;
        }
        
        .search-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #aaa;
        }
        
        #search {
            width: 100%;
            padding: 12px 20px 12px 45px;
            border: 2px solid var(--border-color);
            border-radius: 30px;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        #search:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .sort-controls {
            display: flex;
            gap: 10px;
            margin: 10px 0;
            flex-wrap: wrap;
        }
        
        .sort-btn {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 8px 15px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }
        
        .sort-btn:hover {
            background-color: var(--hover-color);
        }
        
        .sort-btn.active {
            background-color: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        
        .file-count {
            font-size: 0.9rem;
            color: #666;
        }
        
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .file-card {
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-color);
            height: 100%;
        }
        
        .file-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .file-card-header {
            padding: 15px;
            background-color: var(--primary-color);
            color: white;
        }
        
        .file-title {
            margin: 0;
            font-size: 1.1rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .file-path {
            margin: 5px 0 0;
            font-size: 0.85rem;
            opacity: 0.9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .file-card-body {
            padding: 15px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        
        .file-preview {
            background-color: rgba(0,0,0,0.02);
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: #555;
            flex-grow: 1;
            position: relative;
            overflow: hidden;
            max-height: 100px;
            line-height: 1.5;
        }
        
        .file-preview::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(transparent, var(--card-bg));
        }
        
        .file-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            color: #666;
            font-size: 0.85rem;
            margin-top: auto;
        }
        
        .file-meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .file-card-footer {
            padding: 15px;
            text-align: center;
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 10px;
        }
        
        .btn {
            flex: 1;
            display: inline-block;
            background-color: var(--primary-color);
            color: white;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 4px;
            transition: background-color 0.2s;
            text-align: center;
        }
        
        .btn:hover {
            background-color: var(--secondary-color);
        }
        
        .btn-preview {
            background-color: #6c757d;
        }
        
        .btn-preview:hover {
            background-color: #5a6268;
        }
        
        .no-results {
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
            border-top: 1px solid var(--border-color);
        }
        
        /* 預覽模態框 */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
            overflow: auto;
        }
        
        .modal-content {
            position: relative;
            background-color: var(--bg-color);
            margin: 2% auto;
            padding: 0;
            width: 90%;
            max-width: 1200px;
            height: 90%;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .modal-header {
            padding: 15px;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-title {
            margin: 0;
            font-size: 1.2rem;
            font-weight: normal;
        }
        
        .modal-close {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0 10px;
        }
        
        .modal-body {
            height: calc(100% - 60px);
        }
        
        .preview-iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        
        @media (max-width: 768px) {
            .file-grid {
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            }
            
            .controls {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .sort-controls {
                margin-top: 10px;
            }
            
            .modal-content {
                width: 95%;
                height: 95%;
                margin: 2.5% auto;
            }
        }
        
        @media (max-width: 480px) {
            .file-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 1.8rem;
            }
            
            .file-card-footer {
                flex-direction: column;
            }
        }
        
        /* 暗黑模式支持 */
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #375a88;
                --secondary-color: #4a6fa5;
                --text-color: #e1e1e1;
                --bg-color: #1a1a1a;
                --card-bg: #2a2a2a;
                --border-color: #444;
                --hover-color: #333;
            }
            
            #search {
                background-color: #333;
                color: #e1e1e1;
            }
            
            .file-preview {
                background-color: rgba(255,255,255,0.05);
            }
            
            .file-preview::after {
                background: linear-gradient(transparent, var(--card-bg));
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>HTML 文件導航</h1>
            <p class="subtitle">瀏覽所有可用的 HTML 頁面</p>
            <div class="search-container">
                <i class="fas fa-search search-icon"></i>
                <input type="text" id="search" placeholder="搜尋文件...">
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="controls">
            <div class="file-count"><span id="visible-count">0</span> / <span id="total-count">0</span> 個文件</div>
            <div class="sort-controls">
                <button class="sort-btn active" data-sort="modified" data-order="desc">
                    <i class="fas fa-calendar-alt"></i> 最後修改
                </button>
                <button class="sort-btn" data-sort="created" data-order="desc">
                    <i class="fas fa-history"></i> 創建時間
                </button>
                <button class="sort-btn" data-sort="name" data-order="asc">
                    <i class="fas fa-font"></i> 文件名
                </button>
                <button class="sort-btn" data-sort="path" data-order="asc">
                    <i class="fas fa-folder"></i> 路徑
                </button>
                <button class="sort-btn" data-sort="size" data-order="desc">
                    <i class="fas fa-weight"></i> 文件大小
                </button>
            </div>
        </div>
        
        <div class="file-grid" id="file-grid">
            <!-- 文件卡片將由 JavaScript 動態生成 -->
        </div>
    </div>
    
    <!-- 預覽模態框 -->
    <div id="preview-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title" id="modal-title">文件預覽</h3>
                <button class="modal-close" id="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <iframe id="preview-iframe" class="preview-iframe" src=""></iframe>
            </div>
        </div>
    </div>
    
    <footer>
        <p>此頁面由 GitHub Actions 自動生成 | 最後更新: <span id="last-updated"></span></p>
    </footer>

    <script>
        // 文件數據
        const files = PLACEHOLDER_FOR_FILES_JSON;
        
        // 設置最後更新時間
        document.getElementById('last-updated').textContent = new Date().toLocaleString();
        document.getElementById('total-count').textContent = files.length;
        
        // 當前排序狀態
        let currentSort = {
            field: 'modified',
            order: 'desc'
        };
        
        // 初始化頁面
        function initPage() {
            sortAndRenderFiles();
            setupEventListeners();
        }
        
        // 設置事件監聽器
        function setupEventListeners() {
            // 搜索功能
            document.getElementById('search').addEventListener('input', function() {
                sortAndRenderFiles();
            });
            
            // 排序按鈕
            document.querySelectorAll('.sort-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const sortField = this.dataset.sort;
                    let sortOrder = this.dataset.order;
                    
                    // 如果點擊當前排序欄位，則切換排序順序
                    if (sortField === currentSort.field) {
                        sortOrder = currentSort.order === 'asc' ? 'desc' : 'asc';
                        this.dataset.order = sortOrder;
                    }
                    
                    // 更新排序狀態
                    currentSort.field = sortField;
                    currentSort.order = sortOrder;
                    
                    // 更新按鈕狀態
                    document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // 重新排序和渲染
                    sortAndRenderFiles();
                });
            });
            
            // 模態框關閉按鈕
            document.getElementById('modal-close').addEventListener('click', function() {
                document.getElementById('preview-modal').style.display = 'none';
            });
            
            // 點擊模態框外部關閉
            window.addEventListener('click', function(event) {
                const modal = document.getElementById('preview-modal');
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        // 打開預覽模態框
        function openPreview(filePath, title) {
            const modal = document.getElementById('preview-modal');
            const iframe = document.getElementById('preview-iframe');
            const modalTitle = document.getElementById('modal-title');
            
            iframe.src = filePath;
            modalTitle.textContent = title;
            modal.style.display = 'block';
        }
        
        // 排序並渲染文件
        function sortAndRenderFiles() {
            const searchTerm = document.getElementById('search').value.toLowerCase();
            
            // 過濾文件
            const filteredFiles = files.filter(file => {
                const searchString = `${file.title} ${file.name} ${file.path} ${file.preview}`.toLowerCase();
                return searchString.includes(searchTerm);
            });
            
            // 排序文件
            filteredFiles.sort((a, b) => {
                let valueA, valueB;
                
                // 根據排序欄位獲取值
                switch (currentSort.field) {
                    case 'name':
                        valueA = a.name.toLowerCase();
                        valueB = b.name.toLowerCase();
                        break;
                    case 'path':
                        valueA = a.path.toLowerCase();
                        valueB = b.path.toLowerCase();
                        break;
                    case 'size':
                        valueA = a.size;
                        valueB = b.size;
                        break;
                    case 'created':
                        valueA = a.created;
                        valueB = b.created;
                        break;
                    case 'modified':
                    default:
                        valueA = a.modified;
                        valueB = b.modified;
                        break;
                }
                
                // 比較
                if (valueA < valueB) return currentSort.order === 'asc' ? -1 : 1;
                if (valueA > valueB) return currentSort.order === 'asc' ? 1 : -1;
                return 0;
            });
            
            // 更新可見文件計數
            document.getElementById('visible-count').textContent = filteredFiles.length;
            
            // 渲染文件
            renderFiles(filteredFiles);
        }
        
        // 渲染文件列表
        function renderFiles(files) {
            const fileGrid = document.getElementById('file-grid');
            fileGrid.innerHTML = '';
            
            if (files.length === 0) {
                fileGrid.innerHTML = '<div class="no-results"><i class="fas fa-search" style="font-size: 2rem; margin-bottom: 10px;"></i><h3>沒有找到匹配的文件</h3><p>請嘗試不同的搜索詞</p></div>';
                return;
            }
            
            files.forEach(file => {
                const card = document.createElement('div');
                card.className = 'file-card';
                
                card.innerHTML = `
                    <div class="file-card-header">
                        <h3 class="file-title">${file.title}</h3>
                        <p class="file-path">${file.path}</p>
                    </div>
                    <div class="file-card-body">
                        <div class="file-preview">${file.preview}</div>
                        <div class="file-meta">
                            <div class="file-meta-item"><i class="far fa-calendar-plus"></i> 創建: ${file.created_formatted}</div>
                            <div class="file-meta-item"><i class="far fa-calendar-alt"></i> 修改: ${file.modified_formatted}</div>
                            <div class="file-meta-item"><i class="fas fa-file"></i> ${file.size_formatted}</div>
                        </div>
                    </div>
                    <div class="file-card-footer">
                        <a href="${file.path}" class="btn" target="_blank">
                            <i class="fas fa-external-link-alt"></i> 查看
                        </a>
                        <button class="btn btn-preview" onclick="openPreview('${file.path}', '${file.title.replace(/'/g, "\\'")}')">
                            <i class="fas fa-eye"></i> 預覽
                        </button>
                    </div>
                `;
                
                fileGrid.appendChild(card);
            });
        }
        
        // 初始化頁面
        document.addEventListener('DOMContentLoaded', initPage);
    </script>
</body>
</html>
"""

# 將文件數據轉換為 JSON 並插入到 HTML 中
files_json = json.dumps(html_files, ensure_ascii=False)
html_content = html_content.replace('PLACEHOLDER_FOR_FILES_JSON', files_json)

# 寫入 index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"成功生成 index.html，包含 {len(html_files)} 個 HTML 文件")
