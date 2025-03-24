
import math
from prettytable import PrettyTable

def taylor_exp(x,eps):
    i = 1
    sum = 1
    previous_value = 0
    while (i <= 500 and abs(sum - previous_value) > eps):
        previous_value = sum
        sum += pow(x,i)
        i += 1
    return [i,sum]


def work():
    while(True):
            user_input = input("Enter x: ")
            try:
                x = float(user_input)
                if (abs(x)>=1): ValueError
                else: break

            except ValueError:
                print("Wrong input.")

    while(True):
        user_input = input("Enter eps: ")
        try:
            eps = float(user_input)
            break
        except ValueError:
            print("Wrong input.")
        
    table = PrettyTable()
    table.field_names = ["x", "n", "F(x)", "Math F(x)", "eps"]
    result = taylor_exp(x,eps)
    table.add_row([x, result[0], result[1], 1/(1-x), eps])
    print(table)

