import time

from font_transfer import FontTransfer

t1 = time.time()

ft = FontTransfer()
# print(ft.get_chars_from_font('../docs/land.ttf'))

# ft.font_to_image('land.ttf')

transfer_dict = ft.get_font_transfer_dict('../docs/land.ttf')
print(transfer_dict)
print(len(transfer_dict))

t2 = time.time()
print('总耗时:{}'.format(t2 - t1))
