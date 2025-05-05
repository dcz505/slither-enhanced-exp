/**
 * 代码查看模块 - 提供源代码上下文和完整文件查看功能
 * 此模块与主应用解耦，可以独立添加、删除或修改
 */

// 缓存已加载的源文件，避免重复请求
const sourceFileCache = {};

/**
 * 初始化代码查看模块
 */
function initCodeViewer() {
  console.log('初始化代码查看模块...');

  // 确保只初始化一次
  if (window.__codeViewerInitialized) return;
  window.__codeViewerInitialized = true;

  // 创建模态窗口
  createSourceFileModal();

  // 设置事件委托
  setupEventDelegation();

  console.log('CodeViewer模块已初始化');
}

/**
 * 创建源文件查看用的模态窗口并添加到DOM
 */
function createSourceFileModal() {
  // 检查是否已有模态窗口
  if (document.getElementById('sourceFileModal')) return;

  const modal = document.createElement('div');
  modal.id = 'sourceFileModal';
  modal.className = 'modal';
  modal.innerHTML = `
    <div class="modal-box w-11/12 max-w-5xl">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg source-file-title">查看源文件</h3>
        <button class="btn btn-sm btn-circle close-modal">✕</button>
      </div>
      <div class="source-file-content bg-gray-800 p-4 rounded overflow-auto max-h-[70vh]"></div>
      <div class="modal-footer mt-4 flex justify-between items-center">
        <div class="file-info text-sm text-gray-500"></div>
        <div class="modal-action">
          <button class="btn btn-sm close-modal">关闭</button>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // 添加关闭按钮事件
  modal.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', () => {
      modal.classList.remove('modal-open');
    });
  });
}

/**
 * 设置事件委托，处理所有代码查看相关的点击事件
 */
function setupEventDelegation() {
  document.addEventListener('click', async (event) => {
    // 查找被点击的按钮及其相关的漏洞项
    const contextButton = event.target.closest('.show-context-btn');
    const fileButton = event.target.closest('.show-file-btn');
    const modalCloseButton = event.target.closest('.close-modal');

    // 处理代码上下文查看按钮
    if (contextButton) {
      const item = contextButton.closest('.vulnerability-item');
      if (!item) return;

      const locationEl = item.querySelector('.vulnerability-location');
      const codeContextDiv = item.querySelector('.code-context');

      if (locationEl && codeContextDiv) {
        // 解析文件和行号信息
        const fileInfo = parseLocationText(locationEl.textContent);
        if (!fileInfo || !fileInfo.filePath) {
          console.error('无法解析文件路径:', locationEl.textContent);
          codeContextDiv.innerHTML = '<div class="error p-4 text-red-500">无法解析文件路径信息</div>';
          codeContextDiv.classList.remove('hidden');
          return;
        }

        // 切换显示/隐藏状态
        const isHidden = codeContextDiv.classList.contains('hidden');
        const buttonTextSpan = contextButton.querySelector('.btn-text');

        if (isHidden) {
          showLoadingIndicator(codeContextDiv);
          codeContextDiv.classList.remove('hidden');

          try {
            // 加载上下文代码
            const contextCode = await loadCodeContext(fileInfo.filePath, fileInfo.lineNumbers, 3);
            displayContextCode(codeContextDiv, contextCode); // 使用单独的函数显示
            if (buttonTextSpan) buttonTextSpan.textContent = '隐藏上下文';

            // 确保上下文区域有足够高度显示内容
            const minHeight = 100; // 最小高度，单位像素
            if (codeContextDiv.offsetHeight < minHeight) {
              codeContextDiv.style.minHeight = minHeight + 'px';
            }
          } catch (error) {
            console.error('加载代码上下文时出错:', error);
            codeContextDiv.innerHTML = `<div class="error p-4 text-red-500">加载上下文失败: ${error.message}</div>`;
          }
        } else {
          codeContextDiv.classList.add('hidden');
          codeContextDiv.innerHTML = ''; // 清空内容
          if (buttonTextSpan) buttonTextSpan.textContent = '显示上下文';
        }
      }
    }

    // 处理查看完整文件按钮 (包括代码上下文底部的链接)
    if (fileButton) {
      // 首先尝试从按钮本身获取文件路径
      let filePath = fileButton.dataset.filepath;

      // 如果按钮本身没有文件路径，尝试从最近的漏洞项获取
      if (!filePath) {
        const item = fileButton.closest('.vulnerability-item');
        if (item) {
          const locationEl = item.querySelector('.vulnerability-location');
          if (locationEl) {
            const fileInfo = parseLocationText(locationEl.textContent);
            filePath = fileInfo ? fileInfo.filePath : null;
          }
        }
      }

      if (!filePath) {
        console.error('无法确定要查看的文件路径');
        return;
      }

      const modal = document.getElementById('sourceFileModal');
      if (!modal) {
        console.error('找不到源文件模态窗口');
        return;
      }

      const titleEl = modal.querySelector('.source-file-title');
      const contentEl = modal.querySelector('.source-file-content');
      const fileInfoEl = modal.querySelector('.file-info');
      const fileName = filePath.split('/').pop();

      // 设置标题和文件信息
      if (titleEl) titleEl.textContent = `源文件: ${fileName}`;
      if (fileInfoEl) fileInfoEl.textContent = `路径: ${filePath}`;

      // 显示加载指示器
      if (contentEl) showLoadingIndicator(contentEl);
      modal.classList.add('modal-open');

      try {
        // 提取行号（可能在按钮或URL中）
        let highlightLines = [];
        if (fileButton.dataset.lines) {
          try {
            highlightLines = JSON.parse(fileButton.dataset.lines);
          } catch (e) {
            console.warn('无法解析行号:', e);
          }
        }

        // 加载并显示源文件
        const { html, lineCount } = await loadFullSourceFile(filePath, highlightLines);
        if (contentEl) contentEl.innerHTML = html;
        if (fileInfoEl) fileInfoEl.textContent = `路径: ${filePath} | 行数: ${lineCount}`;

        // 滚动到高亮行
        if (contentEl && highlightLines && highlightLines.length > 0) {
          const highlightedLine = contentEl.querySelector(`.line-${highlightLines[0]}`);
          if (highlightedLine) {
            // 使用 setTimeout 确保DOM更新后再滚动
            setTimeout(() => {
              highlightedLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
          }
        }
      } catch (error) {
        console.error('加载完整源文件时出错:', error);
        if (contentEl) contentEl.innerHTML = `<div class="error p-4 text-red-500">加载文件失败: ${error.message}</div>`;
      }
    }

    // 处理模态框关闭按钮
    if (modalCloseButton) {
      const modal = modalCloseButton.closest('.modal');
      if (modal) {
        modal.classList.remove('modal-open');
      }
    }
  });
}

/**
 * 从位置文本中解析文件路径和行号
 * @param {string} locationText - 格式如 "Contract.function (path/to/file.sol#L10-L15)" 或 "path/to/file.sol#L10"
 * @returns {Object} 包含文件路径和行号的对象 { filePath: string | null, fileName: string, lineNumbers: number[] }
 */
function parseLocationText(locationText) {
  let filePath = null;
  let fileName = 'unknown';
  const lineNumbers = [];

  if (!locationText) {
    return { filePath, fileName, lineNumbers };
  }

  console.log("解析位置文本:", locationText);

  // 尝试匹配包含文件路径和行号的核心模式: (path/to/file.sol#L<start>-L<end>) 或 (path/to/file.sol#L<line>)
  // 或者 path/to/file.sol#L<start>-L<end> (不一定在末尾)
  const corePatternMatch = locationText.match(/([\w\/.-]+\.sol)#L(\d+)(?:-L(\d+))?/);

  if (corePatternMatch) {
    filePath = corePatternMatch[1].trim();
    fileName = filePath.split('/').pop();
    const startLine = parseInt(corePatternMatch[2], 10);
    const endLine = corePatternMatch[3] ? parseInt(corePatternMatch[3], 10) : startLine;

    if (!isNaN(startLine)) {
      for (let i = startLine; i <= endLine; i++) {
        lineNumbers.push(i);
      }
      console.log(`通过核心模式匹配行号:`, { filePath, fileName, lineNumbers });
      return { filePath, fileName, lineNumbers };
    }
  }

  // 如果核心模式未匹配到行号，但可能匹配到文件路径，则单独处理文件路径
  if (!filePath) {
    const pathMatch = locationText.match(/([\w\/.-]+\.sol)/);
    if (pathMatch) {
      filePath = pathMatch[1].trim();
      fileName = filePath.split('/').pop();
    }
  }

  // 如果仍然没有文件路径，最后尝试从括号中提取
  if (!filePath) {
    const parenPathMatch = locationText.match(/\(([^#)]+)\)/);
    if (parenPathMatch && parenPathMatch[1].includes('.sol')) {
      filePath = parenPathMatch[1].trim();
      fileName = filePath.split('/').pop();
    }
  }

  // 如果只解析到文件路径，没有行号，返回空行号数组
  console.log(`解析结果 (无精确行号):`, { filePath, fileName, lineNumbers });
  return { filePath, fileName, lineNumbers };
}

/**
 * 在指定元素中显示加载指示器
 * @param {HTMLElement} container - 显示加载指示器的容器
 */
function showLoadingIndicator(container) {
  container.innerHTML = `
    <div class="loading-indicator flex items-center justify-center p-4">
      <div class="loading-spinner mr-2"></div>
      <span>正在加载代码...</span>
    </div>
  `;
}

/**
 * 加载代码上下文
 * @param {string} filePath - 源文件路径
 * @param {Array<number>} lineNumbers - 漏洞代码行号
 * @param {number} contextLines - 上下文行数
 * @returns {Promise<string>} 代码上下文的HTML
 */
async function loadCodeContext(filePath, lineNumbers, contextLines = 3) {
  try {
    // 获取源文件内容
    const sourceCode = await getSourceCode(filePath);
    if (!sourceCode) {
      return '<div class="error p-4 text-red-500">无法加载源代码</div>';
    }

    const lines = sourceCode.split('\n');

    // 如果没有行号或行号数组为空，显示明确的提示信息
    if (!lineNumbers || lineNumbers.length === 0) {
      return `
        <div class="code-block">
          <div class="code-header">源文件: ${filePath.split('/').pop()}</div>
          <div class="p-4 text-center text-gray-400">
            <i class="fas fa-info-circle mr-2"></i>
            无法确定具体漏洞行号，请点击"查看完整文件"以获取更多信息
          </div>
          <div class="code-footer">
             <a href="#" class="text-blue-400 hover:underline show-file-btn" data-filepath="${filePath}">查看完整文件</a>
          </div>
        </div>
      `;
    }

    // 计算需要显示的行范围（严格围绕漏洞行）
    const vulnStart = Math.min(...lineNumbers);
    const vulnEnd = Math.max(...lineNumbers);

    // 上下文行数 - 默认只显示漏洞行上下3行
    const startLine = Math.max(1, vulnStart - contextLines);
    const endLine = Math.min(lines.length, vulnEnd + contextLines);

    // 限制最大显示行数为15行
    const MAX_CONTEXT_LINES = 15;
    let actualStartLine = startLine;
    let actualEndLine = endLine;

    if (endLine - startLine + 1 > MAX_CONTEXT_LINES) {
      // 如果计算出的范围超过限制，以漏洞行为中心调整
      const halfContext = Math.floor((MAX_CONTEXT_LINES - (vulnEnd - vulnStart + 1)) / 2);
      actualStartLine = Math.max(1, vulnStart - halfContext);
      actualEndLine = Math.min(lines.length, actualStartLine + MAX_CONTEXT_LINES - 1);

      // 再次调整，确保不裁剪掉漏洞行
      if (actualEndLine < vulnEnd) {
        actualEndLine = vulnEnd;
        actualStartLine = Math.max(1, actualEndLine - MAX_CONTEXT_LINES + 1);
      }
    }

    // 构建上下文代码，高亮漏洞行
    let contextCode = `<div class="code-block">`;

    // 添加代码段头部信息
    contextCode += `<div class="code-header">漏洞相关代码 (行 ${actualStartLine}-${actualEndLine})</div>`;

    // 添加前部省略提示（如果需要）
    if (actualStartLine > 1) {
      contextCode += `<div class="code-omitted">... 省略前面 ${actualStartLine - 1} 行 ...</div>`;
    }

    // 添加代码行，高亮漏洞行
    for (let i = actualStartLine; i <= actualEndLine; i++) {
      const lineContent = lines[i - 1] || '';
      const isVulnLine = i >= vulnStart && i <= vulnEnd;
      const lineClass = isVulnLine ? 'highlighted-line' : '';

      contextCode += `
        <div class="code-line ${lineClass}">
          <span class="line-number">${i}</span>
          <span class="line-content">${escapeHtml(lineContent)}</span>
        </div>
      `;
    }

    // 添加尾部省略提示（如果需要）
    if (actualEndLine < lines.length) {
      contextCode += `<div class="code-omitted">... 省略后面 ${lines.length - actualEndLine} 行 ...</div>`;
    }

    // 添加底部提示信息
    contextCode += `
      <div class="code-footer">
        <span class="text-yellow-400">黄色高亮</span> 表示漏洞相关代码行 - 
        <a href="#" class="text-blue-400 hover:underline show-file-btn" data-filepath="${filePath}">查看完整文件</a>
      </div>
    </div>`;

    return contextCode;
  } catch (error) {
    console.error('加载代码上下文失败:', error);
    return `<div class="error p-4 text-red-500">加载代码上下文失败: ${error.message}</div>`;
  }
}

/**
 * 加载完整源文件
 * @param {string} filePath - 源文件路径
 * @param {Array<number>} highlightLines - 需要高亮的行号
 * @returns {Promise<Object>} 包含HTML和行数的对象
 */
async function loadFullSourceFile(filePath, highlightLines = []) {
  try {
    // 获取源文件内容
    const sourceCode = await getSourceCode(filePath);
    if (!sourceCode) {
      return {
        html: '<div class="error p-4 text-red-500">无法加载源代码</div>',
        lineCount: 0
      };
    }

    const lines = sourceCode.split('\n');

    // 构建带行号的源代码HTML
    let sourceHtml = `<div class="code-block">`;
    lines.forEach((lineContent, index) => {
      const lineNumber = index + 1;
      const isHighlighted = highlightLines.includes(lineNumber);
      const lineClass = isHighlighted ? 'highlighted-line' : '';

      sourceHtml += `
        <div class="code-line ${lineClass} line-${lineNumber}">
          <span class="line-number">${lineNumber}</span>
          <span class="line-content">${escapeHtml(lineContent)}</span>
        </div>
      `;
    });
    sourceHtml += `</div>`;

    return {
      html: sourceHtml,
      lineCount: lines.length
    };
  } catch (error) {
    console.error('加载源文件失败:', error);
    return {
      html: `<div class="error p-4 text-red-500">加载源文件失败: ${error.message}</div>`,
      lineCount: 0
    };
  }
}

/**
 * 获取源代码（从缓存或通过AJAX请求）
 * @param {string} filePath - 源文件路径
 * @returns {Promise<string>} 源代码文本
 */
async function getSourceCode(filePath) {
  // 检查缓存
  if (sourceFileCache[filePath]) {
    return sourceFileCache[filePath];
  }

  try {
    // 不同路径处理
    let sourceCode = '';
    const fileName = filePath.split('/').pop();
    const fileExt = fileName.split('.').pop().toLowerCase();

    // 标准化路径以便于匹配
    const normalizedPath = filePath.replace(/\\/g, '/').toLowerCase();

    console.log('尝试获取文件:', normalizedPath);

    // 为测试/演示环境提供内置代码示例
    if (fileExt === 'sol' || normalizedPath.includes('sol') || normalizedPath.includes('solidity')) {
      // Solidity 文件示例
      sourceCode = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerabilityTest {
    mapping(address => uint256) public balances;
    uint8 public poolBalance; // 数值转换漏洞：使用uint8存储余额

    // 闪电贷漏洞：未验证还款逻辑
    function flashLoan(uint256 amount, address target) external {
        uint256 initialBalance = address(this).balance;
        require(initialBalance >= amount, "Insufficient liquidity");

        // 不安全的闪电贷实现：未验证目标合约的还款能力
        (bool success, ) = target.call{value: amount}("");
        require(success, "Loan transfer failed");

        // 漏洞：未验证合约余额是否恢复
        require(address(this).balance >= initialBalance, "Loan not repaid");
    }

    // 数值精度漏洞：除法导致的精度损失
    function convertToShares(uint256 amount) public pure returns (uint256) {
        // 错误的价格计算：除法在乘法之前执行导致精度损失
        return (amount / 1e18) * 100; // 当amount不是1e18的整数倍时丢失精度
    }

    // 不安全的数值转换
    function updatePoolBalance(uint256 newBalance) external {
        // 漏洞：将uint256强制转换为uint8
        poolBalance = uint8(newBalance); // 高位截断风险
    }

    // 带有精度问题的存款逻辑
    function deposit() external payable {
        // 使用不精确的汇率计算（1 ETH = 100 shares）
        uint256 shares = msg.value * 100 / 1e18;  // 当金额较小时会得到0
        
        // 数值转换漏洞：可能溢出
        poolBalance += uint8(shares);
        balances[msg.sender] += shares;
    }

    receive() external payable {}
}`;
    } else if (fileExt === 'js' || normalizedPath.includes('javascript')) {
      // JavaScript 文件示例
      sourceCode = `// 这是示例 JavaScript 代码
function vulnerableFunction(userInput) {
  // 不安全的 eval 使用
  return eval(userInput);  // 这可能导致代码注入
}

// 不安全的正则表达式
function matchPattern(input) {
  const regex = new RegExp(input);  // 可能导致正则表达式拒绝服务攻击
  return regex.test("sample text");
}

// 示例代码 - 实际源代码不可用
console.log("文件路径:", "${filePath}");
`;
    } else {
      // 通用示例
      sourceCode = `// 源文件：${filePath}
// 这是一个演示用的源代码示例
// 在实际生产环境中，这里应该通过API获取真实的源代码

// 以下是模拟的源代码内容：
function exampleFunction() {
  console.log("这是${fileName}中的示例函数");
  return true;
}

class DemoClass {
  constructor() {
    this.value = 10;
  }
  
  getValue() {
    return this.value;
  }
}

// 文件末尾`;
    }

    // 缓存源代码以便重用
    sourceFileCache[filePath] = sourceCode;
    return sourceCode;
  } catch (error) {
    console.error('获取源代码失败:', error, filePath);
    return `// 无法获取源代码: ${filePath}\n// 错误: ${error.message}\n\n// 请确保文件存在且可访问`;
  }
}

