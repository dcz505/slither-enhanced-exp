// 全局变量
let reportData = null;
const MAX_HISTORY_ITEMS = 5; // 最大历史记录数量
const MAX_HISTORY_SIZE_MB = 5; // 历史记录最大占用空间（MB）

// 主题切换功能
function setupThemeSwitch() {
  const themeToggleBtn = document.getElementById('themeToggleBtn');

  if (!themeToggleBtn) return;

  // 从localStorage加载主题设置
  const savedTheme = localStorage.getItem('slitherTheme') || 'light';

  // 设置初始主题
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  // 点击事件处理
  themeToggleBtn.addEventListener('click', function () {
    // 获取当前主题
    const currentTheme = document.documentElement.getAttribute('data-theme');
    // 切换到新主题
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    // 更新HTML根元素的data-theme属性
    document.documentElement.setAttribute('data-theme', newTheme);

    // 保存主题设置
    localStorage.setItem('slitherTheme', newTheme);

    // 更新图标
    updateThemeIcon(newTheme);

    // 更新dropArea样式
    updateDropAreaStyle(newTheme);

    console.log('主题已切换为:', newTheme);
  });
}

// 更新dropArea的样式
function updateDropAreaStyle(theme) {
  const dropArea = document.getElementById('dropArea');
  if (!dropArea) return;

  // 移除所有主题相关类
  dropArea.classList.remove('bg-blue-50', 'bg-blue-100', 'border-blue-500');

  // 根据主题设置适当的样式
  if (theme === 'dark') {
    // 深色主题样式已在CSS中通过[data-theme="dark"] #dropArea定义
  } else {
    // 浅色主题，重置为默认样式
    dropArea.classList.add('bg-blue-50');
    dropArea.classList.add('border-dashed');
    dropArea.classList.add('border-blue-300');
  }
}

// 更新主题图标
function updateThemeIcon(theme) {
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  if (!themeToggleBtn) return;

  // 根据当前主题调整图标
  if (theme === 'dark') {
    themeToggleBtn.innerHTML = '<i class="fas fa-shield-alt text-2xl"></i><i class="fas fa-moon text-xs absolute top-0 right-0"></i>';
    themeToggleBtn.title = '切换到浅色模式';
  } else {
    themeToggleBtn.innerHTML = '<i class="fas fa-shield-alt text-2xl"></i><i class="fas fa-sun text-xs absolute top-0 right-0"></i>';
    themeToggleBtn.title = '切换到深色模式';
  }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  // 显示加载指示器
  const loadingIndicator = document.getElementById('loadingIndicator');
  if (loadingIndicator) {
    loadingIndicator.style.display = 'flex';
  }

  // 设置主题切换功能
  setupThemeSwitch();

  // 应用当前主题样式到dropArea
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  updateDropAreaStyle(currentTheme);

  // 设置文件拖放功能
  setupFileDrop();

  // 设置事件监听器 - 上传报告
  const uploadBtn = document.getElementById('uploadReportBtn');
  if (uploadBtn) {
    uploadBtn.addEventListener('click', uploadReport);
  }

  // 设置事件监听器 - 加载示例报告
  const loadExampleBtn = document.getElementById('loadExampleBtn');
  if (loadExampleBtn) {
    loadExampleBtn.addEventListener('click', function () {
      loadDefaultReport();
      // 隐藏拖放区域，因为已经加载了报告
      const dropArea = document.getElementById('dropArea');
      if (dropArea) {
        dropArea.classList.add('hidden');
      }
    });
  }

  // 设置事件监听器 - 导出JSON
  const downloadJsonBtn = document.getElementById('downloadJsonBtn');
  if (downloadJsonBtn) {
    downloadJsonBtn.addEventListener('click', function () {
      downloadReport('json');
    });
  }

  // 设置事件监听器 - 导出Markdown
  const downloadMarkdownBtn = document.getElementById('downloadMarkdownBtn');
  if (downloadMarkdownBtn) {
    downloadMarkdownBtn.addEventListener('click', function () {
      downloadReport('markdown');
    });
  }

  // 设置事件监听器 - 导出PDF
  const downloadPdfBtn = document.getElementById('downloadPdfBtn');
  if (downloadPdfBtn) {
    downloadPdfBtn.addEventListener('click', generatePdfReport);
  }

  // 设置历史记录清除按钮
  const clearHistoryBtn = document.getElementById('clearHistoryBtn');
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', clearHistory);
  }

  // 设置清空当前报告按钮
  const clearCurrentReportBtn = document.getElementById('clearCurrentReportBtn');
  if (clearCurrentReportBtn) {
    clearCurrentReportBtn.addEventListener('click', clearCurrentReport);
  }

  // 设置漏洞筛选器
  setupVulnerabilityFilter();

  // 初始化历史记录菜单
  loadHistoryMenu();

  // 显示初始空白状态
  clearReportDisplay();

  // 隐藏加载指示器
  if (loadingIndicator) {
    loadingIndicator.style.display = 'none';
  }

  // 显示拖放区域
  const dropArea = document.getElementById('dropArea');
  if (dropArea) {
    dropArea.classList.remove('hidden');
  }
});

// 历史记录管理函数
function addToHistory(data, fileName = null) {
  try {
    // 从localStorage获取历史记录
    let history = JSON.parse(localStorage.getItem('slitherReportHistory') || '[]');

    // 准备新的历史记录项
    const now = new Date();
    const newHistoryItem = {
      id: `report_${now.getTime()}`,
      timestamp: now.toISOString(),
      displayName: fileName || `报告-${now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })}`,
      data: data
    };

    // 检查是否已存在相同内容的报告
    const existingIndex = history.findIndex(item =>
      JSON.stringify(item.data) === JSON.stringify(data)
    );

    // 如果存在，则移除旧的
    if (existingIndex > -1) {
      history.splice(existingIndex, 1);
    }

    // 添加新的历史记录项到头部
    history.unshift(newHistoryItem);

    // 限制历史记录数量
    if (history.length > MAX_HISTORY_ITEMS) {
      history = history.slice(0, MAX_HISTORY_ITEMS);
    }

    // 检查历史记录大小
    let historyString = JSON.stringify(history);
    let historySize = new Blob([historyString]).size / (1024 * 1024); // 转换为MB

    // 如果历史记录超过大小限制，移除最老的记录
    while (historySize > MAX_HISTORY_SIZE_MB && history.length > 1) {
      history.pop(); // 移除最后一项
      historyString = JSON.stringify(history);
      historySize = new Blob([historyString]).size / (1024 * 1024);
    }

    // 保存更新后的历史记录
    localStorage.setItem('slitherReportHistory', historyString);

    // 刷新历史记录菜单
    loadHistoryMenu();

    return true;
  } catch (error) {
    console.error('添加到历史记录时出错:', error);
    return false;
  }
}

function loadHistoryMenu() {
  const historyItemsContainer = document.getElementById('historyItems');
  if (!historyItemsContainer) return;

  try {
    // 从localStorage获取历史记录
    const history = JSON.parse(localStorage.getItem('slitherReportHistory') || '[]');

    // 清空容器
    historyItemsContainer.innerHTML = '';

    if (history.length === 0) {
      // 显示无历史记录提示
      historyItemsContainer.innerHTML = '<li class="text-gray-500 text-center py-2 text-sm">暂无历史记录</li>';
      return;
    }

    // 添加历史记录项
    history.forEach(item => {
      const listItem = document.createElement('li');

      const link = document.createElement('a');
      link.className = 'flex items-center justify-between';
      link.dataset.historyId = item.id;

      // 显示名称和时间
      const nameSpan = document.createElement('span');
      nameSpan.className = 'flex-grow truncate';
      nameSpan.textContent = item.displayName;
      link.appendChild(nameSpan);

      // 时间信息作为提示
      const date = new Date(item.timestamp);
      link.title = `加载时间: ${date.toLocaleString('zh-CN')}`;

      // 添加点击事件
      link.addEventListener('click', () => loadReportFromHistory(item.id));

      listItem.appendChild(link);
      historyItemsContainer.appendChild(listItem);
    });
  } catch (error) {
    console.error('加载历史记录菜单时出错:', error);
    historyItemsContainer.innerHTML = '<li class="text-red-500 text-center py-2 text-sm">加载历史记录失败</li>';
  }
}

function loadReportFromHistory(historyId) {
  try {
    // 显示加载指示器
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
      loadingIndicator.style.display = 'flex';
    }

    // 从localStorage获取历史记录
    const history = JSON.parse(localStorage.getItem('slitherReportHistory') || '[]');

    // 查找对应ID的历史记录
    const historyItem = history.find(item => item.id === historyId);

    if (!historyItem) {
      throw new Error('未找到历史记录');
    }

    // 加载报告数据
    loadReport(historyItem.data);

    // 保存为当前报告
    localStorage.setItem('slitherReport', JSON.stringify(historyItem.data));

    // 隐藏拖放区域
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
      dropArea.classList.add('hidden');
    }

    // 隐藏加载指示器
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }

    console.log('从历史记录加载了报告:', historyItem.displayName);
    return true;
  } catch (error) {
    console.error('从历史记录加载报告时出错:', error);

    // 隐藏加载指示器
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }

    alert('加载历史报告失败: ' + error.message);
    return false;
  }
}

function clearHistory() {
  try {
    // 移除历史记录
    localStorage.removeItem('slitherReportHistory');

    // 刷新历史记录菜单
    loadHistoryMenu();

    console.log('历史记录已清除');
    return true;
  } catch (error) {
    console.error('清除历史记录时出错:', error);
    alert('清除历史记录失败: ' + error.message);
    return false;
  }
}

// 加载默认示例报告的函数
function loadDefaultReport() {
  console.log('尝试加载默认示例报告');

  try {
    // 先尝试通过fetch加载，不保存到localStorage，不添加到历史记录
    fetchAndLoadReport('./example-report.json', false, false)
      .catch(error => {
        console.warn('通过fetch加载默认报告失败，尝试使用内置示例:', error);
        // 如果fetch失败，使用内置示例数据
        useBuiltinExampleData();
      });
  } catch (e) {
    console.error('加载默认示例报告过程中发生错误:', e);
    // 所有尝试都失败时使用内置示例
    useBuiltinExampleData();
  }
}

