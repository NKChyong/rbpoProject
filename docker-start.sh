#!/bin/bash

echo "🐳 Reading List API - Docker Setup"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker Desktop."
    exit 1
fi

echo "✅ Docker установлен: $(docker --version)"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker не запущен. Запустите Docker Desktop."
    exit 1
fi

echo "✅ Docker запущен"
echo ""

# Check ports
echo "Проверка портов..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Порт 3000 занят (нужен для фронтенда)"
fi

if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Порт 5432 занят (нужен для PostgreSQL)"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Порт 8000 занят (нужен для API)"
fi

echo ""
echo "🚀 Запуск проекта..."
echo ""

# Start Docker Compose
docker-compose up --build

echo ""
echo "✅ Проект запущен!"
echo ""
echo "Доступные сервисы:"
echo "  🌐 Фронтенд:  http://localhost:3000"
echo "  🔌 API:       http://localhost:8000"
echo "  📖 Swagger:   http://localhost:8000/api/docs"
echo ""
echo "Для остановки: Ctrl+C, затем 'docker-compose down'"
