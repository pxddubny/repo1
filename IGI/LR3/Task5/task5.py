#Найти максимальный по модулю элемент списка и /
# сумму элементов списка, расположенных между первым и вторым отрицательными элементами

def work():
    while (True):
        try:
            arr = list(map(int, input("Enter list: ").split()))
            break
        except ValueError:
            print ("Wrong input")
    
    print("максимальный по модулю элемент списка")
    print(max_abs_element(arr))
    print("сумма элементов списка")
    print(sum_of_list(arr))
    print("сумма элементов списка, расположенных между первым и вторым отрицательными элементами")
    print(sum_between_negative(arr))

def max_abs_element(arr):
    max = arr[0]
    for x in arr:
        if(abs(x) > max):
            max = x
    return max

def sum_of_list(arr):
    sum = 0
    for x in arr:
        sum += x
    return sum

def sum_between_negative(arr):
    sum = 0
    summing = False
    for x in arr:
        if (x < 0 and summing == True): break
        if (summing): sum += x
        if (x < 0 and summing == False): summing = True
    return sum