// 使用内置示例数据的函数
function useBuiltinExampleData() {
  console.log('使用内置示例数据');

  // 直接使用example-report.json的内容作为内置示例
  const builtinExample = {
    "summary": {
      "audit_time": "2025-04-20 15:30:10",
      "solc_version": "0.8.17",
      "file_count": 3,
      "contracts": [
        "TokenContract",
        "Vault",
        "Exchange"
      ],
      "vulnerabilities": {
        "high": 1,
        "medium": 2,
        "low": 3,
        "informational": 1
      }
    },
    "vulnerabilities": [
      {
        "name": "不安全的重入漏洞",
        "description": "合约中的withdraw函数在转账前没有更新状态，容易导致重入攻击。",
        "impact": "high",
        "impact_description": "攻击者可以重复提取资金，直到合约余额耗尽，导致资金损失。",
        "recommendation": "遵循检查-效果-交互模式，确保在外部调用前更新所有状态变量。",
        "contract": "Vault",
        "function": "withdraw",
        "filename": "Vault.sol",
        "code": "function withdraw(uint256 amount) public {\n    require(balances[msg.sender] >= amount, \"Insufficient balance\");\n    // VULNERABLE: 在转账前应该更新余额\n    (bool success, ) = msg.sender.call{value: amount}(\"\");\n    require(success, \"Transfer failed\");\n    balances[msg.sender] -= amount;\n}"
      },
      {
        "name": "整数溢出",
        "description": "合约中的_transfer函数没有检查整数溢出，可能导致意外行为。",
        "impact": "medium",
        "impact_description": "在极端情况下，用户余额可能会溢出，导致资金损失或异常行为。",
        "recommendation": "使用SafeMath库或Solidity 0.8.x的内置溢出检查来防止整数溢出。",
        "contract": "TokenContract",
        "function": "_transfer",
        "filename": "TokenContract.sol",
        "code": "function _transfer(address from, address to, uint256 amount) internal {\n    balances[from] -= amount;\n    balances[to] += amount;\n    emit Transfer(from, to, amount);\n}"
      },
      {
        "name": "gas限制问题",
        "description": "循环中的操作可能会超过gas限制，导致交易失败。",
        "impact": "medium",
        "impact_description": "当用户数量增长到一定规模时，交易可能会因为gas限制而失败，影响合约功能。",
        "recommendation": "优化循环逻辑，或者实现分批处理机制。",
        "contract": "Exchange",
        "function": "distributeRewards",
        "filename": "Exchange.sol",
        "code": "function distributeRewards() public {\n    for (uint i = 0; i < users.length; i++) {\n        address user = users[i];\n        uint256 reward = calculateReward(user);\n        balances[user] += reward;\n    }\n}"
      },
      {
        "name": "缺少事件发射",
        "description": "重要的状态变更操作没有发射事件，降低了透明度和可追踪性。",
        "impact": "low",
        "impact_description": "缺少事件使得用户和监控系统难以追踪合约状态变化，降低透明度。",
        "recommendation": "在关键状态变更操作中添加事件发射。",
        "contract": "Vault",
        "function": "setFee",
        "filename": "Vault.sol",
        "code": "function setFee(uint256 newFee) public onlyOwner {\n    fee = newFee;\n    // 缺少事件发射\n}"
      },
      {
        "name": "使用硬编码地址",
        "description": "合约中使用了硬编码的地址，这会降低合约的可移植性和可更新性。",
        "impact": "low",
        "impact_description": "如果硬编码地址需要更改，整个合约需要重新部署，造成不必要的麻烦。",
        "recommendation": "使用可更新的地址存储机制，如通过owner设置地址或使用可升级合约模式。",
        "contract": "Exchange",
        "function": "constructor",
        "filename": "Exchange.sol",
        "code": "constructor() {\n    // 硬编码地址不利于测试和更新\n    tokenAddress = 0x1234567890123456789012345678901234567890;\n}"
      },
      {
        "name": "缺少访问控制",
        "description": "特权函数没有适当的访问控制，允许任何人调用。",
        "impact": "low",
        "impact_description": "任何人都可以调用特权函数，可能导致未经授权的状态变更。",
        "recommendation": "添加适当的访问控制修饰符，如onlyOwner或特定角色检查。",
        "contract": "TokenContract",
        "function": "mint",
        "filename": "TokenContract.sol",
        "code": "function mint(address to, uint256 amount) public {\n    // 缺少访问控制\n    totalSupply += amount;\n    balances[to] += amount;\n    emit Transfer(address(0), to, amount);\n}"
      },
      {
        "name": "函数可见性优化",
        "description": "某些内部函数被标记为public，这可能暴露了不必要的接口。",
        "impact": "informational",
        "impact_description": "虽然不会直接导致安全问题，但良好的可见性设置可以减少攻击面并提高代码质量。",
        "recommendation": "将不需要外部调用的函数设置为internal或private。",
        "contract": "Exchange",
        "function": "calculateReward",
        "filename": "Exchange.sol",
        "code": "function calculateReward(address user) public view returns (uint256) {\n    // 这个函数可以设置为internal\n    return (balances[user] * rewardRate) / 100;\n}"
      }
    ],
    "interval_analysis": {
      "TokenContract": {
        "totalSupply": {
          "interval": "[0, +∞)",
          "type": "uint256"
        },
        "decimals": {
          "interval": "18",
          "type": "uint8"
        }
      },
      "Vault": {
        "fee": {
          "interval": "[0, 500]",
          "type": "uint256"
        },
        "totalDeposits": {
          "interval": "[0, +∞)",
          "type": "uint256"
        }
      }
    }
  };

  // 加载内置示例数据，不保存到localStorage
  loadReport(builtinExample);

  // 隐藏加载指示器
  const loadingIndicator = document.getElementById('loadingIndicator');
  if (loadingIndicator) {
    loadingIndicator.style.display = 'none';
  }
}

// 用于获取并加载报告的函数
function fetchAndLoadReport(url, saveToLocalStorage = true, addToHistoryRecord = true) {
  console.log('开始获取报告:', url);

  // 显示加载指示器
  const loadingIndicator = document.getElementById('loadingIndicator');
  if (loadingIndicator) {
    loadingIndicator.style.display = 'flex';
  }

  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      loadReport(data);
      // 可选保存到 localStorage
      if (saveToLocalStorage) {
        localStorage.setItem('slitherReport', JSON.stringify(data));
      }
      // 可选添加到历史记录
      if (addToHistoryRecord) {
        const fileName = url.split('/').pop().replace('.json', '');
        addToHistory(data, fileName);
      }

      // 隐藏拖放区域
      const dropArea = document.getElementById('dropArea');
      if (dropArea) {
        dropArea.classList.add('hidden');
      }

      // 隐藏加载指示器
      if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
      }

      return data;
    })
    .catch(error => {
      console.error('获取或解析报告失败:', error);

      // 隐藏加载指示器
      if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
      }

      // 对于网络错误，不显示弹窗，而是返回rejected Promise以便调用者处理
      return Promise.reject(error);
    });
}

// 清空报告显示区域的函数
function clearReportDisplay() {
  // 清空各个显示区域
  const areas = [
    'auditTime', 'solcVersion', 'fileCount', 'contractCount',
    'highCount', 'mediumCount', 'lowCount', 'infoCount',
    'highBar', 'mediumBar', 'lowBar', 'infoBar',
    'contractsList', 'vulnerabilitiesContainer'
  ];

  areas.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      if (id === 'vulnerabilitiesContainer') {
        element.innerHTML = `
          <div id="noVulnerabilities" class="text-center py-10 text-gray-500">
            <i class="fas fa-shield-check text-6xl text-gray-300 mb-4"></i>
            <p class="text-lg">未发现漏洞或尚未加载报告</p>
            <p class="text-sm text-gray-400 mt-2">上传报告文件或选择示例报告开始分析</p>
          </div>
        `;
      } else {
        element.innerHTML = id.includes('Count') ? '0' : '-';
      }

      if (id.includes('Bar')) {
        element.style.width = '0%';
      }
    }
  });

  // 注释掉区间分析清理
  // renderIntervalAnalysis({});
}

// 设置文件拖放功能
function setupFileDrop() {
  const dropArea = document.getElementById('dropArea') || document.body;

  // 确保拖放区域可见
  if (dropArea.id === 'dropArea') {
    dropArea.classList.remove('hidden');
  }

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
    document.body.addEventListener(eventName, () => {
      if (dropArea.id === 'dropArea') {
        dropArea.classList.remove('hidden');
      }
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  function highlight() {
    if (dropArea.id === 'dropArea') {
      // 检查当前主题
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';

      if (currentTheme === 'dark') {
        // 在深色主题下使用不同的高亮样式
        dropArea.classList.add('active');
      } else {
        // 浅色主题保持原样式
        dropArea.classList.add('border-blue-500');
        dropArea.classList.add('bg-blue-100');
      }
    } else {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      if (currentTheme === 'dark') {
        dropArea.classList.add('bg-opacity-10');
        dropArea.classList.add('bg-primary');
      } else {
        dropArea.classList.add('bg-blue-50');
      }
    }
  }

  function unhighlight() {
    if (dropArea.id === 'dropArea') {
      // 移除所有可能的高亮样式
      dropArea.classList.remove('active');
      dropArea.classList.remove('border-blue-500');
      dropArea.classList.remove('bg-blue-100');
    } else {
      dropArea.classList.remove('bg-blue-50');
      dropArea.classList.remove('bg-opacity-10');
      dropArea.classList.remove('bg-primary');
    }
  }

  document.body.addEventListener('drop', handleDrop, false);
  dropArea.addEventListener('drop', handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length) {
      handleFiles(files);
    }
  }
}

// 文件上传处理函数
function uploadReport() {
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = '.json,application/json';
  fileInput.style.display = 'none';

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      handleFiles(e.target.files);
    }
  });

  document.body.appendChild(fileInput);
  fileInput.click();

  // 清理DOM
  setTimeout(() => {
    document.body.removeChild(fileInput);
  }, 1000);
}

function handleFiles(files) {
  // 显示加载指示器
  const loadingIndicator = document.getElementById('loadingIndicator');
  if (loadingIndicator) {
    loadingIndicator.style.display = 'flex';
  }

  if (files.length === 0) {
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    alert('未选择任何文件');
    return;
  }

  const file = files[0];
  if (file.type === 'application/json' || file.name.endsWith('.json')) {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        loadReport(data);
        // 保存到 localStorage
        localStorage.setItem('slitherReport', e.target.result);
        // 添加到历史记录，使用文件名作为显示名称
        addToHistory(data, file.name.replace('.json', ''));

        // 隐藏加载指示器
        if (loadingIndicator) {
          loadingIndicator.style.display = 'none';
        }

        // 隐藏拖放区域
        const dropArea = document.getElementById('dropArea');
        if (dropArea) {
          dropArea.classList.add('hidden');
        }
      } catch (error) {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        alert('无法解析JSON文件: ' + error.message);
      }
    };

    reader.onerror = () => {
      if (loadingIndicator) loadingIndicator.style.display = 'none';
      alert('读取文件时发生错误');
    };

    reader.readAsText(file);
  } else {
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    alert('请选择一个JSON格式的Slither审计报告文件');
  }
}

