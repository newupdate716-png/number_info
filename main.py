from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def lookup_phone_number(phone_number):
    url = "https://calltracer.in"
    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "country": "IN",
        "q": phone_number
    }

    try:
        # POST রিকোয়েস্ট পাঠানো হচ্ছে
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # টেবিল থেকে তথ্য খোঁজার ফাংশন
        def get_value(label):
            cell = soup.find(string=lambda t: t and label in t)
            if cell:
                tr = cell.find_parent("tr")
                if tr and tr.find_all("td"):
                    tds = tr.find_all("td")
                    if len(tds) > 1:
                        return tds[1].get_text(strip=True)
            return "N/A"

        data = {
            "Number": phone_number,
            "Complaints": get_value("Complaints"),
            "Owner Name": get_value("Owner Name"),
            "SIM Card": get_value("SIM card"),
            "Mobile State": get_value("Mobile State"),
            "IMEI Number": get_value("IMEI number"),
            "MAC Address": get_value("MAC address"),
            "Connection": get_value("Connection"),
            "IP Address": get_value("IP address"),
            "Owner Address": get_value("Owner Address"),
            "Hometown": get_value("Hometown"),
            "Reference City": get_value("Refrence City"),
            "Owner Personality": get_value("Owner Personality"),
            "Language": get_value("Language"),
            "Mobile Locations": get_value("Mobile Locations"),
            "Country": get_value("Country"),
            "Tracking History": get_value("Tracking History"),
            "Tracker ID": get_value("Tracker Id"),
            "Tower Locations": get_value("Tower Locations"),
        }

        # যদি কোনো তথ্য না পাওয়া যায়
        if all(v == "N/A" for k, v in data.items() if k != "Number"):
            return {"error": "No data found for this number."}, 404
            
        return data, 200

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}, 500
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "message": "Welcome to Number Info API",
        "usage": "/info?number=PHONE_NUMBER"
    })

@app.route('/info', methods=['GET'])
def number_info():
    phone_number = request.args.get('number')
    
    if not phone_number:
        return jsonify({"error": "Please provide ?number= parameter"}), 400

    # নাম্বার ফরম্যাট চেক
    clean_number = phone_number.replace('+', '').strip()
    if not clean_number.isdigit():
        return jsonify({"error": "Invalid phone number format"}), 400

    result, status_code = lookup_phone_number(phone_number)
    return jsonify(result), status_code

if __name__ == '__main__':
    # পোর্ট সেট করা (ডিফল্ট ৫০০০)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
