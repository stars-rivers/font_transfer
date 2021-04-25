from fontTools.ttLib import TTFont

ttf = TTFont('../docs/land.ttf')
# ttf.saveXML('../docs/land.xml')

print(ttf['cmap'].getBestCmap())

new_dict = ttf['cmap'].getBestCmap()

char_dict = {}
for k, v in new_dict.items():
    if ttf['glyf'][v].xMin:
        char_dict[k] = v

print(char_dict)
print(len(char_dict))

# print(ttf['hmtx'])
# for x in ttf["cmap"].tables:
#     print([y for y in x.cmap.items() if ttf['glyf'][y[1]].xMin])
# ttf = TTFont('../docs/woff.woff')
# ttf.saveXML('../docs/woff.xml')
