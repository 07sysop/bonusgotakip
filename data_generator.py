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
    if any(x in b for x in ['akaryakıt', 'benzin', 'mazot', 'otogaz', 'petrol', 'opet', 'shell', 'bp', 'total', 'aygaz', 'mogaz', 'po', 'petrol ofisi', 'sunpet', 'lukoil']): return 'Akaryakıt'
    if any(x in b for x in ['otomotiv', 'lastik', 'araç bakım', 'servis', 'otopark', 'bakım', 'onarım', 'birlas', 'euromaster', 'autogong', 'bridgestone', 'goodyear', 'lassa', 'michelin', 'continental', 'pirelli']): return 'Otomotiv'
    if any(x in b for x in ['market', 'bakkal', 'süpermarket', 'migros', 'carrefour', 'a101', 'bim', 'şok', 'file', 'bizim toptan', 'gıda', 'metro market', 'metro toptancı', 'macrocenter', 'hakmar', 'happy center', 'onur market', 'altunbilekler', 'kim market']): return 'Market'
    if any(x in b for x in ['giyim', 'tekstil', 'moda', 'ayakkabı', 'çanta', 'aksesuar', 'saat', 'gözlük', 'kuyum', 'altın', 'pırlanta', 'kozmetik', 'boyner', 'zara', 'lcw', 'lc waikiki', 'koton', 'mavi', 'gratis', 'watsons', 'flo', 'bershka', 'massimo dutti', 'oysho', 'pandora', 'stradivarius', 'lefties', 'pull&bear', 'nine west', 'desa', 'sportive', 'forever', 'sephora', "victoria's secret", 'in street', 'atasun', 'solaris', 'reebok', 'marks & spence', 'adl', 'decathlon', 'fenerium', 'jimmy key', 'under armour', 'vakko', 'vakkoroma', 'beymen', 'yargıcı', 'divarese', 'network', 'ipekyol', 'twist', 'ramsey', 'kip', 'bisse', 'gap', 'lumberjack', 'lacoste', 'gant', 'nautica', 'superstep', 'asics', 'skechers', 'klaud', 'brooks', 'penti', 'sneak up', 'mango', 'derimod', "d's", 'damat', 'pierre cardin', 'cacharel', 'avva', 'panço', 'panco', 'defacto', 'nike', 'lee', 'wrangler']): return 'Moda'
    if any(x in b for x in ['elektronik', 'beyaz eşya', 'teknoloji', 'telefon', 'bilgisayar', 'tv', 'teknosa', 'mediamarkt', 'vatan', 'arçelik', 'beko', 'vestel', 'samsung', 'philips', 'dyson', 'troyestore', 'vaillant', 'itopya', 'monster', 'demirdöküm', 'incehesap', 'miele', 'gürgençler', 'bosch', 'siemens', 'kumtel', 'baymak', 'profilo', 'mitsubishi electric', 'alarko carrier']): return 'Elektronik'
    if any(x in b for x in ['seyahat', 'gezi', 'turizm', 'tatil', 'otel', 'uçak', 'bilet', 'hava yolu', 'araç kiralama', 'rent a car', 'jolly', 'ets', 'turları', 'booking', 'avis', 'budget', 'türk hava yolları', 'thy', 'ajet', 'pegasus', 'europcar', 'yolcu360', 'sunexpress', 'corendon', 'enterprise', 'garenta']): return 'Seyahat'
    if any(x in b for x in ['e-ticaret', 'online alışveriş', 'amazon', 'hepsiburada', 'trendyol', 'n11', 'pttavm', 'pazarama', 'çiçeksepeti', 'yemeksepeti', 'getir', 'morhipo']): return 'E-Ticaret'
    if any(x in b for x in ['restoran', 'kafe', 'kafeterya', 'pastane', 'yemek', 'burger', 'pizza', 'kahve', 'starbucks', 'yeme', 'içme', 'köfteci', 'caribou coffee', 'espresso lab', 'nero', 'mcdonalds', 'burger king', 'kfc', 'dominos']): return 'Restoran'
    if any(x in b for x in ['mobilya', 'dekorasyon', 'ev tekstili', 'yatak', 'baza', 'mutfak', 'ikea', 'kelebek', 'bellona', 'istikbal', 'yataş', 'doğtaş', 'vivense', 'koçtaş', 'bauhaus']): return 'Mobilya'
    if any(x in b for x in ['eğitim', 'okul', 'kırtasiye', 'kitap', 'kurs', 'harç', 'üniversite', 'kolej', 'dr', 'd&r', 'nezih', 'kitapyurdu']): return 'Eğitim'
    if any(x in b for x in ['vergi', 'fatura', 'mtv', 'sgk', 'trafik cezası', 'harç', 'belediye']): return 'Vergi'
    return 'Diğer'

def tarih_analiz_et(metin, api_end_date=None):
    if api_end_date:
        try:
            # API tarihleri genelde ISO formatında gelir (örn: 2025-12-31T23:59:00)
            date_str = api_end_date.split("T")[0]
            fark = (datetime.strptime(date_str, "%Y-%m-%d") - datetime.now()).days + 1
            return "SÜRESİ DOLDU" if fark < 0 else f"SON {fark} GÜN"
        except: pass
    
    # Metin içi tarih analizi (Regex)
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bankkart.com.tr/kampanyalar",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }

    def scrape(self):
        data = []
        page_index = 1
        print("🚀 Bankkart verileri çekiliyor...")
        
        while True:
            params = {
                "indexNo": page_index,
                "CategoryId": "",
                "cuzdan": "",
                "arsiv": "",
                "type": "Bireysel"
            }

            try:
                response = requests.get(self.api_url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    json_data = response.json()
                    
                    # Liste kontrolü (Veri bitince API bazen boş liste döner)
                    if isinstance(json_data, list):
                        break
                    
                    items = json_data.get("Items", [])
                    if not items:
                        break
                    
                    for item in items:
                        title = clean(item.get("Title", ""))
                        seo_name = item.get("SeoName", "")
                        link = self.base_url + seo_name if seo_name else ""
                        end_date = item.get("EndDate", "")
                        
                        # Resim API'den direkt dönmüyor, boş bırakıyoruz veya SEO adından türetilebilir.
                        # Standart yapıya uyması için boş string geçiyoruz.
                        
                        data.append({
                            "banka": "Bankkart",
                            "baslik": title,
                            "resim": "", 
                            "link": link,
                            "tarih_bilgisi": tarih_analiz_et(title, end_date),
                            "kategori": kategori_belirle(title)
                        })
                    
                    page_index += 1
                    time.sleep(0.3)
                else:
                    break
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
                    if src and not src.startswith("http"):
                        src = self.base + src
                
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
# ANA ÇALIŞTIRMA BLOĞU
# ==========================================
if __name__ == "__main__":
    all_data = []
    
    # Tüm bankaları sırayla çalıştır
    all_data.extend(BankkartBot().scrape())
    all_data.extend(MaximumBot().scrape())
    all_data.extend(ParafBot().scrape())
    all_data.extend(WorldBot().scrape())
    all_data.extend(BonusBot().scrape())
    
    print(f"\n✅ Toplam {len(all_data)} kampanya bulundu ve kaydediliyor...")
    
    with open("kampanyalar.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        
    print("📁 'kampanyalar.json' dosyası başarıyla oluşturuldu.")