// 加载报告数据 - 重构以优先处理 results.detectors 结构
function loadReport(data) {
  try {
    reportData = data; // 保存原始数据

    // 更灵活地处理不同格式的报告输出
    if (!reportData) {
      console.error('报告加载失败: 无数据');
      alert('报告加载失败: 无数据');
      clearReportDisplay();
      return;
    }

    // 尝试获取漏洞数据 (支持多种可能的格式)
    let detectors = [];

    // 1. 如果是Slither标准JSON格式
    if (reportData.results && reportData.results.detectors) {
      // t1.json 格式
      detectors = reportData.results.detectors;
    }
    // 2. 如果是简化的detectors数组
    else if (reportData.detectors) {
      detectors = reportData.detectors;
    }
    // 3. 如果报告本身就是一个detectors数组
    else if (Array.isArray(reportData) && reportData.length > 0 && (reportData[0].check || reportData[0].impact)) {
      detectors = reportData;
    }
    // 4. 使用增强型的漏洞报告格式 (包含更详细信息的格式)
    else if (reportData.vulnerabilities && Array.isArray(reportData.vulnerabilities)) {
      detectors = reportData.vulnerabilities;
    }

    console.log('检测到的漏洞数量:', detectors.length);

    if (detectors.length === 0) {
      console.warn('未在报告中找到任何漏洞检测结果');
      // 可以继续处理，显示一个空报告
    }

    // 1. 计算漏洞统计
    const vulnerabilityCounts = { high: 0, medium: 0, low: 0, informational: 0 };

    // 处理不同格式的impact字段
    detectors.forEach(detector => {
      let impactLower = '';

      if (detector.impact) {
        // 标准格式或增强格式
        impactLower = detector.impact.toLowerCase();
      } else if (detector.severity) {
        // 另一种可能的格式
        impactLower = detector.severity.toLowerCase();
      }

      // 标准化impact值
      if (impactLower === 'high' || impactLower === 'critical') {
        vulnerabilityCounts.high++;
      } else if (impactLower === 'medium') {
        vulnerabilityCounts.medium++;
      } else if (impactLower === 'low') {
        vulnerabilityCounts.low++;
      } else if (impactLower === 'informational' || impactLower === 'info') {
        vulnerabilityCounts.informational++;
      }
    });

    // 如果有summary字段中包含漏洞统计，则直接使用
    if (reportData.summary && reportData.summary.vulnerabilities) {
      const summaryStats = reportData.summary.vulnerabilities;
      if (summaryStats.high !== undefined) vulnerabilityCounts.high = summaryStats.high;
      if (summaryStats.medium !== undefined) vulnerabilityCounts.medium = summaryStats.medium;
      if (summaryStats.low !== undefined) vulnerabilityCounts.low = summaryStats.low;
      if (summaryStats.informational !== undefined) vulnerabilityCounts.informational = summaryStats.informational;
    }

    // 渲染漏洞统计
    renderVulnerabilityStats(vulnerabilityCounts);

    // 2. 渲染摘要信息
    let summary = calculateSummary(reportData, detectors);

    // 如果报告中已包含摘要信息，则优先使用报告中的摘要
    if (reportData.summary) {
      summary = {
        auditTime: reportData.summary.audit_time || new Date().toLocaleString(),
        solcVersion: reportData.summary.solc_version || '-',
        fileCount: reportData.summary.file_count || 0,
        contractCount: (reportData.summary.contracts && reportData.summary.contracts.length) || 0
      };
    }

    renderSummary(summary);

    // 3. 提取并渲染合约列表
    const contracts = extractContracts(reportData, detectors);
    renderContractsList(contracts);

    // 4. 渲染漏洞列表
    renderVulnerabilities(detectors);

    // 5. 渲染区间分析结果 (如果有的话)
    // 注释掉区间分析渲染，因为暂时不需要此功能
    // if (reportData.interval_analysis) {
    //   renderIntervalAnalysis(reportData.interval_analysis);
    // }

    console.log('报告加载完成');

    // 将报告保存到localStorage（仅在格式正确时）
    try {
      localStorage.setItem('slitherReport', JSON.stringify(reportData));
    } catch (storageError) {
      console.warn('无法保存报告到本地存储:', storageError);
    }

    // 在报告加载完成后，安全地更新PDF内容
    setTimeout(() => {
      try {
        updatePdfContent();
      } catch (pdfError) {
        console.warn('更新PDF内容时出错:', pdfError);
      }
    }, 100);

    // 重新初始化代码查看器
    setTimeout(() => {
      if (window.CodeViewer && window.CodeViewer.init) {
        console.log('重新初始化CodeViewer模块...');
        window.CodeViewer.init();
      }
    }, 300);


  } catch (error) {
    console.error('加载报告时出错:', error);
    alert('加载报告失败: ' + error.message);
    // clearReportDisplay();
  }
}

// 新增：计算摘要信息的辅助函数 (示例)
function calculateSummary(data, detectors) {
  const summary = {
    auditTime: new Date().toLocaleString(), // 使用当前时间作为示例
    solcVersion: '-',
    fileCount: 0,
    contractCount: 0
  };

  // 尝试提取 solc 版本
  // 在 t1.json 格式中，可能没有直接提供 solc 版本
  // 尝试从 pragma 检测中找到它
  if (detectors && detectors.length > 0) {
    for (const detector of detectors) {
      if (detector.check === 'solc-version' && detector.elements && detector.elements.length > 0) {
        const element = detector.elements[0];
        if (element.type === 'pragma' && element.type_specific_fields && element.type_specific_fields.directive) {
          summary.solcVersion = element.type_specific_fields.directive.join('');
          break;
        }
      }
    }
  }

  const filenames = new Set();
  const contractNames = new Set();

  // 从 detectors 中提取文件和合约信息
  if (detectors && detectors.length > 0) {
    detectors.forEach(detector => {
      if (detector.elements) {
        detector.elements.forEach(element => {
          if (element.source_mapping && element.source_mapping.filename_relative) {
            filenames.add(element.source_mapping.filename_relative);
          }
          if (element.type === 'contract' || (element.type_specific_fields && element.type_specific_fields.parent && element.type_specific_fields.parent.type === 'contract')) {
            const contractElement = element.type === 'contract' ? element : element.type_specific_fields.parent;
            if (contractElement.name) {
              contractNames.add(contractElement.name);
            }
          }
          else if (element.type === 'function' && element.type_specific_fields && element.type_specific_fields.parent && element.type_specific_fields.parent.type === 'contract') {
            if (element.type_specific_fields.parent.name) {
              contractNames.add(element.type_specific_fields.parent.name);
            }
          }
        });
      }
    });
  }

  summary.fileCount = filenames.size;
  summary.contractCount = contractNames.size;

  return summary;
}

// 新增：提取合约信息的辅助函数
function extractContracts(data, detectors) {
  // 合约数组
  const contracts = [];
  const contractsMap = new Map(); // 使用Map避免重复

  // 从漏洞数据中提取合约信息
  // 情况1: 增强型格式的报告，直接包含contracts数组
  if (data.summary && data.summary.contracts && Array.isArray(data.summary.contracts)) {
    data.summary.contracts.forEach(contractName => {
      if (!contractsMap.has(contractName)) {
        contractsMap.set(contractName, {
          name: contractName,
          file: '未知文件',
          status: '已审计'
        });
      }
    });
  }

  // 情况2: 标准格式，从detectors中提取
  if (detectors && detectors.length > 0) {
    detectors.forEach(detector => {
      // 使用增强型格式中的contract和filename字段
      if (detector.contract && detector.filename) {
        const contractKey = `${detector.contract}:${detector.filename}`;
        if (!contractsMap.has(contractKey)) {
          contractsMap.set(contractKey, {
            name: detector.contract,
            file: detector.filename,
            status: '已审计',
            vulnerability_count: 1
          });
        } else {
          const contract = contractsMap.get(contractKey);
          contract.vulnerability_count = (contract.vulnerability_count || 0) + 1;
        }
      }
      // 从elements中提取
      else if (detector.elements) {
        detector.elements.forEach(element => {
          let contractName = '';
          let filename = '';

          // 提取合约名称
          if (element.type === 'contract' && element.name) {
            contractName = element.name;
          } else if (element.type_specific_fields && element.type_specific_fields.parent && element.type_specific_fields.parent.type === 'contract') {
            contractName = element.type_specific_fields.parent.name;
          }

          // 提取文件名
          if (element.source_mapping) {
            filename = element.source_mapping.filename_relative || element.source_mapping.filename_short || '';
          }

          if (contractName && filename) {
            const contractKey = `${contractName}:${filename}`;
            if (!contractsMap.has(contractKey)) {
              contractsMap.set(contractKey, {
                name: contractName,
                file: filename,
                status: '已审计',
                vulnerability_count: 1
              });
            } else {
              const contract = contractsMap.get(contractKey);
              contract.vulnerability_count = (contract.vulnerability_count || 0) + 1;
            }
          }
        });
      }
    });
  }

  // 将Map转换为数组
  for (const contract of contractsMap.values()) {
    contracts.push(contract);
  }

  return contracts;
}

// 渲染报告摘要
function renderSummary(summary) {
  const auditTimeEl = document.getElementById('auditTime');
  const solcVersionEl = document.getElementById('solcVersion');
  const fileCountEl = document.getElementById('fileCount');
  const contractCountEl = document.getElementById('contractCount');

  // 更新主界面
  if (auditTimeEl) auditTimeEl.textContent = summary.auditTime || '-';
  if (solcVersionEl) solcVersionEl.textContent = summary.solcVersion || '-';
  if (fileCountEl) fileCountEl.textContent = summary.fileCount || '0';
  if (contractCountEl) contractCountEl.textContent = summary.contractCount || '0';

  // 更新PDF隐藏元素
  const pdfAuditTime = document.getElementById('pdf-auditTime');
  const pdfSolcVersion = document.getElementById('pdf-solcVersion');
  const pdfFileCount = document.getElementById('pdf-fileCount');
  const pdfContractCount = document.getElementById('pdf-contractCount');

  if (pdfAuditTime) pdfAuditTime.textContent = summary.auditTime || '-';
  if (pdfSolcVersion) pdfSolcVersion.textContent = summary.solcVersion || '-';
  if (pdfFileCount) pdfFileCount.textContent = summary.fileCount || '0';
  if (pdfContractCount) pdfContractCount.textContent = summary.contractCount || '0';
}

