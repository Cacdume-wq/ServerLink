# up.py
import requests
import re
import json
import uuid
from io import BytesIO
import os
import time
from datetime import datetime

# Màu sắc cho terminal
green = '\033[92m'
red = '\033[91m'
yellow = '\033[93m'
blue = '\033[94m'
reset = '\033[0m'
bold = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def debug_print(*args):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}]", *args)

def print_banner():
    clear_screen()
    

def facebook_info(cookie: str, timeout: int = 15):
    try:
        session = requests.Session()
        session_id = str(uuid.uuid4())
        fb_dtsg = ""
        jazoest = ""
        lsd = ""
        name = ""
        user_id = cookie.split("c_user=")[1].split(";")[0]

        headers = {
            "authority": "www.facebook.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "vi",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "viewport-width": "1366",
            "Cookie": cookie
        }

        url = session.get(f"https://www.facebook.com/{user_id}", headers=headers, timeout=timeout).url
        response = session.get(url, headers=headers, timeout=timeout).text

        fb_token = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
        if fb_token:
            fb_dtsg = fb_token[0]

        jazo = re.findall(r'jazoest=(.*?)\"', response)
        if jazo:
            jazoest = jazo[0]

        lsd_match = re.findall(r'"LSD",\[\],\{"token":"(.*?)"\}', response)
        if lsd_match:
            lsd = lsd_match[0]

        get = session.get("https://www.facebook.com/me", headers=headers, timeout=timeout).url
        url = "https://www.facebook.com/" + get.split("%2F")[-2] + "/" if "next=" in get else get
        response = session.get(url, headers=headers, params={"locale": "vi_VN"}, timeout=timeout)

        data_split = response.text.split('"CurrentUserInitialData",[],{')
        json_data_raw = "{" + data_split[1].split("},")[0] + "}"
        parsed_data = json.loads(json_data_raw)

        user_id = parsed_data.get("USER_ID", "0")
        name = parsed_data.get("NAME", "")

        if user_id == "0" and name == "":
            print(f"{red}[!] Cookie is invalid or expired.{reset}")
            return {'success': False}
        elif "828281030927956" in response.text:
            print(f"{red}[!] Account is under a 956 checkpoint.{reset}")
            return {'success': False}
        elif "1501092823525282" in response.text:
            print(f"{red}[!] Account is under a 282 checkpoint.{reset}")
            return {'success': False}
        elif "601051028565049" in response.text:
            print(f"{red}[!] Account action is blocked (spam).{reset}")
            return {'success': False}

        json_data = {
            'success': True,
            'user_id': user_id,
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'lsd': lsd,
            'name': name,
            'session': session,
            'session_id': session_id,
            'cookie': cookie,
            'headers': headers
        }
        print(f"{green}✓ Đăng nhập thành công!{reset}")
        print(f"{blue}📱 Tên: {name}{reset}")
        print(f"{blue}🆔 ID: {user_id}{reset}")
        return json_data
        
    except Exception as e:
        debug_print("Lỗi trong facebook_info:", str(e))
        return {'success': False}

