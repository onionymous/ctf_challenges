# run with python test_iframe.py

from flask import Flask, render_template_string

app = Flask(__name__)

# Host on port 3000 to differ from the embedded service (8000)
HOST = "0.0.0.0"
PORT = 3000

# Simple page with an iframe pointing to 0.0.0.0:8000
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>test</title>
</head>
<body>
   <iframe src="http://0.0.0.0:8000/search?query=z" style="width: 100%; height: 500px;"></iframe> 
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)