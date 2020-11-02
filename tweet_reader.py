import json
import io

with io.open('E:/Work/tweet.js', encoding='utf8') as js_file:
    data = js_file.read()
    objs = data[data.find('[') : data.rfind(']')+1]
    jsonObj = json.loads(objs)

