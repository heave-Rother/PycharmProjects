#n*n矩阵相乘的实现
    # 1：传入两个矩阵------list传入
    # 2：表示矩阵的每个元素-------将第二个矩阵转置

def matrix_n(list1,list2):
    list3 = []
    list4 = []
    listsa = []
    listsb = []
    n = int(len(list1)**0.5)#求平方根
    for k in range(n):
        for i in range(n):
            b = k + i*n
            list3.append(list2[b])

    for k in range(n):
        listsa.append(list1[k*n:(k+1)*n])
        listsb.append(list3[k*n:(k+1)*n])
    for lista in listsa:
        for listb in listsb:
            num = 0
            for i in range(n):
                d = lista[i] * listb[i]
                num += d
            list4.append(num)
    print(list4)















list1 = [1,2,3,4,5,6,7,8,9]
list2 = [1,2,3,4,5,6,7,8,9]
matrix_n(list1,list2)







