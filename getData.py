import requests
import os

API_URL = "https://vi.wikipedia.org/w/api.php"
data_file = r'C:\Users\Admin\Desktop\Chatbot mon data\data'

# Danh sách thể loại ban đầu cần quét
initial_categories = [
    {'title': 'Thể loại:Tai mũi họng', 'pageid': 16708},
    {'title': 'Thể loại:Tâm thần học', 'pageid': 181778},
    {'title': 'Thể loại:Thang điểm y khoa', 'pageid': 2062465},
    {'title': 'Thể loại:Thận học', 'pageid': 3049456},
    {'title': 'Thể loại:Thần kinh học', 'pageid': 1149238},
    {'title': 'Thể loại:Thiết bị y khoa', 'pageid': 495029},
    {'title': 'Thể loại:Thú y', 'pageid': 2185698},
    {'title': 'Thể loại:Thuật ngữ y học', 'pageid': 1210352},
    {'title': 'Thể loại:Tim mạch học', 'pageid': 679264},
    {'title': 'Thể loại:Tôn giáo và y học', 'pageid': 1830790},
    {'title': 'Thể loại:Triệu chứng', 'pageid': 12430484},
    {'title': 'Thể loại:Bệnh truyền nhiễm', 'pageid': 344347},
    {'title': 'Thể loại:Ung thư học', 'pageid': 350593},
    {'title': 'Thể loại:Vắc-xin', 'pageid': 1067841}
]

# Hàm lấy danh sách các trang và danh sách các thể loại
def extract_pages(category_name):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmtype": "page|subcat",
        "cmlimit": "max",
        "format": "json"
    }
    
    response = requests.get(API_URL, params=params)
    data = response.json()
    
    category_members = data.get('query', {}).get('categorymembers', [])
    subcategories = []
    pages = []

    for member in category_members:
        if member['title'].startswith("Thể loại:"):
            subcategories.append({'title': member['title'], 'pageid': member['pageid']})
        else:
            pages.append({'title': member['title'], 'pageid': member['pageid']})

    return {"subcategories": subcategories, "pages": pages}

# Hàm lấy nội dung của một trang
def get_page_content(page_id):
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "pageids": page_id,
        "format": "json"
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    pages = data.get('query', {}).get('pages', {})
    for page_id, page in pages.items():
        return page.get('extract', '')

# Hàm kiểm tra xem đã lưu thông tin hay chưa
def is_saved(saved_items, item_id):
    return item_id in saved_items

# Hàm lấy nội dung trong các trang của 1 thể loại
def get_all_content(category_name, category_id, depth, max_depth, parent_folder, saved_items, structure_file):
    if depth > max_depth:
        return

    ep = extract_pages(category_name)
    pages = ep['pages']
    subcategories = ep['subcategories']

    category_folder = os.path.join(parent_folder, str(category_id))
    
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    # Ghi vào file structure
    if not is_saved(saved_items, category_id):
        with open(structure_file, 'a', encoding='utf-8') as f:
            f.write('\t' * depth + f"{category_id}//{category_name}\n")
            # f.write('\t' * depth + f"{category_id}//{category_name.replace('Thể loại:', '').strip()}\n")
        saved_items.add(category_id)

    for page in pages:
        if not is_saved(saved_items, page['pageid']):
            with open(os.path.join(category_folder, f"{page['pageid']}.txt"), 'w', encoding='utf-8') as f:
                f.write(get_page_content(page['pageid']))
            with open(structure_file, 'a', encoding='utf-8') as f:
                f.write('\t' * (depth + 1) + f"{page['pageid']}//{page['title']}\n")
            saved_items.add(page['pageid'])

    print(f"Saved {len(pages)} pages in category {category_name}")
    
    for subcategory in subcategories:
        get_all_content(subcategory['title'], subcategory['pageid'], depth + 1, max_depth, category_folder, saved_items, structure_file)

# Chạy chương trình với độ sâu tối đa là 2
structure_file = r'C:\Users\Admin\Desktop\Chatbot mon data\data\structure.txt'
saved_items = set()
# Xóa nội dung file trước khi bắt đầu
with open(structure_file, 'w', encoding='utf-8') as f:
    f.write("")

for initial_category in initial_categories:
    get_all_content(initial_category['title'], initial_category['pageid'], 0, 2, data_file, saved_items, structure_file)