// 渲染漏洞统计 - 修改为使用传入的统计对象
function renderVulnerabilityStats(counts) {
  const stats = {
    high: counts.high || 0,
    medium: counts.medium || 0,
    low: counts.low || 0,
    informational: counts.informational || 0,
  };
  const total = stats.high + stats.medium + stats.low + stats.informational;

  const highCountEl = document.getElementById('highCount');
  const mediumCountEl = document.getElementById('mediumCount');
  const lowCountEl = document.getElementById('lowCount');
  const infoCountEl = document.getElementById('infoCount');
  const highBarEl = document.getElementById('highBar');
  const mediumBarEl = document.getElementById('mediumBar');
  const lowBarEl = document.getElementById('lowBar');
  const infoBarEl = document.getElementById('infoBar');

  if (highCountEl) highCountEl.textContent = stats.high;
  if (mediumCountEl) mediumCountEl.textContent = stats.medium;
  if (lowCountEl) lowCountEl.textContent = stats.low;
  if (infoCountEl) infoCountEl.textContent = stats.informational;

  // 计算百分比并更新进度条
  const calculateWidth = (count) => (total > 0 ? (count / total * 100).toFixed(2) : 0);

  if (highBarEl) highBarEl.style.width = `${calculateWidth(stats.high)}%`;
  if (mediumBarEl) mediumBarEl.style.width = `${calculateWidth(stats.medium)}%`;
  if (lowBarEl) lowBarEl.style.width = `${calculateWidth(stats.low)}%`;
  if (infoBarEl) infoBarEl.style.width = `${calculateWidth(stats.informational)}%`;

  // 更新PDF隐藏内容
  const pdfHigh = document.getElementById('pdf-highCount');
  const pdfMedium = document.getElementById('pdf-mediumCount');
  const pdfLow = document.getElementById('pdf-lowCount');
  const pdfInfo = document.getElementById('pdf-infoCount');
  if (pdfHigh) pdfHigh.textContent = stats.high;
  if (pdfMedium) pdfMedium.textContent = stats.medium;
  if (pdfLow) pdfLow.textContent = stats.low;
  if (pdfInfo) pdfInfo.textContent = stats.informational;
}

// 渲染合约列表
function renderContractsList(contracts) {
  const contractsList = document.getElementById('contractsList');
  if (!contractsList) {
    console.error('找不到合约列表元素');
    return;
  }

  // 清空现有内容
  contractsList.innerHTML = '';

  // 如果没有合约，显示提示信息
  if (!contracts || contracts.length === 0) {
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = `
      <td colspan="3" class="text-center py-4 text-gray-500">
        <i class="fas fa-folder-open text-gray-300 text-2xl mb-2"></i>
        <p>未发现合约</p>
      </td>
    `;
    contractsList.appendChild(emptyRow);
    return;
  }

  // 添加合约行
  contracts.forEach(contract => {
    const row = document.createElement('tr');
    row.className = 'hover'; // 使用DaisyUI的hover效果

    // 设置合约状态样式
    let statusClass = 'badge-info';
    let statusIcon = 'fa-check-circle';
    let statusText = contract.status || '已审计';

    // 根据漏洞数量设置状态
    if (contract.vulnerability_count > 0) {
      statusClass = 'badge-warning';
      statusIcon = 'fa-exclamation-triangle';
      statusText = `${contract.vulnerability_count}个问题`;
    }

    row.innerHTML = `
      <td class="font-medium">
        <div class="flex items-center">
          <i class="fas fa-file-contract text-primary mr-2"></i>
          ${contract.name || '未命名合约'}
        </div>
      </td>
      <td class="text-gray-600 truncate max-w-xs" title="${contract.file || '未知文件'}">
        ${contract.file || '未知文件'}
      </td>
      <td>
        <span class="badge ${statusClass} gap-1">
          <i class="fas ${statusIcon} text-xs"></i>
          ${statusText}
                </span>
            </td>
        `;

    contractsList.appendChild(row);
  });
}

// 渲染漏洞详情，支持多种漏洞数据格式
function renderVulnerabilities(detectors) {
  // 获取容器元素
  const container = document.getElementById('vulnerabilitiesContainer');
  const noVulnDiv = document.getElementById('noVulnerabilities');
  const template = document.getElementById('vulnerabilityTemplate');

  if (!container || !template) {
    console.error('找不到漏洞容器或模板元素');
    return;
  }

  // 清空原有内容
  container.innerHTML = '';

  // 如果没有漏洞，显示无漏洞提示
  if (!detectors || detectors.length === 0) {
    if (noVulnDiv) {
      container.appendChild(noVulnDiv);
      noVulnDiv.style.display = 'block';
    }
    return;
  }

  // 隐藏无漏洞提示
  if (noVulnDiv) {
    noVulnDiv.style.display = 'none';
  }

  // 遍历漏洞数据
  detectors.forEach((detector, index) => {
    // 克隆模板
    const vulnNode = template.content.cloneNode(true);
    const vulnItem = vulnNode.querySelector('.vulnerability-item');

    // 处理漏洞严重程度
    let impact = '';
    if (detector.impact) {
      impact = detector.impact.toLowerCase();
    } else if (detector.severity) {
      impact = detector.severity.toLowerCase();
    }

    // 设置数据属性，用于筛选
    vulnItem.setAttribute('data-impact', impact);

    // 为不同严重程度设置不同的CSS类
    const badgeEl = vulnItem.querySelector('.severity-badge');
    const severityClass = getSeverityClass(impact);
    if (badgeEl) {
      badgeEl.classList.add(...severityClass);
      badgeEl.textContent = getSeverityInitial(impact);
      badgeEl.title = getSeverityDescription(impact);
    }

    // 处理漏洞标题
    const titleEl = vulnItem.querySelector('.vulnerability-title');
    if (titleEl) {
      // 处理不同格式的漏洞名称/描述
      if (detector.name) {
        // 增强型报告格式
        titleEl.textContent = detector.name;
      } else if (detector.check) {
        // Slither原始格式
        titleEl.textContent = `${detector.check} ${detector.impact ? `(${detector.impact})` : ''}`;
      } else if (detector.description) {
        // 尝试从描述中提取简短标题
        const shortDesc = detector.description.split('\n')[0].substring(0, 100);
        titleEl.textContent = shortDesc;
      }
    }

    // 设置漏洞位置信息
    const locationEl = vulnItem.querySelector('.vulnerability-location');
    if (locationEl) {
      let locationString = '';
      // 优先使用包含行号的描述（来自Slither原始格式）
      if (detector.description && detector.description.includes('#L')) {
        locationString = detector.description.split('\n')[0]; // 通常第一行包含位置信息
      } else if (detector.first_markdown_element) { // 备选方案
        locationString = detector.first_markdown_element;
      } else if (detector.contract && detector.function) {
        // 增强型格式，但可能缺少行号，尝试组合
        locationString = `${detector.contract}.${detector.function}`;
        if (detector.filename) {
          locationString += ` (${detector.filename})`;
        }
      } else if (detector.filename) {
        // 只有文件名
        locationString = detector.filename;
      } else if (detector.elements && detector.elements.length > 0) {
        // 最后的备选，从elements构造（可能不含行号）
        const element = detector.elements[0];
        if (element.type === 'function' && element.name) {
          locationString += element.name;
          if (element.type_specific_fields?.parent?.name) {
            locationString = element.type_specific_fields.parent.name + '.' + locationString;
          }
        }
        if (element.source_mapping?.filename_short) {
          if (locationString) locationString += ' ';
          locationString += `(${element.source_mapping.filename_short})`;
        }
      }
      locationEl.textContent = locationString || '未知位置';
    }

    // 设置漏洞描述
    const descEl = vulnItem.querySelector('.vulnerability-description');
    if (descEl) {
      descEl.textContent = detector.description || '';
    }

    // 设置漏洞影响
    const impactEl = vulnItem.querySelector('.vulnerability-impact');
    if (impactEl) {
      if (detector.impact_description) {
        // 增强型报告格式
        impactEl.textContent = detector.impact_description;
      } else {
        // 标准格式，使用通用说明
        impactEl.textContent = `此漏洞被标记为 ${getSeverityDescription(impact)} 级别影响，可能会${getImpactDescription(impact)}`;
      }
    }

    // 设置漏洞修复建议
    const recEl = vulnItem.querySelector('.vulnerability-recommendation');
    if (recEl) {
      if (detector.recommendation) {
        // 增强型报告格式
        recEl.textContent = detector.recommendation;
      } else {
        // 标准格式，使用通用建议
        recEl.textContent = getRecommendationByDetectorType(detector.check || '');
      }
    }

    // 设置漏洞代码
    const codeEl = vulnItem.querySelector('.vulnerability-code');
    if (codeEl) {
      // 增强型报告格式，直接使用code字段
      if (detector.code) {
        codeEl.textContent = detector.code;
        // 尝试进行代码高亮
        try {
          if (Prism) {
            Prism.highlightElement(codeEl);
          }
        } catch (e) {
          console.warn('代码高亮失败:', e);
        }
      } else if (detector.elements && detector.elements.length > 0) {
        // Slither原始格式，尝试从elements中提取代码信息
        const element = detector.elements[detector.elements.length > 1 ? 1 : 0]; // 通常第二个元素包含更具体的代码
        if (element && element.name) {
          codeEl.textContent = element.name;
          // 为了视觉效果，添加一些上下文
          if (element.type === 'node') {
            codeEl.textContent = `// 在函数中:\n${element.name};`;
          } else if (element.type === 'function') {
            codeEl.textContent = `function ${element.name}() {\n    // 漏洞代码\n}`;
          }

          // 尝试代码高亮
          try {
            if (Prism) {
              Prism.highlightElement(codeEl);
            }
          } catch (e) {
            console.warn('代码高亮失败:', e);
          }
        }
      }
    }

    // 设置代码查看按钮事件
    const contextBtn = vulnItem.querySelector('.show-context-btn');
    const fileBtn = vulnItem.querySelector('.show-file-btn');
    const contextDiv = vulnItem.querySelector('.code-context');

    // 保存漏洞数据到按钮的dataset中，供代码查看模块使用
    if (contextBtn && fileBtn) {
      // 提取文件路径、行号等信息
      let filepath = '';
      let lines = [];

      if (detector.filename) {
        // 增强型报告格式，优先使用filename
        filepath = detector.filename;
      }

      // 优先从 element.source_mapping 获取行号
      if (detector.elements && detector.elements.length > 0 && detector.elements[0].source_mapping) {
        const sm = detector.elements[0].source_mapping;
        // 如果filepath尚未设置，从source_mapping中获取
        if (!filepath) {
          filepath = sm.filename_relative || sm.filename_short || '';
        }
        // 获取行号数组
        if (sm.lines && sm.lines.length > 0) {
          lines = sm.lines;
        }
      }

      // 如果从source_mapping未获取到行号，尝试从 description 或 first_markdown_element 解析
      if (lines.length === 0) {
        const locationText = detector.description || detector.first_markdown_element || '';
        const lineMatch = locationText.match(/#L(\d+)(?:-L(\d+))?$/);
        if (lineMatch) {
          const startLine = parseInt(lineMatch[1], 10);
          const endLine = lineMatch[2] ? parseInt(lineMatch[2], 10) : startLine;
          if (!isNaN(startLine)) {
            for (let i = startLine; i <= endLine; i++) {
              lines.push(i);
            }
            // 如果filepath尚未设置，尝试从这里解析
            if (!filepath) {
              filepath = locationText.substring(0, locationText.lastIndexOf('#L')).trim();
              const pathInParens = filepath.match(/\(([^)]+)\)$/);
              if (pathInParens) {
                filepath = pathInParens[1].trim();
              } else {
                const parts = filepath.split(' ');
                filepath = parts.length > 1 ? parts[parts.length - 1] : parts[0];
              }
            }
          }
        }
      }

      // 如果仍然没有文件路径，使用 'unknown'
      if (!filepath) {
        filepath = 'unknown';
      }

      // 设置数据属性
      contextBtn.dataset.filepath = filepath;
      contextBtn.dataset.lines = JSON.stringify(lines);
      fileBtn.dataset.filepath = filepath;

      // 添加特定的CSS类，供事件委托使用
      contextBtn.classList.add('show-context-btn');
      fileBtn.classList.add('show-file-btn');

      // 移除个别监听器，改为使用事件委托 (在code-viewer.js中的setupEventDelegation实现)
      /*
      contextBtn.addEventListener('click', function () {
        // 代码上下文查看逻辑，通过CodeViewer模块处理
        if (window.CodeViewer) {
          window.CodeViewer.showContext(this, contextDiv);
        } else {
          console.error('CodeViewer模块未初始化');
        }
      });

      fileBtn.addEventListener('click', function () {
        // 完整文件查看逻辑，通过CodeViewer模块处理
        if (window.CodeViewer) {
          window.CodeViewer.showFile(this);
        } else {
          console.error('CodeViewer模块未初始化');
        }
      });
      */
    }

    // 添加到容器
    container.appendChild(vulnNode);
  });
}

