#!/bin/bash

echo "🔹 حذف ملفات migration ماعدا __init__.py ..."
find . -path "*/migrations/*.py" ! -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "🔹 حذف مجلدات __pycache__ ..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "✅ الانتهاء من تنظيف المجلدات"
