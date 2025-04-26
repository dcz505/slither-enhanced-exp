from setuptools import setup, find_packages

setup(
    name="slither_enhanced",
    version="0.1.0",
    description="Slither插件模块，包含区间分析模块和DeFi特定检测器模块和UI模块",
    author="dcz",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "slither-analyzer>=0.9.0",
        "numpy>=1.20.0",
        "matplotlib>=3.4.0"
    ],
    entry_points={
        "slither_analyzer.plugin": [
            "slither-enhanced=slither_enhanced:make_plugin",
        ],
        "console_scripts": [
            "interval-analyze=slither_enhanced.src.python_module.interval_analysis.cli:main",
            "interval-analyze-run=slither_enhanced.scripts.run_interval_analysis:main",
            "interval-example=slither_enhanced.scripts.interval_analysis_example:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
) 