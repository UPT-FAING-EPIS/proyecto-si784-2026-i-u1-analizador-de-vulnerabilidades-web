from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Vulnerable Test Site")

@app.get("/", response_class=HTMLResponse)
def index(request: Request, test: str = "", id: str = "", redirect: str = ""):
    # 1. Open Redirect Vulnerability
    if redirect:
        # Vulnerable open redirect - redirects anywhere specified by user
        return RedirectResponse(url=redirect)
        
    # 2. XSS Vulnerability
    # The 'test' parameter is reflected directly in the HTML without sanitization
    reflected_xss = test

    # 3. SQL Injection Simulation
    # If the user injects a quote, simulate a database error
    sql_error = ""
    if "'" in id:
        sql_error = "<b>Warning: MySQL server has gone away</b><br/>You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version"
        
    # 4. Info Disclosure Simulation
    # Stack trace leak
    stack_trace = ""
    if id == "error":
        stack_trace = """
        <pre>
        Exception in thread "main" java.lang.NullPointerException
            at com.example.vulnerable.Main.process(Main.java:42)
            at com.example.vulnerable.Main.main(Main.java:15)
        </pre>
        """

    # 5. CSRF Vulnerability
    # A form that performs a state-changing operation without a CSRF token
    csrf_form = """
        <h3>Update Profile (Vulnerable to CSRF)</h3>
        <form action="/update" method="POST">
            <input type="text" name="email" value="user@example.com" />
            <input type="submit" value="Update Email" />
        </form>
    """

    # Missing Security Headers (automatically missing unless we add them)
    # The response won't have X-Frame-Options, Content-Security-Policy, etc.

    html_content = f"""
    <html>
        <head>
            <title>Vulnerable Test Application</title>
        </head>
        <body>
            <h1>Welcome to the deliberately vulnerable site</h1>
            <p>This site is designed to fail all security checks.</p>
            
            <div id="xss-target">
                Your search query: {reflected_xss}
            </div>
            
            <div id="sql-error">
                {sql_error}
            </div>
            
            <div id="info-leak">
                {stack_trace}
            </div>
            
            {csrf_form}
        </body>
    </html>
    """
    
    # Intentionally add vulnerable headers to trigger Info Disclosure
    response = HTMLResponse(content=html_content)
    response.headers["Server"] = "Apache/2.4.41 (Ubuntu)"
    response.headers["X-Powered-By"] = "PHP/7.4.3"
    
    return response

@app.post("/update")
def update_profile():
    return {"message": "Profile updated successfully without CSRF check!"}
