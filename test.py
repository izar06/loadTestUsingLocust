import csv
import json
import time
from locust import HttpUser, task, between, events

# === SETUP CSV LOGGER ===
log_filename = f"loadtest_log_{time.strftime('%Y%m%d%H%M%S')}.csv"
csv_file = open(log_filename, mode="w", newline="")
csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_MINIMAL)

# Menulis header ke file CSV
csv_writer.writerow([
    "Request Type", "Endpoint", "Response Time (s)", "Status Code", "Headers",
    "Request Body", "Response Body", "Status"
])
csv_file.flush()

@events.request.add_listener
def log_request_response(request_type, name, response_time, response, context, exception, **kwargs):
    payload = context.get("payload", {})
    headers = context.get("headers", {})
    status = "SUCCESS" if exception is None and response.status_code == 200 else "FAILURE"
    try:
        if exception is None:
            csv_writer.writerow([
                request_type,
                name,
                response_time,
                response.status_code,
                json.dumps(headers, ensure_ascii=False),
                json.dumps(payload, ensure_ascii=False),
                response.text,
                status
            ])
        else:
            csv_writer.writerow([
                request_type,
                name,
                response_time,
                "ERROR",
                json.dumps(headers, ensure_ascii=False),
                json.dumps(payload, ensure_ascii=False),
                f"Request failed with exception: {exception}",
                "FAILURE"
            ])
        csv_file.flush()
    except Exception as e:
        print(f"Error logging request response: {e}")

# === LOCUST CLASS ===
class APIPostUser(HttpUser):
    wait_time = between(1, 3)  # waktu tunggu antar request per user (1-3 detik)

    @task
    def test(self):
        url = "/objects"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "name": "Apple MacBook Pro 16",
            "data": {
                "year": 2019,
                "price": 1849.99,
                "CPU model": "Intel Core i9",
                "Hard disk size": "1 TB"
            }
        }
        response = self.client.post(
            url,
            headers=headers,
            json=payload,
            context={"payload": payload, "headers": headers}
        )
        print("\n=== HIT ENDPOINT: POST /objects ===")
        print(f"Request headers: {headers}")
        print(f"Request body: {json.dumps(payload, indent=2)}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        # === VALIDASI RESPONSE ===
        if response.status_code == 200:
            print("✅ Validasi sukses: response status 200 OK.")
        else:
            print(f"❌ Validasi gagal: expected 200, got {response.status_code}.")


# from locust import HttpUser, task, between

# class APIPostUser(HttpUser):
#     # waktu tunggu antar request per user (random antara 1-3 detik)
#     wait_time = between(1, 3)

#     @task
#     def test(self): #step awal buat function
#         url = "/objects" #siapkan url yang ingin di load test
#         #siapkan headers
#         headers = {
#             "Content-Type": "application/json"
#         }
#         #siapkan payloadnya
#         payload = {
#             "name": "Apple MacBook Pro 16",
#             "data": {
#                 "year": 2019,
#                 "price": 1849.99,
#                 "CPU model": "Intel Core i9",
#                 "Hard disk size": "1 TB"
#                 }
#         }
        
#         self.client.post(url, headers=headers, json=payload)

