# ============================================
# FastAPI + SQLAlchemy + Alembic 项目 Makefile
# ============================================

# -----------------------------
# Alembic 命令
# -----------------------------
# 使用 python -m alembic 调用 Alembic
ALEMBIC = python -m alembic

# ===========================
# 清理缓存文件
# ===========================
clean:
	@echo "🧹 清理 __pycache__ 与临时文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete

# ===========================
# 初始化虚拟环境
# ===========================
init:
	@echo "🚀 初始化虚拟环境并安装依赖..."
	# 如果 venv 文件夹不存在，则创建虚拟环境
	@if [ ! -d "venv" ]; then \
		echo "🔧 创建虚拟环境..."; \
		python3 -m venv venv; \
	fi
	@echo "⚡ 激活虚拟环境并升级 pip..."
	# 在同一个 shell 中激活虚拟环境，升级 pip 并安装 requirements.txt 依赖
	@bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
	@echo "✅ 虚拟环境初始化完成！"
	@echo "👉 之后使用虚拟环境，请执行: source venv/bin/activate"


migrate: 
	@bash -c "source venv/bin/activate && python tools/migrate.py"