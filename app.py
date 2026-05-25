from flask import Flask, render_template_string

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Number Range</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: #0f172a;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .card {
            background: #1e293b;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0,0,0,0.4);
            width: 90%;
            max-width: 400px;
        }

        h1 {
            margin-bottom: 20px;
            font-size: 28px;
        }

        .range-box {
            background: #334155;
            padding: 15px;
            border-radius: 10px;
            font-size: 24px;
            word-break: break-all;
            margin-bottom: 20px;
            user-select: all;
        }

        button {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #2563eb;
        }

        .footer {
            margin-top: 20px;
            font-size: 14px;
        }

        a {
            color: #60a5fa;
            text-decoration: none;
        }
    </style>
</head>
<body>

<div class="card">
    <h1>Range</h1>

    <div class="range-box" id="rangeText">
        26134739XXX
    </div>

    <button onclick="copyText()">Copy Range</button>

    <div class="footer">
        Source: <a href="https://tempnumbers.blogspot.com" target="_blank">tempnumbers.blogspot.com</a>
    </div>
</div>

<script>
function copyText() {
    const text = document.getElementById('rangeText').innerText;

    navigator.clipboard.writeText(text).then(() => {
        alert('Copied: ' + text);
    });
}
</script>

</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