// 获取漏洞严重程度对应的CSS类数组
function getSeverityClass(severity) {
  severity = severity.toLowerCase();
  if (severity === 'high' || severity === 'critical') return ['bg-red-600', 'text-white', 'py-1', 'px-2', 'rounded-md', 'text-xs'];
  if (severity === 'medium') return ['bg-orange-500', 'text-white', 'py-1', 'px-2', 'rounded-md', 'text-xs'];
  if (severity === 'low') return ['bg-yellow-500', 'text-white', 'py-1', 'px-2', 'rounded-md', 'text-xs'];
  return ['bg-blue-500', 'text-white', 'py-1', 'px-2', 'rounded-md', 'text-xs']; // informational
}

// 获取严重程度对应的字母标识
function getSeverityInitial(severity) {
  severity = severity.toLowerCase();
  if (severity === 'high' || severity === 'critical') return 'H';
  if (severity === 'medium') return 'M';
  if (severity === 'low') return 'L';
  return 'I'; // informational
}

// 获取漏洞影响的通用描述
function getImpactDescription(severity) {
  severity = severity.toLowerCase();
  if (severity === 'high' || severity === 'critical') {
    return '导致严重的资金损失或合约功能完全受损';
  } else if (severity === 'medium') {
    return '对合约功能产生部分影响或在特定条件下导致资金损失';
  } else if (severity === 'low') {
    return '在特殊情况下对合约产生轻微影响';
  } else {
    return '不直接影响合约安全，但可能影响代码质量或最佳实践';
  }
}

// 根据漏洞类型获取通用修复建议
function getRecommendationByDetectorType(detectorType) {
  switch (detectorType) {
    case 'arbitrary-send-eth':
      return '验证转账目标地址，限制可接收资金的地址列表，实施多签或时间锁等额外安全措施。';
    case 'divide-before-multiply':
      return '调整计算顺序，先进行乘法运算后进行除法，以防止因舍入误差导致的精度损失。';
    case 'missing-zero-check':
      return '添加对关键地址参数的零地址检查，防止向零地址发送资金或授权。';
    case 'solc-version':
      return '更新到最新稳定版本的Solidity编译器，以避免已知的编译器问题。';
    case 'low-level-calls':
      return '谨慎使用低级调用，确保所有外部调用都有适当的错误处理和状态检查。';
    default:
      return '请参考详细的审计报告或咨询安全专家获取针对此问题的具体修复建议。';
  }
}

// 渲染区间分析结果
function renderIntervalAnalysis(intervalData) {
  // // 检查必要的DOM元素是否存在
  // const container = document.getElementById('intervalAnalysisContainer');
  // const pdfContainer = document.getElementById('pdf-intervalAnalysisContainer');
  // const section = document.getElementById('intervalAnalysisSection');
  // const pdfSection = document.getElementById('pdf-intervalAnalysisSection');

  // // 如果任何必要元素不存在，则直接返回
  // if (!container || !pdfContainer || !section || !pdfSection) {
  //   console.log('区间分析所需的DOM元素不存在，跳过渲染');
  //   return;
  // }

  // container.innerHTML = '';
  // pdfContainer.innerHTML = '';

  // if (!intervalData || Object.keys(intervalData).length === 0) {
  //   section.style.display = 'none';
  //   pdfSection.style.display = 'none';
  //   return;
  // }

  // section.style.display = 'block';
  // pdfSection.style.display = 'block';

  // for (const [contractName, variables] of Object.entries(intervalData)) {
  //   // 主界面渲染
  //   const contractDiv = document.createElement('div');
  //   contractDiv.className = 'mb-6';

  //   contractDiv.innerHTML = `
  //           <h3 class="text-lg font-medium text-gray-800 mb-3">${contractName}</h3>
  //       `;

  //   const table = document.createElement('table');
  //   table.className = 'table w-full';

  //   table.innerHTML = `
  //           <thead>
  //               <tr>
  //                   <th class="bg-gray-50">变量名</th>
  //                   <th class="bg-gray-50">值区间</th>
  //                   <th class="bg-gray-50">类型</th>
  //               </tr>
  //           </thead>
  //           <tbody></tbody>
  //       `;

  //   const tbody = table.querySelector('tbody');

  //   for (const [varName, info] of Object.entries(variables)) {
  //     const row = document.createElement('tr');

  //     row.innerHTML = `
  //               <td>${varName}</td>
  //               <td><span class="interval-value">${info.interval || '未知'}</span></td>
  //               <td>${info.type || '未知'}</td>
  //           `;

  //     tbody.appendChild(row);
  //   }

  //   contractDiv.appendChild(table);
  //   container.appendChild(contractDiv);

  //   // PDF版本渲染
  //   const pdfContractDiv = document.createElement('div');
  //   pdfContractDiv.className = 'mb-6';
  //   pdfContractDiv.innerHTML = `<h3 class="text-lg font-medium mb-3">${contractName}</h3>`;

  //   const pdfTable = document.createElement('table');
  //   pdfTable.className = 'w-full';
  //   pdfTable.setAttribute('border', '1');
  //   pdfTable.setAttribute('cellpadding', '5');

  //   pdfTable.innerHTML = `
  //     <thead>
  //       <tr>
  //           <th>变量名</th>
  //           <th>值区间</th>
  //           <th>类型</th>
  //       </tr>
  //     </thead>
  //     <tbody></tbody>
  //   `;

  //   const pdfTbody = pdfTable.querySelector('tbody');

  //   for (const [varName, info] of Object.entries(variables)) {
  //     const pdfRow = document.createElement('tr');
  //     pdfRow.innerHTML = `
  //       <td>${varName}</td>
  //       <td>${info.interval || '未知'}</td>
  //       <td>${info.type || '未知'}</td>
  //     `;
  //     pdfTbody.appendChild(pdfRow);
  //   }

  //   pdfContractDiv.appendChild(pdfTable);
  //   pdfContainer.appendChild(pdfContractDiv);
  // }

  if (!document.getElementById('interval-analysis-container')) {
    console.log('区间分析容器不存在，跳过渲染');
    return;
  }
}

// 设置漏洞筛选器
function setupVulnerabilityFilter() {
  // 处理传统select元素 (向后兼容)
  const vulnerabilityFilter = document.getElementById('vulnerabilityFilter');
  if (vulnerabilityFilter) {
    vulnerabilityFilter.addEventListener('change', function () {
      filterVulnerabilities(this.value);
    });
  }

  // 处理新的dropdown组件
  const filterItems = document.querySelectorAll('.vulnerability-filter-dropdown .filter-item');
  if (filterItems.length > 0) {
    filterItems.forEach(item => {
      item.addEventListener('click', function (e) {
        e.preventDefault();

        // 获取筛选值
        const filterValue = this.getAttribute('data-value');

        // 更新当前显示的筛选值
        const currentFilterEl = document.getElementById('currentFilter');
        if (currentFilterEl) {
          currentFilterEl.textContent = this.textContent.trim();
        }

        // 更新active状态
        filterItems.forEach(el => el.classList.remove('active'));
        this.classList.add('active');

        // 应用筛选
        filterVulnerabilities(filterValue);
      });
    });

    // 设置初始按钮样式
    updateFilterButtonStyle('all');
  }
}

