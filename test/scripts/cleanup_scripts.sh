#!/bin/bash

# Slither增强版 - 脚本清理工具
# 该脚本用于清理冗余的测试脚本，只保留必要的脚本

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}    Slither增强版 - 脚本清理工具                         ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKUP_DIR="$SCRIPT_DIR/backup"

# 创建备份目录
echo -e "${BLUE}[1/3] 创建备份目录...${NC}"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✓ 备份目录创建成功: $BACKUP_DIR${NC}"

# 需要保留的关键脚本
echo -e "${BLUE}[2/3] 备份所有脚本...${NC}"
cp -r "$SCRIPT_DIR"/*.py "$BACKUP_DIR/"
cp -r "$SCRIPT_DIR"/*.sh "$BACKUP_DIR/"
echo -e "${GREEN}✓ 备份完成${NC}"

# 定义要保留的脚本
KEEP_FILES=(
    "slither_test_runner.py"      # 整合测试脚本
    "run_test_experiment.sh"      # 测试执行脚本
    "cleanup_scripts.sh"          # 当前脚本
    "verify_structure.py"         # 结构验证脚本
)

# 定义不应删除的目录
KEEP_DIRS=(
    "backup"                     # 备份目录
    "__pycache__"                # Python缓存目录
    "interval_analysis"          # 区间分析脚本目录
)

echo -e "${BLUE}[3/3] 清理冗余脚本...${NC}"

# 删除不需要的Python脚本
echo -e "${YELLOW}清理Python脚本...${NC}"
for file in "$SCRIPT_DIR"/*.py; do
    filename=$(basename "$file")
    keep=false
    
    for keep_file in "${KEEP_FILES[@]}"; do
        if [[ "$filename" == "$keep_file" ]]; then
            keep=true
            break
        fi
    done
    
    if [[ "$keep" == false ]]; then
        echo -e "${RED}- 删除: $filename${NC}"
        mv "$file" "$BACKUP_DIR/" 2>/dev/null || rm "$file"
    else
        echo -e "${GREEN}+ 保留: $filename${NC}"
    fi
done

# 删除不需要的Shell脚本
echo -e "${YELLOW}清理Shell脚本...${NC}"
for file in "$SCRIPT_DIR"/*.sh; do
    filename=$(basename "$file")
    keep=false
    
    for keep_file in "${KEEP_FILES[@]}"; do
        if [[ "$filename" == "$keep_file" ]]; then
            keep=true
            break
        fi
    done
    
    if [[ "$keep" == false && "$filename" != "cleanup_scripts.sh" ]]; then
        echo -e "${RED}- 删除: $filename${NC}"
        mv "$file" "$BACKUP_DIR/" 2>/dev/null || rm "$file"
    else
        echo -e "${GREEN}+ 保留: $filename${NC}"
    fi
done

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}脚本清理完成!${NC}"
echo -e "${BLUE}保留的脚本:${NC}"
for file in "${KEEP_FILES[@]}"; do
    echo -e "${GREEN}- $file${NC}"
done
echo -e "${BLUE}原始脚本已备份至: $BACKUP_DIR${NC}"
echo -e "${BLUE}=========================================================${NC}" 