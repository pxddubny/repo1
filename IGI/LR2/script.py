import sys
from geometric_lib.circle import area as circle_area, perimeter as circle_perimeter
from geometric_lib.square import area as square_area, perimeter as square_perimeter

# Проверка аргументов командной строки
if len(sys.argv) != 3:
    print("Usage: python script.py <radius> <side>")
    sys.exit(1)

# Получение аргументов
radius = float(sys.argv[1])
side = float(sys.argv[2])

# Вычисление площади и периметра круга
print(f"Area of circle with radius {radius}: {circle_area(radius)}")
print(f"Perimeter of circle with radius {radius}: {circle_perimeter(radius)}")

# Вычисление площади и периметра квадрата
print(f"Area of square with side {side}: {square_area(side)}")
print(f"Perimeter of square with side {side}: {square_perimeter(side)}")