// 增强的漏洞筛选功能
function filterVulnerabilities(filterValueParam) {
  console.log('触发筛选功能');

  // 确定筛选值
  let filterValue = filterValueParam;

  // 如果没有传入参数，尝试从下拉框获取
  if (!filterValue) {
    // 首先尝试从传统的select获取
    const selectEl = document.getElementById('vulnerabilityFilter');
    if (selectEl) {
      filterValue = selectEl.value;
    } else {
      // 然后尝试从新的dropdown获取
      const activeFilterItem = document.querySelector('.vulnerability-filter-dropdown .filter-item.active');
      if (activeFilterItem) {
        filterValue = activeFilterItem.getAttribute('data-value');
      } else {
        // 默认显示全部
        filterValue = 'all';
      }
    }
  }

  console.log('当前筛选值:', filterValue);

  // 更新筛选按钮样式
  updateFilterButtonStyle(filterValue);

  // 获取所有漏洞项
  const vulnerabilityItems = document.querySelectorAll('.vulnerability-item');
  console.log('找到漏洞项数量:', vulnerabilityItems.length);

  if (vulnerabilityItems.length === 0) {
    console.log('没有找到漏洞项，可能是尚未加载报告');
    return;
  }

  let visibleCount = 0;

  // 遍历并应用筛选
  vulnerabilityItems.forEach((item, index) => {
    const impact = item.getAttribute('data-impact');

    // 判断是否显示该项
    const shouldShow = filterValue === 'all' || impact === filterValue;

    // 根据条件设置显示状态
    item.style.display = shouldShow ? 'block' : 'none';

    if (shouldShow) {
      visibleCount++;
    }
  });

  console.log('可见漏洞数量:', visibleCount);

  // 如果没有可见的漏洞项，显示"无漏洞"提示
  const noVulnDiv = document.getElementById('noVulnerabilities');
  if (noVulnDiv) {
    if (visibleCount > 0) {
      noVulnDiv.style.display = 'none';
    } else {
      noVulnDiv.style.display = 'block';
      const textEl = noVulnDiv.querySelector('p.text-lg');
      if (textEl) {
        textEl.textContent = `未找到${getFilterNameById(filterValue)}漏洞`;
      }
    }
  }
}

// 更新筛选按钮样式
function updateFilterButtonStyle(filterValue) {
  const filterBtn = document.querySelector('.filter-btn');
  if (!filterBtn) return;

  // 移除所有已有的筛选器样式类
  filterBtn.classList.remove('filter-high', 'filter-medium', 'filter-low', 'filter-informational');

  // 根据筛选值设置不同的样式
  if (filterValue !== 'all') {
    filterBtn.classList.add(`filter-${filterValue}`);

    // 更新图标
    const icon = filterBtn.querySelector('.filter-icon i');
    if (icon) {
      // 移除旧的图标类
      icon.className = '';

      // 根据筛选值设置不同的图标
      switch (filterValue) {
        case 'high':
          icon.className = 'fas fa-skull-crossbones';
          break;
        case 'medium':
          icon.className = 'fas fa-exclamation-triangle';
          break;
        case 'low':
          icon.className = 'fas fa-exclamation-circle';
          break;
        case 'informational':
          icon.className = 'fas fa-info-circle';
          break;
        default:
          icon.className = 'fas fa-filter';
      }
    }
  } else {
    // 恢复默认图标
    const icon = filterBtn.querySelector('.filter-icon i');
    if (icon) {
      icon.className = 'fas fa-filter';
    }
  }
}

// 下载报告
function downloadReport(format = 'json') {
  if (!reportData) {
    alert('没有可下载的报告数据');
    return;
  }

  const currentDate = new Date().toISOString().split('T')[0];
  const fileName = `slither-report-${currentDate}`;

  switch (format) {
    case 'json':
      // JSON格式导出
      const jsonBlob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
      downloadBlob(jsonBlob, `${fileName}.json`);
      break;

    case 'markdown':
      // Markdown格式导出
      const markdownContent = generateMarkdownReport(reportData);
      const mdBlob = new Blob([markdownContent], { type: 'text/markdown' });
      downloadBlob(mdBlob, `${fileName}.md`);
      break;

    case 'pdf':
      // PDF格式导出 - 使用第三方库如html2pdf.js
      generatePdfReport();
      break;

    default:
      alert('不支持的导出格式');
  }
}

// 辅助函数：下载Blob
function downloadBlob(blob, fileName) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  link.click();

  // 清理URL
  setTimeout(() => URL.revokeObjectURL(url), 100);
}

// 生成Markdown格式报告 - 优化版
function generateMarkdownReport(data) {
  // 获取当前日期和时间，格式化为更友好的显示方式
  const currentDate = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  // 提取漏洞统计数据
  const vulnCounts = {
    high: 0,
    medium: 0,
    low: 0,
    informational: 0
  };

  // 从不同可能的数据路径获取漏洞信息
  const detectors = data.results?.detectors || data.detectors || (Array.isArray(data) ? data : []);

  // 计算各严重级别漏洞数量
  detectors.forEach(detector => {
    const impact = (detector.impact || 'informational').toLowerCase();
    if (vulnCounts[impact] !== undefined) {
      vulnCounts[impact]++;
    }
  });

  // 构建 Markdown 报告头部
  let markdown = `# Slither 智能合约安全审计报告\n\n`;
  markdown += `**生成日期**: ${currentDate}\n\n`;

  // 添加摘要信息，使用表格格式提高可读性
  markdown += `## 1. 摘要\n\n`;

  // 从报告数据中提取或计算文件和合约数量
  const fileSet = new Set();
  const contractSet = new Set();

  detectors.forEach(detector => {
    if (detector.elements) {
      detector.elements.forEach(element => {
        if (element.source_mapping?.filename_relative) {
          fileSet.add(element.source_mapping.filename_relative);
        }

        // 尝试提取合约名称
        if (element.type === 'contract') {
          if (element.name) contractSet.add(element.name);
        } else if (element.type_specific_fields?.parent?.type === 'contract') {
          if (element.type_specific_fields.parent.name) {
            contractSet.add(element.type_specific_fields.parent.name);
          }
        }
      });
    }
  });

  // Solidity 版本检测
  let solcVersion = '-';
  const solcDetector = detectors.find(d => d.check === 'solc-version');
  if (solcDetector?.elements?.[0]?.type_specific_fields?.directive) {
    solcVersion = solcDetector.elements[0].type_specific_fields.directive.join('');
  }

  // 概要信息表格
  markdown += `| 项目 | 数值 |\n`;
  markdown += `| --- | --- |\n`;
  markdown += `| 文件数量 | ${fileSet.size} |\n`;
  markdown += `| 合约数量 | ${contractSet.size} |\n`;
  markdown += `| Solidity版本 | ${solcVersion} |\n`;
  markdown += `| 总漏洞数量 | ${detectors.length} |\n\n`;

  // 添加漏洞统计信息，使用醒目的表格和图标
  markdown += `## 2. 漏洞统计\n\n`;
  markdown += `| 严重级别 | 数量 | 图示 |\n`;
  markdown += `| --- | :---: | --- |\n`;
  markdown += `| 🔴 高危 | ${vulnCounts.high} | ${'█'.repeat(Math.min(vulnCounts.high, 20))} |\n`;
  markdown += `| 🟠 中危 | ${vulnCounts.medium} | ${'█'.repeat(Math.min(vulnCounts.medium, 20))} |\n`;
  markdown += `| 🟡 低危 | ${vulnCounts.low} | ${'█'.repeat(Math.min(vulnCounts.low, 20))} |\n`;
  markdown += `| 🔵 提示 | ${vulnCounts.informational} | ${'█'.repeat(Math.min(vulnCounts.informational, 20))} |\n\n`;

  // 添加合约列表
  if (contractSet.size > 0) {
    markdown += `## 3. 被审计合约\n\n`;

    // 从文件信息和合约名称中构建合约表格
    const contracts = Array.from(contractSet).map(name => {
      // 查找与此合约关联的文件
      let filename = '';
      for (const detector of detectors) {
        for (const element of detector.elements || []) {
          if ((element.type === 'contract' && element.name === name) ||
            (element.type_specific_fields?.parent?.type === 'contract' &&
              element.type_specific_fields.parent.name === name)) {
            if (element.source_mapping?.filename_relative) {
              filename = element.source_mapping.filename_relative;
              break;
            }
          }
        }
        if (filename) break;
      }

      return { name, filename };
    });

    markdown += `| 合约名称 | 文件路径 |\n`;
    markdown += `| --- | --- |\n`;

    contracts.forEach(contract => {
      markdown += `| \`${contract.name}\` | ${contract.filename || '未知文件'} |\n`;
    });

    markdown += `\n`;
  }

  // 添加漏洞详情，分级别展示
  markdown += `## 4. 漏洞详情\n\n`;

  if (detectors.length === 0) {
    markdown += `未发现漏洞\n\n`;
  } else {
    // 按严重性级别分类漏洞
    const categorizedDetectors = {
      high: detectors.filter(d => (d.impact || '').toLowerCase() === 'high'),
      medium: detectors.filter(d => (d.impact || '').toLowerCase() === 'medium'),
      low: detectors.filter(d => (d.impact || '').toLowerCase() === 'low'),
      informational: detectors.filter(d => (d.impact || '').toLowerCase() === 'informational' || !d.impact)
    };

    // 严重性级别和对应的标题前缀
    const severityHeaders = {
      high: '🔴 高危漏洞',
      medium: '🟠 中危漏洞',
      low: '🟡 低危漏洞',
      informational: '🔵 提示信息'
    };

    // 遍历每个严重级别，生成对应的漏洞详情
    ['high', 'medium', 'low', 'informational'].forEach(severity => {
      const severityDetectors = categorizedDetectors[severity];

      if (severityDetectors.length > 0) {
        markdown += `### 4.${severity === 'high' ? '1' : severity === 'medium' ? '2' : severity === 'low' ? '3' : '4'} ${severityHeaders[severity]} (${severityDetectors.length})\n\n`;

        severityDetectors.forEach((detector, index) => {
          // 检查器名称作为小标题
          markdown += `#### ${index + 1}. ${detector.check || detector.id || '未知检查'}\n\n`;

          // 详细描述
          if (detector.description) {
            markdown += `**描述**: ${detector.description.replace(/\n/g, '\n> ')}\n\n`;
          }

          // 位置信息
          if (detector.elements && detector.elements.length > 0) {
            const element = detector.elements[0];
            if (element.source_mapping) {
              const filename = element.source_mapping.filename_relative || '未知文件';
              const lines = element.source_mapping.lines || [];
              if (lines.length > 0) {
                markdown += `**位置**: \`${filename}#L${lines.join('-L')}\`\n\n`;
              } else {
                markdown += `**位置**: \`${filename}\`\n\n`;
              }
            }

            // 提取代码片段
            let codeSnippet = '';
            if (element.type === 'node' && element.name) {
              codeSnippet = element.name;
            } else if (detector.description) {
              const codeMatches = detector.description.match(/`([^`]+)`/g);
              if (codeMatches && codeMatches.length > 0) {
                codeSnippet = codeMatches.map(match => match.replace(/`/g, '')).join('\n');
              }
            }

            if (codeSnippet) {
              markdown += `**代码片段**:\n\`\`\`solidity\n${codeSnippet}\n\`\`\`\n\n`;
            }
          }

          // 置信度和影响
          markdown += `**影响**: ${detector.impact || '未知'}, **置信度**: ${detector.confidence || '未知'}\n\n`;

          // 修复建议
          if (detector.markdown) {
            // 提取 markdown 中的链接并转换为纯文本建议
            let recommendation = detector.markdown;
            recommendation = recommendation.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
            markdown += `**修复建议**: ${recommendation}\n\n`;
          }

          // 分隔线
          markdown += `---\n\n`;
        });
      }
    });
  }

  // 添加落款
  markdown += `## 报告结尾\n\n`;
  markdown += `此报告由 Slither 静态分析工具生成，报告时间: ${currentDate}。\n`;
  markdown += `请注意审计工具可能存在误报，最终结果需要专业人员确认。\n`;

  return markdown;
}