class ApiClient:
    def __init__(self, cookie):
        self.cookie = cookie
        info = facebook_info(cookie)
        
        if not info.get('success'):
            self.idfb = None
            self.name = None
            self.jazoest = None
            self.fb_dtsg = None
            self.session = requests.Session()
            self.headers = {}
        else:
            self.idfb = info.get('user_id')
            self.name = info.get('name')
            self.jazoest = info.get('jazoest')
            self.fb_dtsg = info.get('fb_dtsg')
            self.session = info.get('session')
            self.session_id = info.get('session_id')
            self.headers = info.get('headers')
    
    def upload(self, linkanh, caption=""):
        try:
            debug_print(f"📤 Đang upload ảnh: {linkanh}")
            img_data = requests.get(linkanh, timeout=30).content
            debug_print(f"✓ Đã tải ảnh, kích thước: {len(img_data)} bytes")
            
            params = {
                'profile_id': self.idfb, 
                '__a': '1', 
                'fb_dtsg': self.fb_dtsg, 
                'jazoest': self.jazoest
            }
            
            ext = linkanh.split('.')[-1].lower()
            if ext == 'jpg':
                ext = 'jpeg'
            mime = f'image/{ext}'
            
            files = {
                'file': ('random_image.' + ext, BytesIO(img_data), mime)
            }
            
            res = self.session.post(
                'https://www.facebook.com/profile/picture/upload/', 
                params=params, 
                headers=self.headers, 
                files=files,
                timeout=30
            ).text
            
            if '{"fbid":"' in res:
                fbid = res.split('{"fbid":"')[1].split('"')[0]
                debug_print(f"✓ Upload thành công, ID: {fbid}")
                return fbid
            else:
                debug_print("❌ Upload thất bại: Không tìm thấy fbid")
                return False
        except Exception as e:
            debug_print("❌ Lỗi upload:", str(e))
            return False

    def UpAvt(self, idavt, caption=""):
        try:
            debug_print("📸 Đang cập nhật avatar...")
            data = {
                'av': self.idfb,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'ProfileCometProfilePictureSetMutation',
                'variables': f'{{"input":{{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,via_cold_start,1721296676721,110519,190055527696468,,","caption":"{caption}","existing_photo_id":"{idavt}","expiration_time":null,"profile_id":"{self.idfb}","profile_pic_method":"EXISTING","profile_pic_source":"TIMELINE","scaled_crop_rect":{{"height":0.99999,"width":0.99999,"x":0,"y":0}},"skip_cropping":true,"actor_id":"{self.idfb}","client_mutation_id":"1"}},"isPage":false,"isProfile":true,"sectionToken":"UNKNOWN","collectionToken":"UNKNOWN","scale":1,"__relay_internal__pv__ProfileGeminiIsCoinFlipEnabledrelayprovider":false}}',
                'server_timestamps': 'true',
                'doc_id': '8252641828081928',
            }
            
            rq = self.session.post(
                'https://www.facebook.com/api/graphql/', 
                headers=self.headers, 
                data=data,
                timeout=30
            ).text
            
            if '{"data":{"profile_picture_set":{"profile":{"__typename":"User","id":"' in rq:
                debug_print("✓ Avatar đã được cập nhật thành công!")
                return True
            else:
                debug_print("❌ Cập nhật avatar thất bại")
                return False
        except Exception as e:
            debug_print("❌ Lỗi cập nhật avatar:", str(e))
            return False
            
    def UpCover(self, idavt, caption=""):
        try:
            debug_print(" Đang cập nhật bìa...")
            data = {
                'av': self.idfb,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'ProfileCometCoverPhotoUpdateMutation',
                'variables': f'{{"input":{{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,via_cold_start,1753753183176,88451,190055527696468,,","cover_photo_id":"{idavt}","focus":{{"x":0.5,"y":0.49999998393811673}},"target_user_id":"{self.idfb}","actor_id":"{self.idfb}","client_mutation_id":"1"}},"scale":1,"contextualProfileContext":null}}',
                'server_timestamps': 'true',
                'doc_id': '31388044007461211',
            }

            rq = self.session.post(
                'https://www.facebook.com/api/graphql/', 
                headers=self.headers, 
                data=data,
                timeout=30
            ).text
            
            if '{"data":{"user_update_cover_photo":{"user":{"name":"' in rq:
                debug_print("✓ Bìa đã được cập nhật thành công!")
                return True
            else:
                debug_print("❌ Cập nhật bìa thất bại")
                return False
        except Exception as e:
            debug_print("❌ Lỗi cập nhật bìa:", str(e))
            return False

def main():
    print_banner()
    
    # Nhập thông tin
    print(f"{yellow}📌 VUI LÒNG NHẬP THÔNG TIN:{reset}")
    print(f"{blue}{'='*50}{reset}")
    
    cookie = input(f"{yellow}[1] Cookie: {reset}").strip()
    if not cookie:
        print(f"{red}❌ Cookie không được để trống!{reset}")
        return
    
    avatar_link = input(f"{yellow}[2] Link ảnh Avatar: {reset}").strip()
    if not avatar_link:
        print(f"{red}❌ Link ảnh avatar không được để trống!{reset}")
        return
    
    cover_link = input(f"{yellow}[3] Link ảnh Bìa: {reset}").strip()
    if not cover_link:
        print(f"{red}❌ Link ảnh bìa không được để trống!{reset}")
        return
    
    caption = input(f"{yellow}[4] Caption (tùy chọn, nhấn Enter để bỏ qua): {reset}").strip()
    try:
        # Khởi tạo API client
        api = ApiClient(cookie)
        
        if not api.idfb:
            print(f"{red} Không thể đăng nhập. Vui lòng kiểm tra cookie!{reset}")
            return
        
        print(f"{green}✓ Đăng nhập thành công với tài khoản: {api.name}{reset}")
        print(f"{green}✓ Bắt đầu cập nhật avatar và bìa...{reset}\n")
        
        # Upload avatar
        avt_id = api.upload(avatar_link, caption)
        if not avt_id:
            print(f"{red} Không thể upload ảnh avatar!{reset}")
            return
        
        # Upload cover
        cover_id = api.upload(cover_link, caption)
        if not cover_id:
            print(f"{red} Không thể upload ảnh bìa!{reset}")
            return
        
        # Kết quả
        result_avt = api.UpAvt(avt_id, caption)
        result_cover = api.UpCover(cover_id, caption)
        
        print(f"\n{blue}{'='*50}{reset}")
        
        if result_avt and result_cover:
            print(f"{green}{bold} SUCCESS: ĐÃ UP AVT + BÌA THÀNH CÔNG!{reset}")
        elif not result_avt and not result_cover:
            print(f"{red}{bold} FAIL FULL: KHÔNG THỂ UP AVT + BÌA{reset}")
        elif not result_avt and result_cover:
            print(f"{yellow}{bold} FAIL AVT: ĐÃ UP BÌA NHƯNG AVT KHÔNG UP ĐƯỢC{reset}")
        elif result_avt and not result_cover:
            print(f"{yellow}{bold} FAIL BÌA: ĐÃ UP AVT NHƯNG BÌA KHÔNG UP ĐƯỢC{reset}")
        
    except Exception as e:
        debug_print("❌ Lỗi:", str(e))
        print(f"{red}❌ Có lỗi xảy ra trong quá trình xử lý!{reset}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{yellow}⚠️ Đã hủy chương trình!{reset}")
    except Exception as e:
        print(f"{red}❌ Lỗi không xác định: {e}{reset}")