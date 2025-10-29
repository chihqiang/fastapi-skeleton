# ===========================
# 初始化虚拟环境及依赖
# ===========================
init:
	@echo "🚀 开始初始化项目环境..."
	# 检查并创建虚拟环境（若不存在）
	@if [ ! -d "venv" ]; then echo "🔧 虚拟环境不存在，正在创建..."; python3 -m venv venv; fi
	# 激活虚拟环境并安装依赖
	@echo "⚡ 安装/升级依赖包..."
	@bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
	@echo "✅ 环境初始化完成！"
	@echo "👉 激活虚拟环境：source venv/bin/activate"

# ===========================
# 代码检查与自动修复
# ===========================
check:
	@echo "检查并运行 ruff 修复代码..."
	@command -v ruff >/dev/null 2>&1 || { pip install ruff; }
	@ruff check --fix .
	@echo "检查并运行 black 格式化代码..."
	@command -v black >/dev/null 2>&1 || { pip install black; }
	@black .
	@echo "检查并运行 isort 排序导入..."
	@command -v isort >/dev/null 2>&1 || {  pip install black; }
	@isort .


# ===========================
# 清理项目缓存文件
# ===========================
clean:
	@echo "🧹 清理 __pycache__ 与 Python 临时文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +  # 递归删除所有 __pycache__ 目录
	@find . -type f -name "*.pyc" -delete                 # 删除所有 .pyc 编译文件
	@find . -type f -name "*.pyo" -delete                 # 删除所有 .pyo 优化编译文件

# ===========================
# 执行数据库迁移脚本
# ===========================
migrate:
	@echo "📦 执行数据库迁移..."
	# 激活虚拟环境并运行迁移脚本
	@bash -c "source venv/bin/activate && python tools/migrate.py"
	@echo "✅ 迁移完成"