// 更新PDF内容元素 - 优化视觉体验
function updatePdfContent() {
  try {
    if (!reportData) {
      console.warn('updatePdfContent: reportData is null, skipping.');
      return;
    }

    // 确保 PDF 内容区域存在
    const pdfContainingDiv = document.getElementById('reportContent');
    if (!pdfContainingDiv) {
      console.error('updatePdfContent: Cannot find PDF container element #reportContent.');
      return;
    }

    // 安全地从 UI 中获取统计数据
    const highCountEl = document.getElementById('highCount');
    const mediumCountEl = document.getElementById('mediumCount');
    const lowCountEl = document.getElementById('lowCount');
    const infoCountEl = document.getElementById('infoCount');

    const stats = {
      high: parseInt(highCountEl?.textContent || '0', 10),
      medium: parseInt(mediumCountEl?.textContent || '0', 10),
      low: parseInt(lowCountEl?.textContent || '0', 10),
      informational: parseInt(infoCountEl?.textContent || '0', 10)
    };

    const totalVulns = stats.high + stats.medium + stats.low + stats.informational;

    // 安全地提取或计算摘要信息
    const fileCountEl = document.getElementById('fileCount');
    const contractCountEl = document.getElementById('contractCount');
    const solcVersionEl = document.getElementById('solcVersion');
    const auditTimeEl = document.getElementById('auditTime');

    const summary = {
      auditTime: auditTimeEl?.textContent || new Date().toLocaleString('zh-CN'),
      fileCount: fileCountEl?.textContent || '0',
      contractCount: contractCountEl?.textContent || '0',
      solcVersion: solcVersionEl?.textContent || '-'
    };

    // 安全地获取处理后的漏洞详情
    const detectors = reportData.results?.detectors || reportData.detectors || (Array.isArray(reportData) ? reportData : []);

    // 确定当前主题
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const isDarkTheme = currentTheme === 'dark';

    // 构建 PDF 内容 HTML，根据当前主题调整样式
    let pdfHtml = `
      <style>
        /* PDF styles with theme awareness */
        .report-header {
          text-align: center;
          margin-bottom: 20px;
          padding-bottom: 10px;
          border-bottom: 2px solid ${isDarkTheme ? '#4b5563' : '#4a5568'};
        }
        .report-header h1 {
          font-size: 28px;
          color: ${isDarkTheme ? '#e2e8f0' : '#2d3748'};
          margin-bottom: 8px;
        }
        .report-date {
          color: ${isDarkTheme ? '#94a3b8' : '#718096'};
          font-size: 14px;
        }
        .report-section {
          margin-bottom: 20px;
          page-break-inside: avoid;
        }
        .report-section h2 {
          font-size: 22px;
          color: ${isDarkTheme ? '#e2e8f0' : '#2d3748'};
          border-bottom: 1px solid ${isDarkTheme ? '#4b5563' : '#e2e8f0'};
          padding-bottom: 5px;
          margin-bottom: 15px;
        }
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 15px;
        }
        .summary-item {
          background-color: ${isDarkTheme ? '#374151' : '#f7fafc'};
          border: 1px solid ${isDarkTheme ? '#4b5563' : '#e2e8f0'};
          border-radius: 6px;
          padding: 10px;
        }
        .summary-label {
          font-size: 14px;
          color: ${isDarkTheme ? '#94a3b8' : '#718096'};
          margin-bottom: 5px;
        }
        .summary-value {
          font-size: 18px;
          font-weight: bold;
          color: ${isDarkTheme ? '#e2e8f0' : '#2d3748'};
        }
        .vulnerability-summary {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-top: 15px;
        }
        .vuln-summary-chart {
          position: relative;
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: conic-gradient(
            ${isDarkTheme ? '#f87171' : '#f56565'} 0% ${stats.high * 360 / (totalVulns || 100)}deg,
            ${isDarkTheme ? '#fb923c' : '#ed8936'} ${stats.high * 360 / (totalVulns || 100)}deg ${(stats.high + stats.medium) * 360 / (totalVulns || 100)}deg,
            ${isDarkTheme ? '#facc15' : '#ecc94b'} ${(stats.high + stats.medium) * 360 / (totalVulns || 100)}deg ${(stats.high + stats.medium + stats.low) * 360 / (totalVulns || 100)}deg,
            ${isDarkTheme ? '#60a5fa' : '#4299e1'} ${(stats.high + stats.medium + stats.low) * 360 / (totalVulns || 100)}deg 360deg
          );
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .vuln-chart-center {
          width: 60px;
          height: 60px;
          background: ${isDarkTheme ? '#1f2937' : 'white'};
          border-radius: 50%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }
        .vuln-total {
          font-size: 18px;
          font-weight: bold;
          color: ${isDarkTheme ? '#e2e8f0' : '#2d3748'};
        }
        .vuln-total-label {
          font-size: 10px;
          color: ${isDarkTheme ? '#94a3b8' : '#718096'};
        }
        .vulnerability-stats {
          flex: 1;
        }
        .vuln-stat-row {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
          gap: 8px;
        }
        .vuln-stat-row.empty .vuln-stat-bar-inner {
          background-color: ${isDarkTheme ? '#4b5563' : '#edf2f7'};
        }
        .vuln-stat-icon {
          margin-right: 6px;
          font-size: 14px;
        }
        .vuln-stat-label {
          font-weight: 500;
          font-size: 12px;
          flex: 1;
          color: ${isDarkTheme ? '#e2e8f0' : 'inherit'};
        }
        .vuln-stat-count {
          font-weight: bold;
          font-size: 14px;
          margin: 0 12px;
          min-width: 24px;
          text-align: right;
          color: ${isDarkTheme ? '#e2e8f0' : 'inherit'};
        }
        .vuln-stat-bar {
          flex: 3;
          height: 10px;
          background: ${isDarkTheme ? '#374151' : '#e5e7eb'};
          border-radius: 5px;
          overflow: hidden;
        }
        .vuln-stat-bar-inner {
          height: 100%;
          border-radius: 5px;
        }
        .high .vuln-stat-bar-inner { background-color: ${isDarkTheme ? '#f87171' : '#ef4444'}; }
        .medium .vuln-stat-bar-inner { background-color: ${isDarkTheme ? '#fb923c' : '#f97316'}; }
        .low .vuln-stat-bar-inner { background-color: ${isDarkTheme ? '#facc15' : '#eab308'}; }
        .info .vuln-stat-bar-inner { background-color: ${isDarkTheme ? '#60a5fa' : '#3b82f6'}; }
        
        .contracts-table {
          width: 100%;
          margin: 16px 0;
          border-collapse: collapse;
        }
        .contracts-table th, .contracts-table td {
          border: 1px solid ${isDarkTheme ? '#4b5563' : '#e2e8f0'};
          padding: 8px;
          text-align: left;
          color: ${isDarkTheme ? '#e2e8f0' : 'inherit'};
        }
        .contracts-table th {
          background-color: ${isDarkTheme ? '#374151' : '#f8fafc'};
          font-weight: 600;
        }
        
        /* 整体页面背景和文本颜色 */
        body {
          background-color: ${isDarkTheme ? '#111827' : 'white'};
          color: ${isDarkTheme ? '#e2e8f0' : '#1f2937'};
        }
        
        /* 打印样式（保持不变，因为打印始终使用浅色主题） */
        @page {
          size: A4;
          margin: 1.5cm;
        }
      </style>
    
      <div class="report-header">
        <h1>Slither 智能合约安全审计报告</h1>
        <p class="report-date">生成日期: ${summary.auditTime}</p>
      </div>

      <div class="report-section">
        <h2>1. 审计摘要</h2>
        <div class="summary-grid">
          <div class="summary-item">
            <div class="summary-label">审计时间</div>
            <div class="summary-value">${summary.auditTime}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Solidity 版本</div>
            <div class="summary-value">${summary.solcVersion}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">文件数量</div>
            <div class="summary-value">${summary.fileCount}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">合约数量</div>
            <div class="summary-value">${summary.contractCount}</div>
          </div>
        </div>
      </div>

      <div class="report-section">
        <h2>2. 漏洞统计</h2>
        <div class="vulnerability-summary">
          <div class="vuln-summary-chart">
            <div class="vuln-chart-center">
              <div class="vuln-total">${totalVulns}</div>
              <div class="vuln-total-label">总计</div>
            </div>
          </div>
          <div class="vulnerability-stats">
            <div class="vuln-stat-row high ${stats.high === 0 ? 'empty' : ''}">
              <div class="vuln-stat-icon">🔴</div>
              <div class="vuln-stat-label">高危漏洞</div>
              <div class="vuln-stat-count">${stats.high}</div>
              <div class="vuln-stat-bar">
                <div class="vuln-stat-bar-inner" style="width: ${Math.min(stats.high * 100 / (totalVulns || 1), 100)}%"></div>
              </div>
            </div>
            <div class="vuln-stat-row medium ${stats.medium === 0 ? 'empty' : ''}">
              <div class="vuln-stat-icon">🟠</div>
              <div class="vuln-stat-label">中危漏洞</div>
              <div class="vuln-stat-count">${stats.medium}</div>
              <div class="vuln-stat-bar">
                <div class="vuln-stat-bar-inner" style="width: ${Math.min(stats.medium * 100 / (totalVulns || 1), 100)}%"></div>
              </div>
            </div>
            <div class="vuln-stat-row low ${stats.low === 0 ? 'empty' : ''}">
              <div class="vuln-stat-icon">🟡</div>
              <div class="vuln-stat-label">低危漏洞</div>
              <div class="vuln-stat-count">${stats.low}</div>
              <div class="vuln-stat-bar">
                <div class="vuln-stat-bar-inner" style="width: ${Math.min(stats.low * 100 / (totalVulns || 1), 100)}%"></div>
              </div>
            </div>
            <div class="vuln-stat-row info ${stats.informational === 0 ? 'empty' : ''}">
              <div class="vuln-stat-icon">🔵</div>
              <div class="vuln-stat-label">提示信息</div>
              <div class="vuln-stat-count">${stats.informational}</div>
              <div class="vuln-stat-bar">
                <div class="vuln-stat-bar-inner" style="width: ${Math.min(stats.informational * 100 / (totalVulns || 1), 100)}%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // 添加被审计合约部分
    const contractsList = document.getElementById('contractsList');
    const contractElements = contractsList ? contractsList.querySelectorAll('tr') : []; // 安全访问

    if (contractElements.length > 0) {
      pdfHtml += `
        <div class="report-section">
          <h2>3. 被审计合约</h2>
          <table class="contracts-table">
            <thead>
              <tr>
                <th>合约名称</th>
                <th>所在文件</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
      `;

      contractElements.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length === 3) {
          // 再次检查cells内容，避免空值
          const name = cells[0]?.textContent || '';
          const file = cells[1]?.textContent || '';
          const status = cells[2]?.textContent?.trim() || '';
          pdfHtml += `
            <tr>
              <td>${name}</td>
              <td>${file}</td>
              <td>${status}</td>
            </tr>
          `;
        }
      });

      pdfHtml += `
            </tbody>
          </table>
        </div>
      `;
    }

    // 添加漏洞详情部分
    if (detectors && detectors.length > 0) {
      pdfHtml += `
        <div class="report-section">
          <h2>4. 漏洞详情</h2>
      `;

      // 按严重性分类排序
      const sortedBySeverity = [...detectors].sort((a, b) => {
        const severityOrder = { High: 0, Medium: 1, Low: 2, Informational: 3 };
        // 使用空值合并确保 impact 存在
        const impactA = a?.impact || 'Informational';
        const impactB = b?.impact || 'Informational';
        const severityA = severityOrder[impactA] ?? 4; // 使用 ?? 处理 undefined
        const severityB = severityOrder[impactB] ?? 4; // 使用 ?? 处理 undefined
        return severityA - severityB;
      });

      // 对于每个严重性级别，添加相应的漏洞
      for (const severity of ['High', 'Medium', 'Low', 'Informational']) {
        const severityVulns = sortedBySeverity.filter(v =>
          (v?.impact || 'Informational').toLowerCase() === severity.toLowerCase());

        if (severityVulns.length > 0) {
          const severityClass = severity.toLowerCase();
          const severityIcon = severity === 'High' ? '🔴' :
            severity === 'Medium' ? '🟠' :
              severity === 'Low' ? '🟡' : '🔵';
          const severityText = getSeverityDescription(severity);

          pdfHtml += `
            <div class="vulnerability-group ${severityClass}">
              <h3>${severityIcon} ${severityText}漏洞 (${severityVulns.length})</h3>
              <div class="vulnerabilities-section">
          `;

          severityVulns.forEach((vuln, index) => {
            // 检查 vuln 是否存在及其属性
            const description = vuln?.description || '没有提供描述';
            const checkName = vuln?.check || '未知检查项';
            const confidence = vuln?.confidence || '未知';

            // 尝试确定位置
            let location = '';
            if (vuln?.elements && vuln.elements.length > 0) {
              const firstElement = vuln.elements[0];
              if (firstElement?.source_mapping) {
                const sm = firstElement.source_mapping;
                const filename = sm.filename_relative || sm.filename_short || '未知文件';
                const lines = sm.lines && sm.lines.length > 0 ?
                  `#L${sm.lines.join('-L')}` : '';
                location = `${filename}${lines}`;
              }
            }

            // 提取代码片段
            let codeSnippet = '';
            if (vuln?.elements && vuln.elements.length > 0) {
              const nodeElement = vuln.elements.find(el => el?.type === 'node');
              if (nodeElement?.name) {
                codeSnippet = nodeElement.name;
              } else if (vuln.description) {
                const codeMatches = vuln.description.match(/`([^`]+)`/g);
                if (codeMatches && codeMatches.length > 0) {
                  codeSnippet = codeMatches.map(match => match.replace(/`/g, '')).join('\n');
                }
              }
            }

            // 安全地处理 markdown
            const recommendation = vuln?.markdown ? vuln.markdown.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') : '';

            pdfHtml += `
              <div class="vulnerability-item">
                <div class="vulnerability-header">
                  <span class="vuln-severity-badge ${severityClass}">${severity}</span>
                  <span class="vuln-title">${checkName}</span>
                  <span class="vuln-confidence">${confidence}可信度</span>
                </div>
                <div class="vulnerability-body">
                  ${location ? `<div class="vuln-location">${location}</div>` : ''}
                  <div class="vuln-description">${description.replace(/\n/g, '<br>')}</div>
                  ${codeSnippet ? `
                  <div class="vuln-code">
                    <div class="vuln-code-header">相关代码:</div>
                    <pre class="code-block">${escapeHtml(codeSnippet)}</pre> 
                  </div>
                  ` : ''}
                  ${recommendation ? `
                  <div class="vuln-recommendation">
                    <div class="vuln-recommendation-header">修复建议:</div>
                    <div class="vuln-recommendation-content">${escapeHtml(recommendation)}</div>
                  </div>
                  ` : ''}
                </div>
              </div>
            `;
          });

          pdfHtml += `
              </div>
            </div>
          `;
        }
      }

      pdfHtml += `</div>`;
    } else {
      pdfHtml += `
        <div class="report-section">
          <h2>4. 漏洞详情</h2>
          <div class="no-vulnerabilities">未发现漏洞</div>
        </div>
      `;
    }

    pdfHtml += `
      <div class="report-footer">
        <p>此报告由 Slither 智能合约审计工具生成</p>
        <p class="timestamp">生成时间: ${new Date().toLocaleString('zh-CN')}</p>
      </div>
    `;

    // 设置 PDF 内容
    pdfContainingDiv.innerHTML = pdfHtml;
    console.log('updatePdfContent: PDF content updated successfully.');
  } catch (error) {
    console.error('更新PDF内容时发生严重错误:', error);
  }
}

