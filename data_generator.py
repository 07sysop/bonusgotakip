import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime

# ==========================================
# AYARLAR VE YARDIMCI FONKSİYONLAR
# ==========================================

def kategori_belirle(baslik):
    b = baslik.lower()
    
    def check(keywords):
        pattern = r'\b(' + '|'.join(keywords) + r')\b'
        return re.search(pattern, b) is not None

    if check(['akaryakıt', 'benzin', 'mazot', 'otogaz', 'petrol', 'opet', 'shell', 'bp', 'total', 'aygaz', 'mogaz', 'po', 'petrol ofisi', 'sunpet', 'lukoil']): return 'Akaryakıt'
    if check(['otomotiv', 'lastik', 'araç bakım', 'servis', 'otopark', 'bakım', 'onarım', 'birlas', 'euromaster', 'autogong', 'bridgestone', 'goodyear', 'lassa', 'michelin', 'continental', 'pirelli']): return 'Otomotiv'
    if check(['market', 'bakkal', 'süpermarket', 'migros', 'carrefour', 'a101', 'bim', 'şok', 'file', 'bizim toptan', 'gıda', 'metro market', 'metro toptancı', 'macrocenter', 'hakmar', 'happy center', 'onur market', 'altunbilekler', 'kim market']): return 'Market'
    if check(['giyim', 'tekstil', 'moda', 'ayakkabı', 'çanta', 'aksesuar', 'saat', 'gözlük', 'kuyum', 'altın', 'pırlanta', 'kozmetik', 'boyner', 'zara', 'lcw', 'lc waikiki', 'koton', 'mavi', 'gratis', 'watsons', 'flo', 'bershka', 'massimo dutti', 'oysho', 'pandora', 'stradivarius', 'lefties', 'pull&bear', 'nine west', 'desa', 'sportive', 'forever', 'sephora', "victoria's secret", 'in street', 'atasun', 'solaris', 'reebok', 'marks & spence', 'adl', 'decathlon', 'fenerium', 'jimmy key', 'under armour', 'vakko', 'vakkoroma', 'beymen', 'yargıcı', 'divarese', 'network', 'ipekyol', 'twist', 'ramsey', 'kip', 'bisse', 'gap', 'lumberjack', 'lacoste', 'gant', 'nautica', 'superstep', 'asics', 'skechers', 'klaud', 'brooks', 'penti', 'sneak up', 'mango', 'derimod', "d's", 'damat', 'pierre cardin', 'cacharel', 'avva', 'panço', 'panco', 'defacto', 'nike', 'lee', 'wrangler']): return 'Moda'
    if check(['elektronik', 'beyaz eşya', 'teknoloji', 'telefon', 'bilgisayar', 'tv', 'teknosa', 'mediamarkt', 'vatan', 'arçelik', 'beko', 'vestel', 'samsung', 'philips', 'dyson', 'troyestore', 'vaillant', 'itopya', 'monster', 'demirdöküm', 'incehesap', 'miele', 'gürgençler', 'bosch', 'siemens', 'kumtel', 'baymak', 'profilo', 'mitsubishi electric', 'alarko carrier']): return 'Elektronik'
    if check(['seyahat', 'gezi', 'turizm', 'tatil', 'otel', 'uçak', 'bilet', 'hava yolu', 'araç kiralama', 'rent a car', 'jolly', 'ets', 'turları', 'booking', 'avis', 'budget', 'türk hava yolları', 'thy', 'ajet', 'pegasus', 'europcar', 'yolcu360', 'sunexpress', 'corendon', 'enterprise', 'garenta']): return 'Seyahat'
    if check(['e-ticaret', 'online alışveriş', 'amazon', 'hepsiburada', 'trendyol', 'n11', 'pttavm', 'pazarama', 'çiçeksepeti', 'yemeksepeti', 'getir', 'morhipo']): return 'E-Ticaret'
    if check(['restoran', 'kafe', 'kafeterya', 'pastane', 'yemek', 'burger', 'pizza', 'kahve', 'starbucks', 'yeme', 'içme', 'köfteci', 'caribou coffee', 'espresso lab', 'nero', 'mcdonalds', 'burger king', 'kfc', 'dominos']): return 'Restoran'
    if check(['mobilya', 'dekorasyon', 'ev tekstili', 'yatak', 'baza', 'mutfak', 'ikea', 'kelebek', 'bellona', 'istikbal', 'yataş', 'doğtaş', 'vivense', 'koçtaş', 'bauhaus']): return 'Mobilya'
    if check(['eğitim', 'okul', 'kırtasiye', 'kitap', 'kurs', 'harç', 'üniversite', 'kolej', 'dr', 'd&r', 'nezih', 'kitapyurdu']): return 'Eğitim'
    if check(['vergi', 'fatura', 'mtv', 'sgk', 'trafik cezası', 'harç', 'belediye']): return 'Vergi'
    return 'Diğer'

