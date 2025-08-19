import os.path

import towhee

path = os.path.abspath('test.jpg')
resnet50 = towhee.pipeline('towhee/image-embedding-resnet50')
vector = resnet50(path)
print(vector)
