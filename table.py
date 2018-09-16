import numpy as np
import pandas as pd
import datetime
import time

#This is just a example df. A normal df will have headers with empty set. Use a loop to append values.
''' Ex:
>>> df = pd.DataFrame(columns=['A'])
>>> for i in range(5):
...     df = df.append({'A': i}, ignore_index=True)
>>> df
'''

d = {'Users' : ['Bob','Sandy','Alex'],
     'Transaction Processed' : [datetime.datetime.now(),datetime.datetime.now(),datetime.datetime.now()],
     'Amount' : [10, -20, 30]}

df = pd.DataFrame(d)
html = df.to_html(classes=["table-bordered", "table-striped", "table-hover w-75 p-3"],index=False)

html = "{% extends 'layout.html' %}\n" + "{% block title %} CookieJar {% endblock %}\n" + "{% block main %}\n" + html + "\n" "{% endblock %}\n"
print (html)
text_file = open ("index.html", "w")
text_file.write (html)
text_file.close ()