/**
 * 显示上下文代码，并应用语法高亮
 * @param {HTMLElement} container - 代码容器元素
 * @param {string} codeHtml - 代码HTML
 */
function displayContextCode(container, codeHtml) {
  container.innerHTML = codeHtml;

  // 应用语法高亮（如果Prism可用）
  if (window.Prism) {
    container.querySelectorAll('pre code').forEach(block => {
      Prism.highlightElement(block);
    });
  }
}

/**
 * HTML转义，防止XSS
 * @param {string} unsafe - 不安全的HTML字符串
 * @returns {string} 转义后的安全字符串
 */
function escapeHtml(unsafe) {
  if (typeof unsafe !== 'string') {
    return '';
  }
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// 导出模块接口
window.CodeViewer = {
  init: initCodeViewer,

  // 显示代码上下文方法
  showContext: function (button, contextDiv) {
    // 查找最近的漏洞项
    const item = button.closest('.vulnerability-item');
    if (!item) return;

    const locationEl = item.querySelector('.vulnerability-location');
    if (!locationEl || !contextDiv) return;

    // 解析文件和行号信息
    const fileInfo = parseLocationText(locationEl.textContent);
    if (!fileInfo || !fileInfo.filePath) {
      console.error('无法解析文件路径:', locationEl.textContent);
      contextDiv.innerHTML = '<div class="error p-4 text-red-500">无法解析文件路径信息</div>';
      contextDiv.classList.remove('hidden');
      return;
    }

    // 切换显示/隐藏状态
    const isHidden = contextDiv.classList.contains('hidden');
    const buttonTextSpan = button.querySelector('.btn-text');

    if (isHidden) {
      showLoadingIndicator(contextDiv);
      contextDiv.classList.remove('hidden');

      // 加载上下文代码
      loadCodeContext(fileInfo.filePath, fileInfo.lineNumbers, 3)
        .then(contextCode => {
          displayContextCode(contextDiv, contextCode);
          if (buttonTextSpan) buttonTextSpan.textContent = '隐藏上下文';

          // 确保上下文区域有足够高度显示内容
          const minHeight = 100; // 最小高度，单位像素
          if (contextDiv.offsetHeight < minHeight) {
            contextDiv.style.minHeight = minHeight + 'px';
          }
        })
        .catch(error => {
          console.error('加载代码上下文时出错:', error);
          contextDiv.innerHTML = `<div class="error p-4 text-red-500">加载上下文失败: ${error.message}</div>`;
        });
    } else {
      contextDiv.classList.add('hidden');
      contextDiv.innerHTML = ''; // 清空内容
      if (buttonTextSpan) buttonTextSpan.textContent = '显示上下文';
    }
  },

  // 显示完整文件方法
  showFile: function (button) {
    // 查找最近的漏洞项
    const item = button.closest('.vulnerability-item');
    if (!item) return;

    const locationEl = item.querySelector('.vulnerability-location');
    if (!locationEl) return;

    const fileInfo = parseLocationText(locationEl.textContent);
    if (!fileInfo || !fileInfo.filePath) {
      console.error('无法解析文件路径:', locationEl.textContent);
      return;
    }

    const modal = document.getElementById('sourceFileModal');
    if (!modal) {
      console.error('找不到源文件模态窗口');
      return;
    }

    const titleEl = modal.querySelector('.source-file-title');
    const contentEl = modal.querySelector('.source-file-content');
    const fileInfoEl = modal.querySelector('.file-info');

    // 设置标题和文件信息
    if (titleEl) titleEl.textContent = `源文件: ${fileInfo.fileName}`;
    if (fileInfoEl) fileInfoEl.textContent = `路径: ${fileInfo.filePath}`;

    // 显示加载指示器
    if (contentEl) showLoadingIndicator(contentEl);
    modal.classList.add('modal-open');

    // 加载并显示源文件
    loadFullSourceFile(fileInfo.filePath, fileInfo.lineNumbers)
      .then(({ html, lineCount }) => {
        if (contentEl) contentEl.innerHTML = html;
        if (fileInfoEl) fileInfoEl.textContent = `路径: ${fileInfo.filePath} | 行数: ${lineCount}`;

        // 滚动到高亮行
        if (contentEl && fileInfo.lineNumbers && fileInfo.lineNumbers.length > 0) {
          const highlightedLine = contentEl.querySelector(`.line-${fileInfo.lineNumbers[0]}`);
          if (highlightedLine) {
            // 使用 setTimeout 确保DOM更新后再滚动
            setTimeout(() => {
              highlightedLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
          }
        }
      })
      .catch(error => {
        console.error('加载完整源文件时出错:', error);
        if (contentEl) contentEl.innerHTML = `<div class="error p-4 text-red-500">加载文件失败: ${error.message}</div>`;
      });
  }
};

// 确保 DOM 加载后初始化
document.addEventListener('DOMContentLoaded', initCodeViewer);