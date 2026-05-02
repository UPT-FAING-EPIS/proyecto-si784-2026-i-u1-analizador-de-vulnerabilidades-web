from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import requests
import datetime
import json
import re
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Web Vulnerability Scanner API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    modules: List[str]
    depth: int = 2
    timeout: int = 10

class ScanResponse(BaseModel):
    id: int
    target_url: str
    status: str
    result_summary: dict

def simple_header_check(url: str, timeout: int):
    try:
        response = requests.get(url, timeout=timeout)
        headers = response.headers
        findings = []
        if 'X-Frame-Options' not in headers:
            findings.append("Missing X-Frame-Options header")
        if 'Content-Security-Policy' not in headers:
            findings.append("Missing Content-Security-Policy header")
        if 'Strict-Transport-Security' not in headers:
            findings.append("Missing Strict-Transport-Security header")
        if 'X-Content-Type-Options' not in headers:
            findings.append("Missing X-Content-Type-Options header")
        return {"status": "success", "findings": findings, "status_code": response.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_xss(url: str, timeout: int):
    findings = []
    try:
        payload = "<script>alert('XSS')</script>"
        parsed = urlparse(url)
        params = parse_qsl(parsed.query)
        if params:
            new_params = [(k, v + payload) for k, v in params]
            test_url = urlunparse(parsed._replace(query=urlencode(new_params)))
        else:
            test_url = url + ("&" if "?" in url else "?") + f"test={payload}"
        
        response = requests.get(test_url, timeout=timeout)
        if payload in response.text:
            findings.append("Potential XSS vulnerability: Payload reflected in response body.")
            
        return {"status": "success", "findings": findings}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_sqli(url: str, timeout: int):
    findings = []
    sql_errors = ["you have an error in your sql syntax", "warning: mysql", "unclosed quotation mark", "quoted string not properly terminated", "pg_query()", "sqlite3.operationalerror"]
    try:
        payload = "'"
        parsed = urlparse(url)
        params = parse_qsl(parsed.query)
        if params:
            new_params = [(k, v + payload) for k, v in params]
            test_url = urlunparse(parsed._replace(query=urlencode(new_params)))
        else:
            test_url = url + ("&" if "?" in url else "?") + f"id=1{payload}"
            
        response = requests.get(test_url, timeout=timeout)
        lower_body = response.text.lower()
        
        for error in sql_errors:
            if error in lower_body:
                findings.append(f"Potential SQL Injection: Found SQL error '{error}' in response.")
                break
                
        return {"status": "success", "findings": findings}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_csrf(url: str, timeout: int):
    findings = []
    try:
        response = requests.get(url, timeout=timeout)
        body = response.text.lower()
        
        if "<form" in body:
            if not re.search(r'name=["\']?(csrf|token|authenticity_token|_csrf)["\']?', body):
                findings.append("Potential CSRF: Found <form> tag without common CSRF token fields.")
        
        return {"status": "success", "findings": findings}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_open_redirect(url: str, timeout: int):
    findings = []
    try:
        payload = "http://evil-domain.com"
        test_url = url + ("&" if "?" in url else "?") + f"redirect={payload}&next={payload}"
        
        response = requests.get(test_url, timeout=timeout, allow_redirects=False)
        
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get("Location", "")
            if location == payload or location.startswith(payload):
                findings.append("Potential Open Redirect: Server redirects to injected external domain.")
                
        return {"status": "success", "findings": findings}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_info_disclosure(url: str, timeout: int):
    findings = []
    try:
        response = requests.get(url, timeout=timeout)
        headers = response.headers
        
        if "Server" in headers and re.search(r'\d', headers["Server"]):
            findings.append(f"Information Disclosure: Server header exposes version: {headers['Server']}")
        
        if "X-Powered-By" in headers:
            findings.append(f"Information Disclosure: X-Powered-By header is present: {headers['X-Powered-By']}")
            
        if "stack trace" in response.text.lower() or "exception in thread" in response.text.lower():
            findings.append("Information Disclosure: Potential stack trace found in response body.")
            
        return {"status": "success", "findings": findings}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/scan", response_model=ScanResponse)
def run_scan(scan_req: ScanRequest, db: Session = Depends(get_db)):
    # Basic URL validation
    if not scan_req.url.startswith(("http://", "https://")):
        scan_req.url = "http://" + scan_req.url

    # Create scan record
    db_scan = models.Scan(target_url=scan_req.url, status="running")
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    results = {}
    
    if "Headers" in scan_req.modules:
        results["Headers"] = simple_header_check(scan_req.url, scan_req.timeout)
    if "XSS" in scan_req.modules:
        results["XSS"] = check_xss(scan_req.url, scan_req.timeout)
    if "SQL Injection" in scan_req.modules:
        results["SQL Injection"] = check_sqli(scan_req.url, scan_req.timeout)
    if "CSRF" in scan_req.modules:
        results["CSRF"] = check_csrf(scan_req.url, scan_req.timeout)
    if "Open Redirect" in scan_req.modules:
        results["Open Redirect"] = check_open_redirect(scan_req.url, scan_req.timeout)
    if "Info Disclosure" in scan_req.modules:
        results["Info Disclosure"] = check_info_disclosure(scan_req.url, scan_req.timeout)
                
    # Update scan record
    db_scan.status = "completed"
    db_scan.result_summary = json.dumps(results)
    db.commit()
    db.refresh(db_scan)
    
    return {
        "id": db_scan.id,
        "target_url": db_scan.target_url,
        "status": db_scan.status,
        "result_summary": results
    }

@app.get("/api/scans")
def get_scans(db: Session = Depends(get_db)):
    scans = db.query(models.Scan).order_by(models.Scan.id.desc()).all()
    # parse json
    for scan in scans:
        if scan.result_summary:
            scan.result_summary = json.loads(scan.result_summary)
    return scans
