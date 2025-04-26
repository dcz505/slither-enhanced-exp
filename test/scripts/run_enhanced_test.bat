@echo off
REM Slither 增强版测试运行脚本
REM 此脚本简化了使用 slither_test_runner.py 进行测试的过程

setlocal enabledelayedexpansion

echo ==================================================================
echo                Slither 增强版 - 测试运行脚本
echo ==================================================================

REM 当前脚本目录
set SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

REM 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未检测到Python。请确保Python已安装并添加到PATH中。
    exit /b 1
)

REM 检查必要的包
echo 检查必要的包...
python -c "import pandas, numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 缺少必要的包。正在安装...
    python -m pip install pandas numpy matplotlib seaborn
)

REM 参数设置
set MAX_FILES=3
set OUTPUT_DIR=..\results
set TEST_SETS=baseline,smartbugs
set VERBOSE=--verbose

REM 处理命令行参数
:param_loop
if "%~1"=="" goto param_done
if /i "%~1"=="--max-files" (
    set MAX_FILES=%~2
    shift
    shift
    goto param_loop
)
if /i "%~1"=="--output-dir" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto param_loop
)
if /i "%~1"=="--test-sets" (
    set TEST_SETS=%~2
    shift
    shift
    goto param_loop
)
if /i "%~1"=="--verbose" (
    set VERBOSE=--verbose
    shift
    goto param_loop
)
if /i "%~1"=="--help" (
    echo 用法: run_enhanced_test.bat [选项]
    echo 选项:
    echo   --max-files N     每个测试集最多测试的文件数，默认为5
    echo   --output-dir DIR  结果输出目录，默认为..\results
    echo   --test-sets SETS  要测试的测试集，逗号分隔，默认为baseline,smartbugs
    echo   --verbose         显示详细输出
    echo   --help            显示此帮助信息
    exit /b 0
)
shift
goto param_loop
:param_done

echo [信息] 将测试以下测试集: %TEST_SETS%
echo [信息] 每个测试集最多测试 %MAX_FILES% 个文件
echo [信息] 结果将保存到: %OUTPUT_DIR%

REM 运行测试
echo.
echo ==================================================================
echo                      开始运行测试
echo ==================================================================
echo.

python slither_test_runner.py --max-files %MAX_FILES% --output-dir %OUTPUT_DIR% --test-sets %TEST_SETS% %VERBOSE%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 测试运行失败，错误代码: %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo ==================================================================
echo                      测试完成
echo ==================================================================
echo.
echo 测试结果已保存到 %OUTPUT_DIR% 目录

exit /b 0 