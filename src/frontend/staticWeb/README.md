# Slither 增强版 - 静态网页报告查看器

这个静态网页报告查看器是 Slither 插件模块的一部分，用于可视化展示智能合约审计报告。它提供了一个用户友好的界面，使用户能够更轻松地理解和分析审计发现。

## 功能特点

- 提供漏洞统计、摘要信息、合约列表和详细的漏洞描述
- 交互式代码查看器，支持查看漏洞相关代码的上下文
- 支持报告筛选和导出（JSON、PDF）
- 拖放文件上传功能
- 本地存储上次查看的报告
- 支持明亮/暗黑主题切换

## 主要改进

1. **优化资源加载**：优化了纯cdn资源加载方式，从纯html+js+daisyUI Css转为加入node包管理资源加载

2. **修复默认报告加载问题**：优化了默认示例报告的加载逻辑，即使在网络请求失败的情况下也能回退到内置的示例数据。

3. **支持多种报告格式导出**：优化了报告导出格式类型，同时稍微处理了报告导出UI界面展示。

4. **改进漏洞显示**：升级了漏洞详情的展示方式，更加清晰地显示严重级别、影响和修复建议，同时优化了相关UI交互。

5. **优化代码结构**：重构了关键函数，提高了代码的可维护性和可扩展性。

6. **增强错误处理**：添加了更全面的错误处理逻辑，提高了应用的稳定性。

7. **移动端布局优化**：改进了在移动设备上的显示效果，包括：
   - 在小屏幕设备上隐藏"智能合约审计报告"标题，仅保留图标
   - 将导航按钮文本缩短为更紧凑的版本（如"历史记录"变为"历史"）
   - 调整按钮大小和间距，使布局在小屏幕上更加紧凑
   - 针对不同屏幕尺寸提供了额外的样式优化

8. **完整主题支持**：
   - 添加了明亮/暗黑主题切换功能，点击左上角盾牌图标切换
   - 使用localStorage保存用户主题偏好，下次访问时自动应用
   - 所有组件、图表和数据展示均支持主题切换
   - 导出的PDF报告会根据当前主题样式生成


## 注意事项

- 该工具是一个纯前端应用，所有数据处理都在浏览器中进行
- 报告数据仅存储在浏览器的本地存储中，不会上传到任何服务器
- 对于大型报告，可能需要较长的加载时间

## 使用方法

1. 打开index.html文件以启动应用
2. 使用"上传报告"按钮或拖放功能导入JSON格式的审计报告
3. 浏览漏洞统计、合约列表和详细的漏洞信息
4. 可以使用筛选功能按严重级别过滤漏洞
5. 点击左上角的盾牌图标可以切换明亮/暗黑主题
6. 使用导出功能将报告导出为其他格式

## 后续改进方向

- 增加CFG等涉及审计功能的交互
- 增加更多的数据可视化功能
- 支持批量报告比较
- 添加导出为不同格式的选项
- 进一步优化移动设备上的体验，包括触摸交互优化

