import cnocr
import time

t1 = time.time()
res_list = cnocr.CnOcr().ocr('../docs/res.png')
print(type(res_list))

lista = []
for res in res_list:
    lista += res
print(lista)
print(len(lista))

print('耗时;', time.time() - t1)