// 生成PDF报告 - 优化版
function generatePdfReport() {
  try {
    // 确保PDF数据已更新
    updatePdfContent();

    // 创建一个新的打印友好HTML页面用于PDF转换
    const printWindow = window.open('', '_blank');

    if (!printWindow) {
      alert('请允许弹出窗口以生成PDF报告');
      return;
    }

    // 获取要打印的内容
    const reportContent = document.getElementById('reportContent');

    if (!reportContent) {
      throw new Error('未找到报告内容元素');
    }

    // 创建打印友好内容，使用优化的 CSS
    const content = `
      <!DOCTYPE html>
      <html lang="zh-CN">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Slither安全审计报告</title>
        <style>
            /* 打印友好的 CSS 样式，优化资源占用 */
          body { 
              font-family: 'Segoe UI', Arial, sans-serif; 
            padding: 20px;
            color: #333;
              font-size: 12px;
              line-height: 1.5;
              max-width: 210mm;
              margin: 0 auto;
              background-color: white;
          }
            
          @media print {
              body { padding: 0; margin: 0; max-width: none; }
            .no-print { display: none; }
          .page-break { page-break-after: always; }
              @page { size: A4; margin: 1.5cm; }
            }
            
            /* 为静态复制版本添加打印按钮 */
            .print-controls {
              position: fixed;
              top: 20px;
              right: 20px;
              display: flex;
              gap: 10px;
              z-index: 9999;
            }
            
            .print-button {
              padding: 8px 16px;
              background-color: #1a56db;
            color: white;
            border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
              display: flex;
              align-items: center;
              gap: 6px;
            }
            
            .close-button {
            padding: 8px 16px;
              background-color: #ef4444;
              color: white;
              border: none;
            border-radius: 4px;
            cursor: pointer;
              font-weight: 500;
              display: flex;
              align-items: center;
              gap: 6px;
          }
        </style>
      </head>
      <body>
          <div class="print-controls no-print">
            <button class="print-button" onclick="window.print()">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 6 2 18 2 18 9"></polyline>
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                <rect x="6" y="14" width="12" height="8"></rect>
              </svg>
              打印PDF
            </button>
            <button class="close-button" onclick="window.close()">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              关闭
            </button>
        </div>
          ${reportContent.innerHTML}
          
          <div class="report-footer">
            <p>此报告由 Slither 智能合约审计工具生成</p>
            <p class="timestamp">生成时间：${new Date().toLocaleString('zh-CN')}</p>
        </div>
        
          <script>
            // 自动聚焦到打印对话框 (部分浏览器支持)
            window.onload = function() {
              setTimeout(function() {
                try {
                  document.querySelectorAll('img').forEach(img => {
                    // 确保图像已加载
                    if (!img.complete) {
                      img.onload = function() {
                        this.dataset.loaded = true;
                      };
                    } else {
                      img.dataset.loaded = true;
                    }
                  });
                } catch (e) {
                  console.error('图像加载检查失败:', e);
                }
              }, 1000);
            };
          </script>
      </body>
    </html>
  `;

    // 写入HTML内容
    printWindow.document.open();
    printWindow.document.write(content);
    printWindow.document.close();
  } catch (error) {
    console.error('生成PDF报告失败:', error);
    alert('生成PDF报告失败: ' + error.message);
  }
}

// 获取严重性首字母
function getSeverityInitial(severity) {
  switch (severity) {
    case 'high':
      return 'H';
    case 'medium':
      return 'M';
    case 'low':
      return 'L';
    case 'informational':
      return 'I';
    default:
      return '?';
  }
}

// 获取严重性描述
function getSeverityDescription(severity) {
  severity = severity.toLowerCase();
  if (severity === 'high' || severity === 'critical') return '高危';
  if (severity === 'medium') return '中危';
  if (severity === 'low') return '低危';
  return '提示'; // informational
}

// 清空当前报告并恢复初始状态
function clearCurrentReport() {
  // 清空全局报告数据
  reportData = null;

  // 清空显示
  clearReportDisplay();

  // 显示拖放区域
  const dropArea = document.getElementById('dropArea');
  if (dropArea) {
    dropArea.classList.remove('hidden');
  }

  console.log('已清空当前报告');
}

// 获取筛选名称
function getFilterNameById(filterId) {
  switch (filterId) {
    case 'high': return '高危';
    case 'medium': return '中危';
    case 'low': return '低危';
    case 'informational': return '提示级别';
    default: return '';
  }
}
