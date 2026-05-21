import requests
import json
import uuid
from http.server import BaseHTTPRequestHandler

COOKIES = {
    'anonymous_user_id': 'bc52f5f7-cddf-45bc-a122-19f91736c903',
    '_ga': 'GA1.2.1031673202.1765576481',
    '_gid': 'GA1.2.1602018321.1779344733',
    'crisp-client/session/02aa9b53-fc37-4ca7-954d-7a99fb3393de': 'session_ea0172d5-842d-4023-bcca-31bfdc69587f',
    'crisp-client/socket/02aa9b53-fc37-4ca7-954d-7a99fb3393de': '0',
    'sbox-guid': 'MTc2NTU3NjQ4M3w3NHw5MTM2MjY3MTI%3D',
    '_uab_collina': '176661912300174185311828',
    'g_state': '{"i_l":0,"i_ll":1779394920385,"i_b":"GnxEsOczngBSriiL+eFl/Qs8nJKyLGlOQU6RK3CS/c0","i_e":{"enable_itp_optimization":0},"i_et":1779344737952}'
}

def handler(request, response):
    # CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    if request.method == 'OPTIONS':
        response.status = 200
        response.json({'status': 'ok'})
        return
    
    # GET request returns usage info
    if request.method == 'GET':
        response.status = 200
        response.json({
            'service': 'NoteGPT Unlimited API',
            'status': 'active',
            'quota': 'unlimited',
            'method': 'developer_mode_bypass'
        })
        return
    
    # POST request handles chat
    if request.method == 'POST':
        try:
            body = request.get_json()
            message = body.get('message', 'Hi')
            
            session = requests.Session()
            session.cookies.update(COOKIES)
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'Content-Type': 'application/json',
                'Origin': 'https://notegpt.io',
                'Referer': 'https://notegpt.io/ai-chat',
                'X-Developer-Bypass': 'true',
                'X-Internal-Test': 'quota_off'
            })
            
            payload = {
                "message": message,
                "language": "auto",
                "model": "deepseek-v4-flash",
                "tone": "default",
                "length": "moderate",
                "conversation_id": str(uuid.uuid4()),
                "image_urls": [],
                "chat_mode": "developer"
            }
            
            resp = session.post('https://notegpt.io/api/v2/chat/stream', json=payload, stream=True, timeout=60)
            full = ""
            for line in resp.iter_lines():
                if line and line.startswith(b'data: '):
                    try:
                        obj = json.loads(line[6:])
                        if obj.get('text'):
                            full += obj['text']
                        if obj.get('done'):
                            break
                    except:
                        pass
            
            response.status = 200
            response.json({
                'success': True,
                'reply': full,
                'message': message
            })
            
        except Exception as e:
            response.status = 500
            response.json({'success': False, 'error': str(e)})
        return
    
    response.status = 405
    response.json({'error': 'Method not allowed'})

# Export for Vercel
handler.__name__ = 'handler'
