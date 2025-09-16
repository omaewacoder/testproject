import pandas as pd
from pmdarima import auto_arima
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Загружаем переменные окружения
load_dotenv()

# 1. Загрузка и подготовка данных
print("Загрузка данных...")
data = pd.read_csv('data/airline-passengers.csv', parse_dates=['Month'], index_col='Month')
# Переименовываем колонку для удобства
data = data.rename(columns={'Passengers': 'passengers'})
print("Первые строки данных:")
print(data.head())
print("\nИнформация о данных:")
print(data.info())

# 2. Визуализация исходных данных
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['passengers'], label='Исторические данные')
plt.title('Месячное количество пассажиров авиалиний (1949-1960)')
plt.xlabel('Дата')
plt.ylabel('Количество пассажиров')
plt.grid(True)
plt.legend()
plt.savefig('data/original_data_plot.png')
plt.show()

# 4. Подбор параметров и обучение модели SARIMA
print(f"\nРазмер обучающей выборки: {len(data)} месяцев")
print("\nПодбор параметров модели SARIMA...")
# Для месячных данных с годовой сезонностью используем m=12
model = auto_arima(train['passengers'],
                   seasonal=True,  # Включаем сезонность
                   m=12,  # Месячные данные с годовой сезонностью
                   stepwise=True,  # Ускоренный подбор параметров
                   trace=True,  # Вывод процесса подбора
                   error_action='ignore',  # Игнорировать ошибки при подборе
                   suppress_warnings=True,  # Подавить предупреждения
                   information_criterion='aic')  # Критерий для выбора модели

print("\n" + "=" * 50)
print("ОТЧЕТ ПО МОДЕЛИ:")
print(model.summary())

# 5. Построение прогноза
forecast_periods = 24  # Прогнозируем на 2 года вперед
forecast, conf_int = model.predict(n_periods=forecast_periods,
                                   return_conf_int=True)

# 6. Создание временного индекса для прогноза
last_date = data.index[-1]  # Последняя дата в исходных данных
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=31),
                             periods=forecast_periods,
                             freq='M')  # 'M' для месячных данных

# 7. Создание DataFrame с прогнозом
forecast_df = pd.DataFrame({
    'date': future_dates,
    'forecast': forecast,
    'confidence_lower': conf_int[:, 0],
    'confidence_upper': conf_int[:, 1]
})
forecast_df.set_index('date', inplace=True)

# 8. Визуализация результатов
plt.figure(figsize=(14, 7))
plt.plot(data.index, data['passengers'], label='Исторические данные', color='blue')
plt.plot(forecast_df.index, forecast_df['forecast'], label='Прогноз', color='red', linewidth=2)
plt.fill_between(forecast_df.index,
                 forecast_df['confidence_lower'],
                 forecast_df['confidence_upper'],
                 color='pink', alpha=0.3, label='Доверительный интервал (95%)')
plt.title('Прогноз количества пассажиров авиалиний на 2 года')
plt.xlabel('Дата')
plt.ylabel('Количество пассажиров')
plt.legend()
plt.grid(True)
plt.savefig('data/forecast_plot.png', dpi=300, bbox_inches='tight')
plt.show()

# 9. Сохранение прогноза в CSV
forecast_df[['forecast']].to_csv('data/forecast_results.csv')
print(f"\nПрогноз сохранен в 'data/forecast_results.csv'")

# 10. Запись в базу данных PostgreSQL
print("\nПодключение к базе данных...")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Подготовка данных для вставки
records = [
    (row['date'], row['forecast'], row['confidence_lower'], row['confidence_upper'], 'sarima_auto')
    for _, row in forecast_df.reset_index().iterrows()
]

try:
    # Подключение к базе данных
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    # SQL запрос для вставки данных
    insert_query = """
    INSERT INTO forecasts (forecast_date, predicted_value, confidence_lower, confidence_upper, model_name)
    VALUES %s
    ON CONFLICT (forecast_date) DO UPDATE
    SET
        predicted_value = EXCLUDED.predicted_value,
        confidence_lower = EXCLUDED.confidence_lower,
        confidence_upper = EXCLUDED.confidence_upper,
        model_name = EXCLUDED.model_name,
        created_at = CURRENT_TIMESTAMP;
    """

    # Выполнение пакетной вставки
    execute_values(cursor, insert_query, records)
    conn.commit()
    print(f"Успешно добавлено/обновлено {len(records)} записей в базе данных")

    # Проверка записанных данных
    cursor.execute("SELECT COUNT(*) FROM forecasts;")
    count = cursor.fetchone()[0]
    print(f"Всего записей в таблице forecasts: {count}")

except Exception as e:
    print(f"Ошибка при работе с базой данных: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()
        print("Соединение с базой данных закрыто")

print("\nГотово! Прогноз построен и сохранен.")