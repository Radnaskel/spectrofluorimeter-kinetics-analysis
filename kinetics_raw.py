import statistics

with open('C:\\Users\\User\\Downloads\\spectral_data.dat', 'r') as file:
    content = file.read()

# Готовим файл
lines = content.split('\n')
switching_times = lines[0]
print(switching_times)

# Получаем времена облучения
LEDtimes = switching_times.split('\t')[3:]
LEDtimes = list(map(float, LEDtimes[:-1]))
print(LEDtimes)

spectra_table = lines[1:]  # Получение строк таблицы спектров

# Получаем лист с длинами волн
zero_row = spectra_table[0]
zero_row_list = zero_row.split('\t')
zero_row_list = list(map(float, zero_row_list[:-1]))
print(zero_row_list)

# Получаем интенсивности при длинах волн около 520 и 580 в первой строке
indices520 = []
for i in range(len(zero_row_list)):
    if 519.5 <= zero_row_list[i] <= 520.5:
        indices520.append(i)
indices580 = []
for i in range(len(zero_row_list)):
    if 579.5 <= zero_row_list[i] <= 580.5:
        indices580.append(i)

# Усредняем значения интенсивностей для импульсов около 520 нм в первой строке
values = spectra_table[1].split('\t')
values_520_first_row = []
for i in indices520:
    values_520_first_row.append(values[i])
values_520_first_row = list(map(float, values_520_first_row))
print(statistics.mean(values_520_first_row))

# Разделим значения из второго столбца (для примера) по LEDtimes, сначала облучение 400 нм, потом 560 нм
LEDtimes_counter = 2
impulse = 400
imp400_times = []
imp560_times = []
imp_400_inten_520 = []
imp_560_inten_520 = []
imp_400_inten_580 = []
imp_560_inten_580 = []
for row in spectra_table[1:-1]:
    values = row.split('\t')  # Предполагается, что значения разделены табуляцией
    values = list(map(float, values[:-1]))
    values_520_row = []
    values_580_row = []
    for i in indices520:
        values_520_row.append(values[i])
    for j in indices580:
        values_580_row.append(values[j])
    values_520_mean = int(statistics.mean(values_520_row))
    values_580_mean = int(statistics.mean(values_580_row))
    if values[0] > 174.6:
        break
    elif impulse == 400:
        if values[0] <= LEDtimes[LEDtimes_counter]:
            imp400_times.append(values[0])
            imp_400_inten_520.append(values_520_mean)
            imp_400_inten_580.append(values_580_mean)
            continue
        else:
            #imp560_times.append(values[0])
            #imp_560_inten_520.append(values_520_mean)
            LEDtimes_counter += 1
            impulse = 560
            continue
    elif impulse == 560:
        if values[0] <= LEDtimes[LEDtimes_counter]:
            imp560_times.append(values[0])
            imp_560_inten_520.append(values_520_mean)
            imp_560_inten_580.append(values_580_mean)
            continue
        else:
            #imp400_times.append(values[0])
            #imp_400_inten_520.append(values_520_mean) # если удалить, то уберём выпад. значения
            LEDtimes_counter += 1
            impulse = 400


with open('imp400_inten_520.csv', 'w') as f:
    for i,j in zip(imp400_times, imp_400_inten_520):
        f.write(str(i) + ',' + str(j) + '\n')
with open('imp560_inten_520.csv', 'w') as f:
    for i,j in zip(imp560_times, imp_560_inten_520):
        f.write(str(i) + ',' + str(j) + '\n')
with open('imp400_inten_580.csv', 'w') as f:
    for i,j in zip(imp400_times, imp_400_inten_580):
        f.write(str(i) + ',' + str(j) + '\n')
with open('imp560_inten_580.csv', 'w') as f:
    for i,j in zip(imp560_times, imp_560_inten_580):
        f.write(str(i) + ',' + str(j) + '\n')

#Идея такая: идём по LED временам, первые два (от 0) значения это облучение в 400 нм, затем идёт облучение в 560 нм около 1 сек и т.д. Создаём два списка: для облучения при 400 нм и при облучении в 560. Записываем первые значения в список 400 нм. Мы сравниваем наше время в первом столбце с LED временами и когда значение в стобце становится больше, то записываем в следующий список. И соответственно идём параллельно по списку LEDtimes.
#Для усреднения берутся столбцы с номерами значений из zero_row, которые отстоят от 520+-0,5 нм и 580+-0,5 нм.
impulse = 400
intensities400 = []
intensities560 = []
for row in spectra_table[1:-1]:
    values = row.split('\t')  # Предполагается, что значения разделены табуляцией
    values = list(map(float, values[:-1]))
    if values[0] > 174.7:
        break
    elif impulse == 400:
        if values[0] <= LEDtimes[LEDtimes_counter]:
            intensities400.append(values[1])
            continue
        else:
            intensities560.append(values[1])
            LEDtimes_counter += 1
            impulse = 560
            continue
    elif impulse == 560:
        if values[0] <= LEDtimes[LEDtimes_counter]:
            intensities560.append(values[1])
            continue
        else:
            intensities400.append(values[1])
            LEDtimes_counter += 1
            impulse = 400