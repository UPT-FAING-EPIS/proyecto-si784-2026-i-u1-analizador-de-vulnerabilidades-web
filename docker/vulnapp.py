"""
VulnApp - Intentionally Vulnerable Web Application for Testing VulnScan.
WARNING: This application is deliberately insecure. Use ONLY in isolated environments.
"""

from flask import Flask, request, render_template_string, make_response
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vulnapp.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS products
                    (id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT)''')
    conn.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?)", [
        (1, 'admin', 'secret123', 'admin@example.com'),
        (2, 'alice', 'pass456', 'alice@example.com'),
        (3, 'bob', 'hunter2', 'bob@example.com'),
    ])
    conn.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?)", [
        (1, 'Widget A', 9.99, 'electronics'),
        (2, 'Gadget B', 29.99, 'electronics'),
        (3, 'Book C', 14.99, 'books'),
    ])
    conn.commit()
    conn.close()


BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>VulnApp - {{ title }}</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
  nav { background: #333; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
  nav a { color: white; text-decoration: none; margin-right: 15px; }
  .card { background: white; padding: 20px; border-radius: 4px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
  input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; width: 200px; }
  button { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
  th { background: #f8f9fa; }
  .result { background: #fff3cd; padding: 10px; border-radius: 3px; margin-top: 10px; }
</style>
</head>
<body>
<nav>
  <a href="/">🏠 Home</a>
  <a href="/search">🔍 Search</a>
  <a href="/login">🔑 Login</a>
  <a href="/greet">👋 Greet</a>
  <a href="/products">📦 Products</a>
  <a href="/contact">✉ Contact</a>
</nav>
<div class="card">{{ content | safe }}</div>
</body>
</html>
"""


@app.route('/')
def index():
    content = """
    <h1>VulnApp - Intentionally Vulnerable Application</h1>
    <p><strong>⚠️ WARNING:</strong> This application is intentionally vulnerable for security testing purposes only.</p>
    <p>Use the navigation above to explore the vulnerable endpoints.</p>
    <ul>
      <li><a href="/search?q=test">Search (XSS + SQLi)</a></li>
      <li><a href="/login">Login (SQLi)</a></li>
      <li><a href="/greet?name=World">Greet (XSS reflected)</a></li>
      <li><a href="/products?category=electronics">Products (SQLi)</a></li>
      <li><a href="/contact">Contact form (CSRF, XSS)</a></li>
    </ul>
    """
    resp = make_response(render_template_string(BASE_TEMPLATE, title='Home', content=content))
    # Deliberately missing security headers
    return resp


@app.route('/search')
def search():
    q = request.args.get('q', '')
    results = []
    if q:
        conn = sqlite3.connect(DB_PATH)
        # VULNERABLE: Direct string interpolation → SQLi
        try:
            cursor = conn.execute(f"SELECT name, price, category FROM products WHERE name LIKE '%{q}%'")
            results = cursor.fetchall()
        except Exception as e:
            results = [('Error', str(e), '')]
        conn.close()

    # VULNERABLE: Reflected XSS - q rendered directly
    content = f"""
    <h2>Search Products</h2>
    <form method="GET">
      <input name="q" value="{q}" placeholder="Search products...">
      <button type="submit">Search</button>
    </form>
    """
    if q:
        content += f'<div class="result">Results for: {q}</div>'  # XSS here
        if results:
            content += '<table><tr><th>Name</th><th>Price</th><th>Category</th></tr>'
            for row in results:
                content += f'<tr><td>{row[0]}</td><td>${row[1]}</td><td>{row[2]}</td></tr>'
            content += '</table>'
        else:
            content += '<p>No results found.</p>'

    resp = make_response(render_template_string(BASE_TEMPLATE, title='Search', content=content))
    return resp


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        conn = sqlite3.connect(DB_PATH)
        # VULNERABLE: SQLi in login
        try:
            cursor = conn.execute(
                f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            )
            user = cursor.fetchone()
            if user:
                message = f'<span style="color:green">Welcome, {user[1]}! (ID: {user[0]})</span>'
                # VULNERABLE: No HttpOnly, no Secure, no SameSite on session cookie
                resp = make_response(render_template_string(BASE_TEMPLATE, title='Login', content=f"""
                    <h2>Login</h2>{message}
                    <p><a href="/">Go to home</a></p>
                """))
                resp.set_cookie('session', f'user_id={user[0]}')  # insecure cookie
                return resp
            else:
                message = '<span style="color:red">Invalid credentials</span>'
        except Exception as e:
            message = f'<span style="color:red">DB Error: {e}</span>'  # Error disclosure
        conn.close()

    content = f"""
    <h2>Login</h2>
    {message}
    <form method="POST">
      <div><input name="username" placeholder="Username" autocomplete="off"></div>
      <div><input name="password" type="password" placeholder="Password"></div>
      <div><button type="submit">Login</button></div>
    </form>
    <p><small>Try: admin / secret123</small></p>
    """
    return render_template_string(BASE_TEMPLATE, title='Login', content=content)


@app.route('/greet')
def greet():
    name = request.args.get('name', 'Stranger')
    # VULNERABLE: Reflected XSS - direct interpolation
    content = f"""
    <h2>Greeting</h2>
    <p>Hello, {name}!</p>
    <form method="GET">
      <input name="name" value="{name}" placeholder="Your name">
      <button type="submit">Greet me</button>
    </form>
    """
    return render_template_string(BASE_TEMPLATE, title='Greet', content=content)


@app.route('/products')
def products():
    category = request.args.get('category', '')
    conn = sqlite3.connect(DB_PATH)
    # VULNERABLE: SQLi
    try:
        if category:
            cursor = conn.execute(f"SELECT * FROM products WHERE category='{category}'")
        else:
            cursor = conn.execute("SELECT * FROM products")
        rows = cursor.fetchall()
    except Exception as e:
        rows = [(0, f'Error: {e}', 0, '')]
    conn.close()

    rows_html = ''.join(
        f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>${r[2]}</td><td>{r[3]}</td></tr>'
        for r in rows
    )
    content = f"""
    <h2>Products</h2>
    <form method="GET">
      <input name="category" value="{category}" placeholder="Filter by category">
      <button type="submit">Filter</button>
    </form>
    <table>
      <tr><th>ID</th><th>Name</th><th>Price</th><th>Category</th></tr>
      {rows_html}
    </table>
    """
    return render_template_string(BASE_TEMPLATE, title='Products', content=content)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = ''
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        msg = request.form.get('message', '')
        # VULNERABLE: No CSRF protection, XSS in name echo
        message = f'<div class="result">Thank you {name}! We received your message.</div>'

    content = f"""
    <h2>Contact Us</h2>
    {message}
    <form method="POST">
      <!-- VULNERABLE: No CSRF token -->
      <div><input name="name" placeholder="Your name"></div>
      <div><input name="email" type="email" placeholder="Your email"></div>
      <div><textarea name="message" placeholder="Your message" rows="4" style="width:300px"></textarea></div>
      <div><button type="submit">Send Message</button></div>
    </form>
    """
    return render_template_string(BASE_TEMPLATE, title='Contact', content=content)


init_db()   # initialise on startup (Windows + Linux compatible)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
