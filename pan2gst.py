from flask import Flask, jsonify, request
import requests
from datetime import datetime
import pytz
import json

app = Flask(__name__)

# GST API Configuration
GST_API_URL = "https://blog-backend.mastersindia.co/api/v1/custom/search/name_and_pan/"

# Headers for GST API
HEADERS = {
    "Host": "blog-backend.mastersindia.co",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.mastersindia.co/gst-number-search-by-name-and-pan/",
    "Origin": "https://www.mastersindia.co",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=0",
    "Te": "trailers"
}

def get_ist_time():
    """Get current time in custom format (DD-MM-YYYY hh:mm AM/PM, [IND])"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    return current_time.strftime("%d-%m-%Y %I:%M %p, [IND]")

def pretty_response(data, status_code=200):
    """Create pretty printed JSON response"""
    response = app.response_class(
        response=json.dumps(data, indent=4, ensure_ascii=False) + '\n',
        status=status_code,
        mimetype='application/json'
    )
    return response

@app.route('/', methods=['GET'])
def base_url():
    """Base URL endpoint showing usage information"""
    current_time = get_ist_time()
    
    data = {
        "success": True,
        "timestamp": current_time,
        "credit": "sidverseapi",
        "message": "GST Details API is running",
        "usage": {
            "endpoint": "/gst/{pan_number}",
            "method": "GET",
            "example": "/gst/AACCG0527D",
            "full_url": f"{request.host_url}gst/AACCG0527D"
        }
    }
    
    return pretty_response(data, 200)

@app.route('/gst/<pan_number>', methods=['GET'])
def get_gst_details(pan_number):
    """Fetch GST details using PAN number"""
    try:
        # Clean and validate PAN number
        pan_number = pan_number.strip().upper()
        current_time = get_ist_time()
        
        # Make API call to MastersIndia GST API
        params = {"keyword": pan_number}
        
        response = requests.get(
            GST_API_URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code == 200:
            api_response = response.json()
            
            # Check if API returned success
            if api_response.get('success'):
                gst_data = api_response.get('data', [])
                
                # Format the response
                result = {
                    "pan": pan_number,
                    "success": True,
                    "timestamp": current_time,
                    "credit": "sidverseapi",
                    "total_gstins": len(gst_data),
                    "data": gst_data
                }
                
                return pretty_response(result, 200)
            else:
                data = {
                    "pan": pan_number,
                    "success": False,
                    "timestamp": current_time,
                    "credit": "sidverseapi",
                    "message": "No GST data found for this PAN"
                }
                return pretty_response(data, 404)
        else:
            data = {
                "pan": pan_number,
                "success": False,
                "timestamp": current_time,
                "credit": "sidverseapi",
                "message": f"NO DATA FOUND: {response.status_code}"
            }
            return pretty_response(data, response.status_code)
            
    except requests.exceptions.Timeout:
        current_time = get_ist_time()
        data = {
            "pan": pan_number,
            "success": False,
            "timestamp": current_time,
            "credit": "sidverseapi",
            "message": "Request timeout"
        }
        return pretty_response(data, 408)
        
    except requests.exceptions.RequestException as e:
        current_time = get_ist_time()
        data = {
            "pan": pan_number,
            "success": False,
            "timestamp": current_time,
            "credit": "sidverseapi",
            "message": f"Request failed: {str(e)}"
        }
        return pretty_response(data, 500)
        
    except Exception as e:
        current_time = get_ist_time()
        data = {
            "pan": pan_number,
            "success": False,
            "timestamp": current_time,
            "credit": "sidverseapi",
            "message": f"NO DATA FOUND: {str(e)}"
        }
        return pretty_response(data, 500)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    current_time = get_ist_time()
    
    data = {
        "success": False,
        "timestamp": current_time,
        "credit": "sidverseapi",
        "message": "Endpoint not found. Use /gst/{pan_number}",
        "usage": {
            "endpoint": "/gst/{pan_number}",
            "method": "GET",
            "example": "/gst/AACCG0527D",
            "full_url": f"{request.host_url}gst/AACCG0527D"
        }
    }
    
    return pretty_response(data, 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
