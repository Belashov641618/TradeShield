from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для фронтенда

# Заглушки данных
PRODUCT_CODES = {
    "123": "123456789",
    "1234": "123456789",
    "12345": "123456789",
    "123456": "123456789",
    "1234567": "123456789",
    "12345678": "123456789",
    "123456789": "123456789",
    "234": "234567890",
    "2345": "234567890",
    "23456": "234567890",
    "234567": "234567890",
    "2345678": "234567890",
    "23456789": "234567890",
    "234567890": "234567890",
    "345": "345678901",
    "3456": "345678901",
    "34567": "345678901",
    "345678": "345678901",
    "3456789": "345678901",
    "34567890": "345678901",
    "345678901": "345678901"
}

PRODUCT_NAMES = {
    "123456789": [
        {"name": "Электронные компоненты и устройства", "code": "123456789"},
        {"name": "Полупроводниковые приборы", "code": "123456789"},
        {"name": "Интегральные микросхемы", "code": "123456789"}
    ],
    "234567890": [
        {"name": "Машины и механическое оборудование", "code": "234567890"},
        {"name": "Двигатели и генераторы", "code": "234567890"},
        {"name": "Насосы и компрессоры", "code": "234567890"}
    ],
    "345678901": [
        {"name": "Химические продукты", "code": "345678901"},
        {"name": "Органические химические соединения", "code": "345678901"},
        {"name": "Фармацевтические продукты", "code": "345678901"}
    ]
}

# Хранилище задач анализа
analysis_jobs = {}

@app.route('/api/product-code/<query>', methods=['GET'])
def get_product_code(query):
    """GET запрос для получения предложения кода товара"""
    # Ищем точное совпадение или наиболее близкое
    if query in PRODUCT_CODES:
        return jsonify({
            "code": PRODUCT_CODES[query],
            "exists": True
        })
    
    # Ищем частичные совпадения
    suggestions = []
    for key, value in PRODUCT_CODES.items():
        if key.startswith(query):
            suggestions.append(value)
    
    if suggestions:
        return jsonify({
            "code": suggestions[0],  # Возвращаем первый найденный
            "exists": True
        })
    
    return jsonify({
        "code": None,
        "exists": False
    })

@app.route('/api/product-names/<product_code>', methods=['GET'])
def get_product_names(product_code):
    """GET запрос для получения наименований товара по коду"""
    if product_code in PRODUCT_NAMES:
        return jsonify({
            "names": PRODUCT_NAMES[product_code],
            "exists": True
        })
    
    return jsonify({
        "names": [],
        "exists": False
    })

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    """POST запрос для запуска анализа"""
    data = request.get_json()
    
    # Генерируем ID задачи
    job_id = f"job_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Сохраняем задачу
    analysis_jobs[job_id] = {
        "status": "processing",
        "inn": data.get('inn'),
        "productCode": data.get('productCode'),
        "productName": data.get('productName'),
        "created_at": time.time()
    }
    
    return jsonify({
        "job": job_id,
        "message": "Анализ запущен"
    })

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """GET запрос для проверки статуса задачи"""
    if job_id not in analysis_jobs:
        return jsonify({"error": "Задача не найдена"}), 404
    
    job = analysis_jobs[job_id]
    elapsed_time = time.time() - job["created_at"]
    
    # Имитируем процесс анализа
    if elapsed_time < 5:
        progress = int(elapsed_time * 20)
        return jsonify({
            "status": f"Анализ данных... {progress}%",
            "progress": progress
        })
    elif elapsed_time < 10:
        progress = int((elapsed_time - 5) * 20)
        return jsonify({
            "status": f"Обработка результатов... {progress}%",
            "progress": progress
        })
    else:
        # Задача завершена
        actions = {
            "regulations": [
                {
                    "id": "wto_tariff",
                    "title": "Повышение ставки таможенной пошлины до уровня связывания в рамках Всемирной торговой организации (ВТО)",
                    "description": "Рекомендуется повышение пошлины до 15% в рамках обязательств ВТО",
                    "priority": "high",
                    "applicable": True
                },
                {
                    "id": "national_tariff",
                    "title": "Повышение ставки таможенной пошлины до уровня 35–50 % в рамках национального контрсанкционного регулирования",
                    "description": "Применение повышенных ставок в рамках контрсанкционной политики",
                    "priority": "medium",
                    "applicable": True
                },
                {
                    "id": "anti_dumping",
                    "title": "Инициирование антидемпингового расследования в отношении экспортёров из стран(ы) X",
                    "description": "Расследование демпинговых цен на товары из Китая и Германии",
                    "priority": "high",
                    "applicable": True
                },
                {
                    "id": "certification",
                    "title": "Применение сертификации соответствия к импортируемому товару",
                    "description": "Введение обязательной сертификации для обеспечения качества",
                    "priority": "medium",
                    "applicable": True
                },
                {
                    "id": "preferential",
                    "title": "Расширение или инициирование применения преференциального режима в отношении товара в рамках государственных закупок",
                    "description": "Поддержка отечественных производителей через госзакупки",
                    "priority": "low",
                    "applicable": False
                },
                {
                    "id": "other_measures",
                    "title": "Иные меры защиты рынка (запрет или квотирование импорта, промышленный сбор, неавтоматическое лицензирование)",
                    "description": "Дополнительные защитные меры при необходимости",
                    "priority": "low",
                    "applicable": False
                }
            ],
            "companies": [
                {
                    "inn": "1234567890",
                    "name": "ООО 'Электронные системы'",
                    "region": "Москва",
                    "volume": "150 млн руб"
                },
                {
                    "inn": "2345678901", 
                    "name": "АО 'Технологии будущего'",
                    "region": "Санкт-Петербург",
                    "volume": "89 млн руб"
                },
                {
                    "inn": "3456789012",
                    "name": "ПАО 'Инновационные решения'",
                    "region": "Новосибирск", 
                    "volume": "67 млн руб"
                },
                {
                    "inn": "4567890123",
                    "name": "ООО 'Промышленные технологии'",
                    "region": "Екатеринбург",
                    "volume": "45 млн руб"
                },
                {
                    "inn": "5678901234",
                    "name": "АО 'Научно-производственный комплекс'",
                    "region": "Казань",
                    "volume": "32 млн руб"
                }
            ],
            "statistics": {
                "import_volume": "2.5 млрд руб",
                "growth_rate": "+12%",
                "main_suppliers": ["Китай", "Германия", "Япония"],
                "domestic_companies": 5,
                "total_domestic_volume": "383 млн руб"
            }
        }
        
        # Удаляем задачу после завершения
        del analysis_jobs[job_id]
        
        return jsonify({
            "actions": actions,
            "status": "completed"
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    return jsonify({
        "status": "ok",
        "message": "TradeShield API работает"
    })

if __name__ == '__main__':
    print("🚀 Запуск TradeShield Backend API...")
    print("📡 Доступные эндпоинты:")
    print("  GET  /api/product-code/<query>     - Получение предложения кода товара")
    print("  GET  /api/product-names/<code>     - Получение наименований по коду")
    print("  POST /api/analyze                  - Запуск анализа")
    print("  GET  /api/job/<job_id>             - Проверка статуса задачи")
    print("  GET  /api/health                   - Проверка работоспособности")
    print("\n🌐 API доступен по адресу: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
