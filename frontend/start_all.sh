#!/bin/bash

echo "🚀 Запуск TradeShield - Полная система"
echo "========================================"

# Функция для завершения всех фоновых процессов
cleanup() {
    echo "🛑 Остановка серверов..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Обработчик сигналов для корректного завершения
trap cleanup SIGINT SIGTERM

echo "📦 Запуск Backend API (порт 5000)..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

echo "🌐 Запуск Frontend сервера (порт 8080)..."
cd TradeShield
python3 -m http.server 8080 &
FRONTEND_PID=$!
cd ..

echo "⏳ Ожидание запуска серверов..."
sleep 3

echo "✅ Серверы запущены!"
echo ""
echo "🔗 Ссылки:"
echo "  Frontend: http://localhost:8080"
echo "  Backend API: http://localhost:5000"
echo ""
echo "📋 Инструкции:"
echo "  1. Откройте http://localhost:8080 в браузере"
echo "  2. Введите ИНН (минимум 10 цифр)"
echo "  3. Введите код товара (начните с 123, 234 или 345)"
echo "  4. Нажмите Enter для принятия предложения"
echo "  5. Выберите наименование товара"
echo "  6. Нажмите 'Анализ'"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"

# Ждем завершения
wait
