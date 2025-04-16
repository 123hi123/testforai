import os
import re
import time
import json
from datetime import datetime

# 格式化文件大小的函數
def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024*1024):.1f} MB"

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
            
            # 獲取最後修改時間
            mod_time = os.path.getmtime(path)
            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            
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
            
            html_files.append({
                "name": file,
                "path": url_path,
                "title": title,
                "size": size_bytes,
                "size_formatted": format_size(size_bytes),
                "modified": mod_time,
                "modified_formatted": mod_time_str
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
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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
        }
        
        .file-meta {
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 0.85rem;
            margin-bottom: 15px;
        }
        
        .file-card-footer {
            padding: 15px;
            text-align: center;
            border-top: 1px solid var(--border-color);
        }
        
        .view-btn {
            display: inline-block;
            background-color: var(--primary-color);
            color: white;
            text-decoration: none;
            padding: 8px 20px;
            border-radius: 4px;
            transition: background-color 0.2s;
            width: 100%;
            box-sizing: border-box;
        }
        
        .view-btn:hover {
            background-color: var(--secondary-color);
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
        
        @media (max-width: 768px) {
            .file-grid {
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            }
            
            .controls {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .sort-controls {
                margin-top: 10px;
                flex-wrap: wrap;
            }
        }
        
        @media (max-width: 480px) {
            .file-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 1.8rem;
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
        }
        
        // 排序並渲染文件
        function sortAndRenderFiles() {
            const searchTerm = document.getElementById('search').value.toLowerCase();
            
            // 過濾文件
            const filteredFiles = files.filter(file => {
                const searchString = `${file.title} ${file.name} ${file.path}`.toLowerCase();
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
                        <div class="file-meta">
                            <span><i class="far fa-calendar-alt"></i> ${file.modified_formatted}</span>
                            <span><i class="fas fa-file"></i> ${file.size_formatted}</span>
                        </div>
                    </div>
                    <div class="file-card-footer">
                        <a href="${file.path}" class="view-btn" target="_blank">查看文件</a>
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
