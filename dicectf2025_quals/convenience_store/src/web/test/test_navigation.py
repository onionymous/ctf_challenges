from flask import Flask, render_template_string

app = Flask(__name__)

HOST = "0.0.0.0"
PORT = 5001


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<body>
  <h2>Page Navigation Timing Test</h2>
  <div id="results"></div>
  <script>
    const urls = [
      'http://0.0.0.0:8000/search?query=dice{',
      'http://0.0.0.0:8000/search?query=zzz',
      'http://0.0.0.0:8000/search?query=aaa'
    ];
    const testIterations = 5;
    let results = {};

    // Initialize test state
    let state = JSON.parse(
      sessionStorage.getItem('testState') || 
      '{"index":0,"iteration":0}'
    );

    async function runTest() {
      if (state.iteration >= testIterations) {
        displayResults();
        return;
      }

      const url = urls[state.index];
      const start = performance.now();

      // Save start time before navigating away
      sessionStorage.setItem('startTime', start.toString());

      // Navigate to the target URL
      window.location.href = url;
    }

    // After returning to the test page, calculate duration
    window.addEventListener('pageshow', (event) => {
      const startTime = parseFloat(sessionStorage.getItem('startTime'));
      if (!startTime) return;

      const endTime = performance.now();
      const duration = endTime - startTime;
      const url = urls[state.index];
      const key = url.split('=')[1];

      results[key] = (results[key] || 0) + duration;

      // Update state
      state.index = (state.index + 1) % urls.length;
      if (state.index === 0) state.iteration++;
      sessionStorage.setItem('testState', JSON.stringify(state));

      // Continue test after a short delay
      setTimeout(runTest, 100);
    });

    function displayResults() {
      let output = '';
      for (const [query, total] of Object.entries(results)) {
        output += `Avg. time for "${query}": ${(total / testIterations).toFixed(2)}ms<br>`;
      }
      document.getElementById('results').innerHTML = output;
      sessionStorage.clear();
    }

    // Start test automatically
    if (!window.location.search.includes('restart')) {
      sessionStorage.clear();
      window.location = window.location + '?restart=true';
    } else {
      runTest();
    }
  </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)