#!/bin/bash

# Slither增强版测试实验执行脚本
# 本脚本清理冗余脚本，然后执行测试实验

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}    Slither增强版测试实验 - 开始执行                     ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_DIR="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$TEST_DIR/results"

# 确保结果目录存在
mkdir -p "$RESULTS_DIR"

# 检查依赖
echo -e "${BLUE}[1/5] 检查环境依赖...${NC}"

# 检查Python
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}✓ Python3已安装${NC}"
    python3 --version
else
    echo -e "${RED}✗ 未找到Python3! 请安装Python 3.8+${NC}"
    exit 1
fi

# 检查必要的Python包
for package in pandas numpy matplotlib seaborn; do
    if python3 -c "import $package" &>/dev/null; then
        echo -e "${GREEN}✓ $package已安装${NC}"
    else
        echo -e "${YELLOW}! $package未安装，尝试安装...${NC}"
        pip install $package
    fi
done

# 检查Slither
if command -v slither &>/dev/null; then
    echo -e "${GREEN}✓ Slither已安装${NC}"
    slither --version
else
    echo -e "${RED}✗ 未找到Slither! 请先安装Slither${NC}"
    exit 1
fi

# 检查配置和目录
echo -e "${BLUE}[2/5] 检查测试配置和目录...${NC}"

if [ -f "$TEST_DIR/configs/test_configs.json" ]; then
    echo -e "${GREEN}✓ 测试配置文件存在${NC}"
else
    echo -e "${RED}✗ 测试配置文件不存在: $TEST_DIR/configs/test_configs.json${NC}"
    exit 1
fi

# 检查测试合约目录
if [ -d "$TEST_DIR/TestContracts/Baseline" ]; then
    echo -e "${GREEN}✓ 基准测试合约目录存在${NC}"
    # 计算合约数量
    CONTRACT_COUNT=$(find "$TEST_DIR/TestContracts/Baseline" -name "*.sol" | wc -l)
    echo -e "${GREEN}  - 找到 $CONTRACT_COUNT 个基准测试合约${NC}"
else
    echo -e "${YELLOW}! 基准测试合约目录不存在，测试可能无法正常进行${NC}"
fi

# 执行测试
echo -e "${BLUE}[3/5] 执行综合测试...${NC}"
python3 "$SCRIPT_DIR/slither_test_runner.py" --output-dir "$RESULTS_DIR" --max-files 10

# 检查结果
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 测试执行失败${NC}"
    exit 1
else
    echo -e "${GREEN}✓ 测试执行完成${NC}"
fi

# 检查最新生成的结果目录
LATEST_RESULT_DIR=$(find "$RESULTS_DIR/evaluation_"* -type d -printf "%T@ %p\n" 2>/dev/null | sort -n | tail -1 | cut -f2- -d" ")

if [ -z "$LATEST_RESULT_DIR" ]; then
    echo -e "${RED}✗ 未找到测试结果目录${NC}"
    exit 1
fi

echo -e "${BLUE}[4/5] 结果目录: $LATEST_RESULT_DIR${NC}"

# 汇总结果
echo -e "${BLUE}[5/5] 生成测试结果摘要...${NC}"

# 检查评估报告
REPORT_FILE="$LATEST_RESULT_DIR/evaluation_report.md"
if [ -f "$REPORT_FILE" ]; then
    echo -e "${GREEN}✓ 评估报告生成成功${NC}"
    
    # 显示报告摘要
    echo -e "${YELLOW}==== 测试结果摘要 ====${NC}"
    echo ""
    # 提取总体性能部分
    sed -n '/总体性能提升/,/测试集性能表现/p' "$REPORT_FILE" | head -n -2
    echo ""
    echo -e "${YELLOW}==== 主要发现 ====${NC}"
    echo ""
    # 提取主要发现部分
    sed -n '/主要发现/,/结论/p' "$REPORT_FILE" | head -n -2
    echo ""
else
    echo -e "${RED}✗ 未找到评估报告: $REPORT_FILE${NC}"
fi

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}测试实验执行完成!${NC}"
echo -e "${BLUE}完整结果位于: $LATEST_RESULT_DIR${NC}"
echo -e "${BLUE}=========================================================${NC}" 