def tarih_analiz_et(metin, api_end_date=None):
    if api_end_date:
        try:
            date_str = api_end_date.split("T")[0]
            fark = (datetime.strptime(date_str, "%Y-%m-%d") - datetime.now()).days + 1
            if fark < 0: return "SÜRESİ DOLDU"
            return f"SON {fark} GÜN"
        except: pass
    
    m = re.search(r'(\d{1,2})\s*([a-zA-ZğüşıöçĞÜŞİÖÇ]+)\s*[-–]\s*(\d{1,2})\s*([a-zA-ZğüşıöçĞÜŞİÖÇ]+)', metin)
    if m: return f"{m.group(1)} {m.group(2)} - {m.group(3)} {m.group(4)}"
    m = re.search(r'(\d{1,2})[-–](\d{1,2})\s*([a-zA-ZğüşıöçĞÜŞİÖÇ]+)', metin)
    if m: return f"{m.group(1)}-{m.group(2)} {m.group(3)}"
    return ""

def clean(text): return re.sub(r'\s+', ' ', text).strip() if text else ""

# ==========================================
# BANKA BOTLARI
# ==========================================

class BankkartBot:
    def __init__(self):
        self.api_url = "https://www.bankkart.com.tr/api/Campaigns/GetMoreShow"
        self.base_url = "https://www.bankkart.com.tr/kampanyalar/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bankkart.com.tr/kampanyalar",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }

    def get_image_from_detail(self, detail_url):
        try:
            detail_headers = {k:v for k,v in self.headers.items() if k != "X-Requested-With"}
            res = requests.get(detail_url, headers=detail_headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")
                meta_img = soup.find("meta", property="og:image")
                if meta_img and meta_img.get("content"):
                    return meta_img.get("content")
                img_div = soup.select_one(".campaign-detail-content img")
                if img_div and img_div.get("src"):
                    return "https://www.bankkart.com.tr" + img_div.get("src")
        except: pass
        return ""

    def scrape(self):
        data = []
        page_index = 1
        print("🚀 Bankkart verileri ve resimleri çekiliyor...")
        
        while True:
            params = {"indexNo": page_index, "type": "Bireysel"}
            try:
                response = requests.get(self.api_url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    json_data = response.json()
                    if isinstance(json_data, list): break
                    items = json_data.get("Items", [])
                    if not items: break
                    
                    for item in items:
                        title = clean(item.get("Title", ""))
                        seo_name = item.get("SeoName", "")
                        
                        cat_seo = item.get("Category", {}).get("SeoName", "")
                        if cat_seo and seo_name:
                            link = f"{self.base_url}{cat_seo}/{seo_name}"
                        else:
                            link = f"{self.base_url}genel-kampanyalar/{seo_name}"
                        
                        img_url = ""
                        if link:
                            img_url = self.get_image_from_detail(link)
                            
                        data.append({
                            "banka": "Bankkart",
                            "baslik": title,
                            "resim": img_url, 
                            "link": link,
                            "tarih_bilgisi": tarih_analiz_et(title, item.get("EndDate", "")),
                            "kategori": kategori_belirle(title)
                        })
                    
                    print(f"✅ Bankkart Sayfa {page_index} işlendi. ({len(items)} adet)")
                    page_index += 1
                    time.sleep(0.5) 
                else: break
            except Exception as e:
                print(f"⚠️ Bankkart hatası: {e}")
                break
        return data

class MaximumBot:
    def __init__(self):
        self.url = "https://www.maximum.com.tr/kampanyalar"
        self.base = "https://www.maximum.com.tr"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    def scrape(self):
        print("🚀 Maximum verileri çekiliyor...")
        try:
            res = requests.get(self.url, headers=self.headers, timeout=20)
            soup = BeautifulSoup(res.content, "html.parser")
            data = []
            for c in soup.select(".card"):
                h3 = c.find("h3", class_="card-text")
                if not h3: continue
                title = clean(h3.text)
                link = c.find("a").get("href", "")
                if link and not link.startswith("http"): link = self.base + link
                img_tag = c.find("img")
                src = ""
                if img_tag:
                    src = img_tag.get("data-src") or img_tag.get("src")
                    if src and not src.startswith("http"): src = self.base + src
                data.append({"banka": "Maximum", "baslik": title, "resim": src, "link": link, "tarih_bilgisi": tarih_analiz_et(title), "kategori": kategori_belirle(title)})
            return data
        except: return []

class ParafBot:
    def __init__(self):
        self.base = "https://www.paraf.com.tr"
        self.url = "https://www.paraf.com.tr/content/parafcard/tr/kampanyalar/_jcr_content/root/responsivegrid/filter.filtercampaigns.all.json"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    def scrape(self):
        print("🚀 Paraf verileri çekiliyor...")
        try:
            res = requests.get(self.url, headers=self.headers, timeout=15).json()
            data = []
            for i in res:
                title = clean(i.get("title", ""))
                link = i.get("url", "")
                if link: link = self.base + link + (".html" if not link.endswith(".html") else "")
                img = i.get("teaserImage", "")
                if img: img = self.base + img
                data.append({"banka": "Paraf", "baslik": title, "resim": img, "link": link, "tarih_bilgisi": tarih_analiz_et(title), "kategori": kategori_belirle(title)})
            return data
        except: return []

class WorldBot:
    def __init__(self):
        self.base = "https://www.worldcard.com.tr"
        self.api = "https://www.worldcard.com.tr/api/campaigns"
        self.sess = requests.Session()
        self.sess.headers.update({"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/json; charset=utf-8"})
    def scrape(self):
        print("🚀 World verileri çekiliyor...")
        data = []
        seen = set()
        params = {"campaignSectorKey": "tum-kampanyalar", "campaignSectorId": "6d897e71-1849-43a3-a64f-62840e8c0442", "campaignTypeId": "0", "keyword": ""}
        for p in range(1, 25):
            self.sess.headers.update({'page': str(p)})
            try:
                r = self.sess.get(self.api, params=params, timeout=10).json()
                items = r.get("Items", [])
                if not items: break
                new = 0
                for i in items:
                    t = i.get("Title", "").strip()
                    if t in seen: continue
                    seen.add(t)
                    new += 1
                    img = i.get("ImageUrl", "")
                    if img.startswith("/"): img = self.base + img
                    lnk = i.get("Url", "")
                    if lnk.startswith("/"): lnk = self.base + lnk
                    data.append({"banka": "World", "baslik": t, "resim": img, "link": lnk, "tarih_bilgisi": tarih_analiz_et(t, i.get("EndDate", "")), "kategori": kategori_belirle(t)})
                if new == 0: break
                time.sleep(0.1)
            except: break
        return data

class BonusBot:
    def __init__(self):
        self.url = "https://www.bonus.com.tr/kampanyalar"
        self.base = "https://www.bonus.com.tr"
        self.headers = {"User-Agent": "Mozilla/5.0"}
    def scrape(self):
        print("🚀 Bonus verileri çekiliyor...")
        try:
            soup = BeautifulSoup(requests.get(self.url, headers=self.headers, timeout=15).content, "html.parser")
            data = []
            for k in soup.select(".campaign-box__image-content"):
                try:
                    a = k.find_parent("a")
                    if not a: continue
                    t = clean(a.get_text())
                    lk = self.base + a.get("href")
                    i = k.find("img")
                    src = self.base + (i.get("data-src") or i.get("src")) if i else ""
                    data.append({"banka": "Bonus", "baslik": t, "resim": src, "link": lk, "tarih_bilgisi": tarih_analiz_et(t), "kategori": kategori_belirle(t)})
                except: continue
            return data
        except: return []

# ==========================================
# 3. HTML ÇIKTI OLUŞTURUCU (TEST)
# ==========================================
def generate_html_preview(json_data):
    json_str = json.dumps(json_data, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BonusGo Yerel Test</title>
    <link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap' rel='stylesheet'/>
    <style>
        :root {{
            --bg: #ffffff;
            --dark: #333;
            --bonus: #00974D;
            --max: #E52E88;
            --paraf: #00ADEF;
            --world: #6A1B9A;
            --bankkart: #E30613;
            --gray: #f4f6f8;
        }}
        body {{ font-family: 'Segoe UI', sans-serif; background-color: var(--gray); padding: 20px; }}
        
        .filters {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; font-family: 'Poppins', sans-serif; }}
        .btn {{ border: 1px solid #ddd; border-radius: 20px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; background: white; color: #666; transition: 0.2s; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn.active {{ color: white; border-color: transparent; }}
        
        .btn.all.active {{ background: var(--dark); }}
        .btn.Bonus.active {{ background: var(--bonus); }}
        .btn.Maximum.active {{ background: var(--max); }}
        .btn.Paraf.active {{ background: var(--paraf); }}
        .btn.World.active {{ background: var(--world); }}
        .btn.Bankkart.active {{ background: var(--bankkart); }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }}
        
        .card {{ background: white; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; border: 2px solid #eee; transition: 0.2s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }}
        
        .card.Maximum {{ border-color: var(--max); }}
        .card.Paraf {{ border-color: var(--paraf); }}
        .card.World {{ border-color: var(--world); }}
        .card.Bonus {{ border-color: var(--bonus); }}
        .card.Bankkart {{ border-color: var(--bankkart); }}
        
        .img-box {{ height: 140px; background: #eee; overflow: hidden; position: relative; }}
        .img-box img {{ width: 100%; height: 100%; object-fit: cover; }}
        
        .content {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
        
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; margin-bottom: 8px; }}
        .Maximum .badge {{ background: var(--max); }}
        .Paraf .badge {{ background: var(--paraf); }}
        .World .badge {{ background: var(--world); }}
        .Bonus .badge {{ background: var(--bonus); }}
        .Bankkart .badge {{ background: var(--bankkart); }}
        
        .title {{ font-size: 13px; font-weight: 600; color: var(--dark); margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.4; }}
        .date {{ text-align: center; font-size: 11px; font-weight: 700; color: #e74c3c; margin-bottom: 8px; min-height: 15px; }}
        
        .btn-detay {{ display: block; width: 100%; padding: 8px 0; color: white; text-align: center; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 12px; margin-top: auto; }}
        .card.Maximum .btn-detay {{ background: var(--max); }}
        .card.Paraf .btn-detay {{ background: var(--paraf); }}
        .card.World .btn-detay {{ background: var(--world); }}
        .card.Bonus .btn-detay {{ background: var(--bonus); }}
        .card.Bankkart .btn-detay {{ background: var(--bankkart); }}
        
        #loadMoreBtn {{
            padding: 12px 30px; background: var(--dark); color: white; border: none; border-radius: 25px;
            cursor: pointer; font-weight: 600; display: block; margin: 40px auto;
            font-family: 'Poppins', sans-serif; transition: background 0.3s;
        }}
        #loadMoreBtn:hover {{ background: #555; }}
        
    </style>
</head>
<body>
    <h2 style="text-align:center; font-family:'Poppins'">BonusGo Yerel Test</h2>
    
    <div class="filters bank-filters">
        <button class="btn all active" onclick="setBank('ALL')">TÜMÜ</button>
        <button class="btn Bonus" onclick="setBank('Bonus')">BONUS</button>
        <button class="btn Maximum" onclick="setBank('Maximum')">MAXIMUM</button>
        <button class="btn Paraf" onclick="setBank('Paraf')">PARAF</button>
        <button class="btn World" onclick="setBank('World')">WORLD</button>
        <button class="btn Bankkart" onclick="setBank('Bankkart')">BANKKART</button>
    </div>

    <div class="grid" id="grid"></div>
    <button id="loadMoreBtn" style="display:none">DAHA FAZLA GÖSTER</button>

    <script>
        const data = {json_str};
        let currentFiltered = [];
        let displayedCount = 0;
        const LOAD_LIMIT = 12;
        let currentBank = 'ALL';
        
        function init() {{
            const counts = {{'Bonus':0, 'Maximum':0, 'Paraf':0, 'World':0, 'Bankkart':0}};
            data.forEach(c => {{ if(counts[c.banka] !== undefined) counts[c.banka]++ }});
            
            Object.keys(counts).forEach(k => {{
                const el = document.querySelector(`.btn.${{k}}`);
                if(el) el.textContent = `${{k.toUpperCase()}} (${{counts[k]}})`;
            }});
            document.querySelector('.btn.all').textContent = `TÜMÜ (${{data.length}})`;
            
            document.getElementById('loadMoreBtn').addEventListener('click', renderChunk);
            setBank('ALL');
        }}
        
        window.setBank = (bank) => {{
            currentBank = bank;
            document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
            if(bank === 'ALL') document.querySelector('.btn.all').classList.add('active');
            else document.querySelector(`.btn.${{bank}}`).classList.add('active');
            
            currentFiltered = bank === 'ALL' ? data : data.filter(c => c.banka === bank);
            document.getElementById('grid').innerHTML = '';
            displayedCount = 0;
            renderChunk();
        }};
        
        function renderChunk() {{
            const chunk = currentFiltered.slice(displayedCount, displayedCount + LOAD_LIMIT);
            const grid = document.getElementById('grid');
            
            chunk.forEach(c => {{
                const card = document.createElement('div');
                card.className = `card ${{c.banka}}`;
                
                const imgUrl = (c.resim && c.resim.length > 5) ? c.resim : `https://via.placeholder.com/300x140?text=${{c.banka}}`;
                const dateHtml = c.tarih_bilgisi ? `<div class="date">${{c.tarih_bilgisi}}</div>` : '<div class="date" style="height:14px;"></div>';
                
                card.innerHTML = `
                    <div class="img-box"><img src="${{imgUrl}}" onerror="this.src='https://via.placeholder.com/300x140?text=ResimYok'"></div>
                    <div class="content">
                        <div><span class="badge">${{c.banka}}</span><div class="title">${{c.baslik}}</div></div>
                        <div>${{dateHtml}}<a href="${{c.link}}" target="_blank" class="btn-detay">DETAY</a></div>
                    </div>
                `;
                grid.appendChild(card);
            }});
            
            displayedCount += chunk.length;
            const btn = document.getElementById('loadMoreBtn');
            const remaining = currentFiltered.length - displayedCount;
            
            if (remaining > 0) {{
                btn.style.display = 'block';
                btn.textContent = `DAHA FAZLA GÖSTER (${{remaining}})`;
            }} else {{
                btn.style.display = 'none';
            }}
            
            if(currentFiltered.length === 0) {{
                 grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:#999;padding:20px;">Kayıt bulunamadı.</div>';
            }}
        }}
        
        init();
    </script>
</body>
</html>
    """
    with open("onizleme.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🌍 'onizleme.html' dosyası oluşturuldu.")

# ==========================================
# ANA ÇALIŞTIRMA BLOĞU
# ==========================================
if __name__ == "__main__":
    all_data = []
    
    all_data.extend(BankkartBot().scrape())
    all_data.extend(MaximumBot().scrape())
    all_data.extend(ParafBot().scrape())
    all_data.extend(WorldBot().scrape())
    all_data.extend(BonusBot().scrape())
    
    print(f"\n✅ Toplam {len(all_data)} kampanya bulundu.")
    
    with open("kampanyalar.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("📁 'kampanyalar.json' kaydedildi.")

    generate_html_preview(all_data)
