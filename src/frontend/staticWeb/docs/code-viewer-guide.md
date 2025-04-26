# 代码查看功能使用指南

本文档介绍如何使用和自定义代码查看模块。

## 功能概述

代码查看模块提供了两个主要功能：

1. **代码上下文查看**：显示漏洞代码周围的上下文代码行，以便更好地理解漏洞上下文。
2. **完整源文件查看**：查看整个源文件内容，以便全面了解代码结构。

## 模块结构

代码查看模块使用模块化设计，便于自定义和维护：

- `js/code-viewer.js` - 主要JavaScript模块，包含所有功能实现
- `css/code-viewer.css` - 样式文件，定义代码查看相关的样式
- `api_example/source_api.py` - 后端API示例，用于获取源代码文件

## 使用方法

### 前端集成

1. 在HTML头部引入CSS文件：
   ```html
   <link rel="stylesheet" href="./css/code-viewer.css">
   ```

2. 在HTML底部引入JavaScript文件（在其他脚本之前）：
   ```html
   <script src="./js/code-viewer.js"></script>
   ```

3. 初始化代码查看模块：
   ```html
   <script>
     document.addEventListener('DOMContentLoaded', function() {
       if (window.CodeViewer) {
         window.CodeViewer.init();
       }
     });
   </script>
   ```

4. 在漏洞详情模板中添加按钮和容器：
   ```html
   <!-- 代码查看按钮 -->
   <div class="flex space-x-2 mt-2">
     <button class="btn btn-sm btn-outline show-context-btn">
       <svg class="h-4 w-4 mr-1">...</svg>
       <span class="btn-text">显示上下文</span>
     </button>
     <button class="btn btn-sm btn-outline show-file-btn">
       <svg class="h-4 w-4 mr-1">...</svg>
       查看完整文件
     </button>
   </div>
   
   <!-- 代码上下文容器 -->
   <div class="code-context hidden mt-4"></div>
   ```

### 后端API实现

目前代码查看模块使用模拟数据进行演示。在实际项目中，你需要实现API来获取源代码。

1. 修改 `js/code-viewer.js` 中的 `getSourceCode` 函数：
   ```javascript
   async function getSourceCode(filePath) {
     // 检查缓存
     if (sourceFileCache[filePath]) {
       return sourceFileCache[filePath];
     }
     
     try {
       // 替换为实际的API调用
       const response = await fetch(`/api/source?path=${encodeURIComponent(filePath)}`);
       if (!response.ok) throw new Error('无法获取源代码');
       const sourceCode = await response.text();
       
       // 缓存源代码
       sourceFileCache[filePath] = sourceCode;
       return sourceCode;
     } catch (error) {
       console.error('获取源代码失败:', error);
       return null;
     }
   }
   ```

2. 使用提供的API示例（可选）：
   - 安装Flask: `pip install flask`
   - 启动API服务器: `python api_example/source_api.py`
   - API端点: `http://localhost:5000/api/source?path=path/to/file.sol`

## 自定义和扩展

### 样式自定义

你可以通过修改 `css/code-viewer.css` 文件自定义代码查看的样式：

```css
/* 修改代码块背景颜色 */
.code-block {
  background: #1e293b; /* 改变为你喜欢的颜色 */
}

/* 修改高亮行的样式 */
.highlighted-line {
  background-color: rgba(234, 179, 8, 0.2); /* 改变高亮颜色 */
  border-left: 3px solid #eab308; /* 改变标记颜色 */
}
```

### 功能扩展

你可以通过修改 `js/code-viewer.js` 文件扩展代码查看功能：

1. 添加代码行号点击功能：
   ```javascript
   // 在 setupEventDelegation 函数中添加
   document.addEventListener('click', function(event) {
     // 检查是否点击了行号
     if (event.target.classList.contains('line-number')) {
       const lineNumber = parseInt(event.target.textContent);
       // 执行你想要的操作，例如高亮该行
       // ...
     }
   });
   ```

2. 添加代码搜索功能：
   ```javascript
   // 创建新函数
   function searchInCode(codeElement, searchText) {
     const codeLines = codeElement.querySelectorAll('.code-line');
     let matchCount = 0;
     
     codeLines.forEach(line => {
       const content = line.querySelector('.line-content');
       const text = content.textContent;
       
       if (text.includes(searchText)) {
         line.classList.add('search-match');
         matchCount++;
       } else {
         line.classList.remove('search-match');
       }
     });
     
     return matchCount;
   }
   
   // 在合适的地方添加搜索框和搜索逻辑
   // ...
   ```

## 故障排除

### 常见问题

1. **无法加载源代码**
   - 确保API服务器正在运行
   - 检查网络请求是否有错误
   - 验证文件路径是否正确

2. **代码高亮不起作用**
   - 确保已加载Prism.js
   - 检查控制台是否有错误

3. **按钮不响应**
   - 检查事件委托是否正确设置
   - 确保选择器匹配HTML结构

### 调试技巧

1. 启用更详细的日志：
   ```javascript
   // 在 code-viewer.js 顶部添加
   const DEBUG = true;
   
   // 添加日志函数
   function log(message, ...args) {
     if (DEBUG) {
       console.log(`[CodeViewer] ${message}`, ...args);
     }
   }
   
   // 在代码中使用
   log('初始化代码查看模块');
   ```

2. 检查DOM结构是否正确：
   ```javascript
   // 在适当的地方添加
   log('按钮元素:', document.querySelectorAll('.show-context-btn').length);
   log('代码上下文容器:', document.querySelectorAll('.code-context').length);
   ```

## 后续开发建议

1. **添加代码搜索**：实现在源文件中搜索特定文本的功能
2. **添加代码导航**：实现跳转到特定行、函数或类的功能
3. **增强高亮**：支持高亮多个代码区域和不同类型的高亮（如错误、警告等）
4. **集成语法分析**：添加代码语法检查和分析功能

---

如有任何问题或需要进一步的帮助，请随时提问。 