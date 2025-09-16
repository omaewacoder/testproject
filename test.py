import pandas as pd
from pmdarima import auto_arima
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import warnings

# Фильтрация всех предупреждений
warnings.filterwarnings('ignore')

# Загружаем переменные окружения
load_dotenv()

# 1. Загрузка и подготовка данных
data = pd.read_csv('data/airline-passengers.csv', parse_dates=['Month'], index_col='Month')
# Переименовываем колонку для удобства
print("Первые 10 строк исходных данных:")
print(data.head(10))
print("Последние 5 строк исходных данных:")
print(data.tail())

# 2. Визуализация исходных данных
plt.figure(figsize=(12, 8))
plt.plot(data.index, data['Passengers'], label='Исходные данные')
plt.title('Количество пассажиров авиалиний по месяцам (1949-1960)')
plt.xlabel('Дата')
plt.ylabel('Количество пассажиров')
plt.grid(True)
plt.legend()
plt.savefig('data/original_data_plot.png')
plt.show()

# 3. Разделение данных (возьмем последние 12 месяцев для проверки точности)
train = data.iloc[:-12]  # Все данные кроме последнего года
test = data.iloc[-12:]  # Последние 12 месяцев для проверки

print(f"\nРазмер обучающей выборки: {len(train)} месяцев")
print(f"Размер тестовой выборки: {len(test)} месяцев")

# 3. Подбор параметров и обучение модели SARIMA
print("\nПодбор параметров модели SARIMA...")
# Для месячных данных с годовой сезонностью используем m=12
model = auto_arima(data['Passengers'],
                   seasonal=True,  # Включаем сезонность
                   m=12,  # Месячные данные с годовой сезонностью
                   stepwise=True,  # Ускоренный подбор параметров
                   trace=False,  # Вывод процесса подбора
                   error_action='ignore',  # Игнорировать ошибки при подборе
                   suppress_warnings=True,  # Подавить предупреждения
                   information_criterion='aic')  # Критерий для выбора модели

# Ручное указание параметров
# model = ARIMA(data['Passengers'],
#               order=(1, 1, 1),          # ← (p, d, q)
#               seasonal_order=(1, 1, 1, 12))  # ← (P, D, Q, m)

# Тогда не нужен auto_arima
# model.fit()

print("\n" + "=" * 50)
print("ОТЧЕТ ПО МОДЕЛИ:")
print(model.summary())