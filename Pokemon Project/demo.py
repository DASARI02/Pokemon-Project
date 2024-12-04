a =  [{'name': 'chaitu'}, {'age': 16}, {'name': 'harry'}, {'age': 15}, {'name': 'potter'}, {'age': 16}]
page_size = 2
page_n = 2

b = (page_n -1 )* page_size  #2
c = page_n + page_size    #4

d = a[b:c]
print(d)