import requests
import json

def check_main_token(token):
    """
    Kiểm tra token chính và lấy thông tin user/profile
    Trả về: (is_valid, user_id, user_name, profile_link)
    """
    url = "https://graph.facebook.com/me"
    params = {
        'access_token': token,
        'fields': 'id,name,link'  # Lấy id, tên và link profile
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'id' in data:
            user_id = data['id']
            user_name = data.get('name', 'Không có tên')
            profile_link = data.get('link', f"https://www.facebook.com/{user_id}")
            return True, user_id, user_name, profile_link
        else:
            error_msg = data.get('error', {}).get('message', 'Token không hợp lệ hoặc đã hết hạn')
            return False, None, None, error_msg
            
    except requests.exceptions.RequestException as e:
        return False, None, None, f"Lỗi kết nối: {e}"

def get_page_tokens(main_token):
    """
    Lấy danh sách các Page và Access Token của chúng
    """
    url = "https://graph.facebook.com/me/accounts"
    params = {
        'access_token': main_token
#        'fields': 'id,name,access_token,link'  # Thêm link của page
    }
    
    try:
        print("\n⏳ Đang tải danh sách Page...")
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'data' in data:
            if len(data['data']) == 0:
                print("\n⚠️ Token này không quản lý Page nào.")
                return
                
            print("\n" + "="*80)
            print(f"📋 DANH SÁCH PAGE (Tổng: {len(data['data'])} Page)")
            print("="*80)
            
            for idx, page in enumerate(data['data'], 1):
                page_name = page.get('name', 'Không có tên')
                page_id = page.get('id', 'Không có ID')
                page_token = page.get('access_token', 'Không có token')
                page_link = page.get('link', f"https://www.facebook.com/{page_id}")
                
                print(f"\n[{idx}] {page_name}")
                print(f"    ID: {page_id}")
                print(f"    Link: {page_link}")
                print(f"    TOKEN: {page_token}")
                print("-"*80)
                
            # Kiểm tra phân trang
            if 'paging' in data and 'next' in data['paging']:
                print("\n⚠️ Có nhiều hơn 100 Page. Cần xử lý thêm phần phân trang.")
        else:
            print("\n❌ Không thể lấy danh sách Page.")
            if 'error' in data:
                print(f"Lỗi: {data['error'].get('message', 'Chi tiết lỗi không rõ')}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
    except json.JSONDecodeError:
        print("❌ Lỗi: Dữ liệu trả về không phải định dạng JSON hợp lệ.")

def main():
    print("🔐 TOOL KIỂM TRA TOKEN & LẤY TOKEN TRANG FACEBOOK")
    print("="*60)
    
    # Nhập token
    main_token = input("\n👉 Nhập Token Account Chính: ").strip()
    
    if not main_token:
        print("❌ Bạn chưa nhập Token. Thoát chương trình.")
        return
    
    # Bước 1: Kiểm tra token chính
    print("\n" + "="*60)
    print("🔍 ĐANG KIỂM TRA TOKEN CHÍNH...")
    print("="*60)
    
    is_valid, user_id, user_name, profile_info = check_main_token(main_token)
    
    if not is_valid:
        print(f"\n❌ TOKEN KHÔNG HỢP LỆ!")
        print(f"   Lý do: {profile_info}")
        print("\n💡 Gợi ý:")
        print("   - Token có thể đã hết hạn")
        print("   - Token không có quyền truy cập thông tin cơ bản")
        print("   - Token bị thu hồi do đổi mật khẩu")
        return
    
    # In thông tin token hợp lệ
    print("\n✅ TOKEN HỢP LỆ!")
    print(f"   📝 Tên: {user_name}")
    print(f"   🆔 ID: {user_id}")
    print(f"   🔗 Profile Link: {profile_info}")
    
    # Bước 2: Lấy danh sách Page và token của chúng
    get_page_tokens(main_token)
    
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Người dùng đã dừng chương trình.")
    except Exception as e:
        print(f"\n❌ Lỗi không xác định: {e}")
