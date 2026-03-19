#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Перемножение матриц с использованием отдельных процессов
(на основе кода из репозитория 3_Parallelism)

СПРАВКА: В исходном коде из 3_Parallelism использовался пул процессов.
Здесь мы создаём отдельный Process для КАЖДОГО элемента матрицы.
"""

import time
from multiprocessing import Process, Queue
import random

def element(index, A, B):
    """Вычисляет один элемент матрицы C = A * B по индексу (i, j)"""
    i, j = index
    res = 0
    # получить размерность вектора для умножения
    N = len(A[0])  # или len(B)
    for k in range(N):
        res += A[i][k] * B[k][j]
    return res

def element_to_queue(index, A, B, q):
    """Вычисляет элемент и кладёт результат в очередь"""
    res = element(index, A, B)
    q.put((index, res))  # отправляем кортеж (индекс, значение)

def sequential_multiply(A, B):
    """Последовательное перемножение матриц"""
    n = len(A)      # строки в A
    m = len(A[0])   # столбцы в A = строки в B
    p = len(B[0])   # столбцы в B
    
    C = [[0] * p for _ in range(n)]
    
    for i in range(n):
        for j in range(p):
            C[i][j] = element((i, j), A, B)
    
    return C

def parallel_multiply(A, B):
    """Параллельное перемножение матриц с использованием отдельных процессов"""
    n = len(A)      # строки в A
    m = len(A[0])   # столбцы в A = строки в B
    p = len(B[0])   # столбцы в B
    
    # Создаём матрицу для результата
    C = [[0] * p for _ in range(n)]
    
    # TODO 1: Создать процесс для каждого элемента результирующей матрицы
    # и передать результат через Queue.
    # Подсказка:
    # 1. Создайте очередь: q = Queue()
    # 2. Создайте список processes = []
    # 3. Для каждого индекса (i, j) создайте процесс:
    #    proc = Process(target=element_to_queue, args=((i, j), A, B, q))
    #    processes.append(proc)
    #    proc.start()
    # 4. Дождитесь завершения всех процессов через proc.join()
    # 5. Получите результаты из очереди и заполните матрицу C
    
    # ═════════════ ИСПРАВЛЕННОЕ РЕШЕНИЕ ═════════════
    
    # 1. Создаём очередь для сбора результатов
    q = Queue()
    
    # 2. Создаём список для хранения процессов
    processes = []
    
    # 3. Создаём и запускаем процесс для каждого элемента матрицы
    print(f"  Создание {n * p} процессов...")
    for i in range(n):
        for j in range(p):
            # ИСПРАВЛЕНО: используем другое имя переменной для процесса
            proc = Process(target=element_to_queue, args=((i, j), A, B, q))
            processes.append(proc)
            proc.start()
    
    # 4. Ждём завершения всех процессов
    print("  Ожидание завершения всех процессов...")
    for proc in processes:  # ИСПРАВЛЕНО: используем proc вместо p
        proc.join()  # ИСПРАВЛЕНО: используем proc.join() вместо p.join()
    
    # 5. Собираем результаты из очереди
    print("  Сбор результатов из очереди...")
    for _ in range(n * p):
        (i, j), value = q.get()
        C[i][j] = value
    
    # ═════════════ КОНЕЦ РЕШЕНИЯ ═════════════
    
    return C

def print_matrix(matrix, name, max_display=5):
    """Красивый вывод матрицы (показывает только первые max_display строк/столбцов)"""
    print(f"\n{name}:")
    rows = len(matrix)
    cols = len(matrix[0])
    
    for i in range(min(rows, max_display)):
        print("  ", end="")
        for j in range(min(cols, max_display)):
            print(f"{matrix[i][j]:8.2f}", end=" ")
        if cols > max_display:
            print("...", end="")
        print()
    if rows > max_display:
        print("  ...")

if __name__ == '__main__':
    # Создаём тестовые матрицы
    print("Генерация матриц...")
    N = 10  # размер матрицы (для теста возьмём 100x100)
    
    A = [[random.random() for _ in range(N)] for _ in range(N)]
    B = [[random.random() for _ in range(N)] for _ in range(N)]
    
    print(f"Матрицы размером {N}x{N} созданы")
    
    # TODO 2: Замерить время последовательного и параллельного вычисления
    # Подсказка: используйте time.time() до и после вызова функций
    
    # ═════════════ИСПРАВЛЕННОЕ РЕШЕНИЕ ═════════════
    
    print("\n" + "="*60)
    print("ЗАМЕР ВРЕМЕНИ ВЫПОЛНЕНИЯ")
    print("="*60)
    
    # Последовательное вычисление
    print("\n--- Последовательное вычисление ---")
    start_time = time.time()
    C_seq = sequential_multiply(A, B)
    seq_time = time.time() - start_time
    print(f"Время выполнения: {seq_time:.4f} секунд")
    
    # Параллельное вычисление
    print("\n--- Параллельное вычисление ---")
    start_time = time.time()
    C_par = parallel_multiply(A, B)
    par_time = time.time() - start_time
    print(f"Время выполнения: {par_time:.4f} секунд")
    
    # Проверка корректности результатов
    print("\n" + "="*60)
    print("ПРОВЕРКА РЕЗУЛЬТАТОВ")
    print("="*60)
    
    # Проверяем несколько элементов
    test_positions = [(0, 0), (N//2, N//2), (N-1, N-1)]
    all_correct = True
    
    for i, j in test_positions:
        seq_val = C_seq[i][j]
        par_val = C_par[i][j]
        diff = abs(seq_val - par_val)
        print(f"  C[{i}][{j}]: {seq_val:.6f} vs {par_val:.6f} (разница: {diff:.10f})")
        if diff > 1e-10:
            all_correct = False
    
    if all_correct:
        print("\n✓ Все проверенные элементы совпадают!")
    else:
        print("\n✗ Обнаружены расхождения в результатах!")
    
    # Вычисляем ускорение
    print("\n" + "="*60)
    print("АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("="*60)
    
    if par_time > 0:
        speedup = seq_time / par_time
        
        print(f"\nПоследовательное время: {seq_time:.4f} сек")
        print(f"Параллельное время:     {par_time:.4f} сек")
        print(f"Ускорение:              {speedup:.2f}x")
        print(f"Количество процессов:   {N*N} (по одному на элемент)")
        
        print(f"\nПримечание по производительности:")
        if speedup < 1:
            print("  ⚠ Параллельная версия работает МЕДЛЕННЕЕ последовательной!")
            print("    Это ожидаемо для маленьких матриц (100x100), так как:")
        else:
            print("  ✓ Есть небольшое ускорение, но оно далеко от идеального, так как:")
        
        print("  • Накладные расходы на создание 10,000 процессов огромны")
        print("  • Операционная система тратит много времени на переключение контекста")
        print("  • Очередь Queue становится узким местом")
        print("  • Это демонстрационный пример, показывающий, ПОЧЕМУ пулы процессов лучше")
    
    print("="*60)
    
    # Покажем небольшую часть матрицы для наглядности
    print_matrix(C_seq, "Часть результирующей матрицы C")
    
    # ═════════════ КОНЕЦ РЕШЕНИЯ ═════════════
