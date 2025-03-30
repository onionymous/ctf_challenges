# run with python test_img_tag.py

from flask import Flask, render_template_string

app = Flask(__name__)

# Host on port 5000 to differ from the embedded service (8000)
HOST = "0.0.0.0"
PORT = 5000

# Simple page with an img tag pointing to 0.0.0.0:8000
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>test</title>
</head>
<body>
    <img src="http://localhost:8000/search?query=z"></img>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)