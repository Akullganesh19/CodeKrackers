import requests

url = "http://localhost:8000/api/v1/threats/"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Nzg3NTI0ODMsInN1YiI6IjMifQ.Ir_8sKSgsQ7oc8UDNi89kM7HTtYYvccqOXH_8NCDmjM",
    "Content-Type": "application/json",
}
data = {
    "type": "smishing",
    "source_number": "SCAM-SMS-DRYRUN",
    "content": "DRY RUN: This is a simulated threat for the demo. Visit http://vas.ai/demo",
    "severity": "critical",
    "confidence_score": 0.99,
}

response = requests.post(url, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(response.json())
