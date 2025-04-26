#!/bin/bash
# Slither 增强版测试运行脚本
# 此脚本简化了使用 slither_test_runner.py 进行测试的过程

# 显示彩色输出
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_header() {
  echo -e "\n${BLUE}=================================================================="
  echo -e "${BLUE} $1${NC}"
  echo -e "${BLUE}==================================================================\n${NC}"
}

print_info() {
  echo -e "${BLUE}[信息] $1${NC}"
}

print_success() {
  echo -e "${GREEN}[成功] $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}[警告] $1${NC}"
}

print_error() {
  echo -e "${RED}[错误] $1${NC}"
}

# 显示帮助信息
show_help() {
  echo "用法: ./run_enhanced_test.sh [选项]"
  echo "选项:"
  echo "  --max-files N     每个测试集最多测试的文件数，默认为5"
  echo "  --output-dir DIR  结果输出目录，默认为../results"
  echo "  --test-sets SETS  要测试的测试集，逗号分隔，默认为baseline,smartbugs"
  echo "  --verbose         显示详细输出"
  echo "  --help            显示此帮助信息"
}

# 当前脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
  print_error "未检测到Python。请确保Python已安装。"
  exit 1
fi

# 参数设置
MAX_FILES=5
OUTPUT_DIR="../results"
TEST_SETS="baseline,smartbugs"
VERBOSE=""

# 处理命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --max-files)
      MAX_FILES="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --test-sets)
      TEST_SETS="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE="--verbose"
      shift
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      print_error "未知参数: $1"
      show_help
      exit 1
      ;;
  esac
done

print_header "Slither 增强版 - 测试运行脚本"

# 检查必要的包
print_info "检查必要的包..."
if ! python3 -c "import pandas, numpy" &> /dev/null; then
  print_warning "缺少必要的包。正在安装..."
  pip3 install pandas numpy matplotlib seaborn
fi

print_info "将测试以下测试集: $TEST_SETS"
print_info "每个测试集最多测试 $MAX_FILES 个文件"
print_info "结果将保存到: $OUTPUT_DIR"

# 运行测试
print_header "开始运行测试"

python3 slither_test_runner.py --max-files "$MAX_FILES" --output-dir "$OUTPUT_DIR" --test-sets "$TEST_SETS" $VERBOSE

if [ $? -ne 0 ]; then
  echo
  print_error "测试运行失败"
  exit 1
fi

print_header "测试完成"
print_success "测试结果已保存到 $OUTPUT_DIR 目录"

exit 0 