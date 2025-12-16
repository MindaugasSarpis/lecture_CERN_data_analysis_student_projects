
from bs4 import BeautifulSoup
from urllib.parse import urlparse

MULTI_VALUE_FIELDS = [
    "peculiars",
    "extra_spaces",
    "extra_equipment",
    "window_orientation"
]
#galutiniu duomenu schema
SCHEMA = [
    "listing_id", "task_id", "category", "ext_date", "city", "hood", "street", "price" , "price_per_month","house_number","flat_number","rooms","area_sqm", "plot_area",
    "floor","floor_total","year_of_creation","interior","building_type", "house_type",
    "heating","peculiars","extra_spaces","extra_equipment","security",
    "window_orientation","building_energy_class","url",
    "entry_date","redacted_date","active_till_date",
    "favorited","views", "water", "distance_to_water", "closest_water"
]
#lauku zodynas
LT_EN_DICT = {
        "Kaina mėn.": "price_per_month",
        "Kambarių sk.": "rooms",
        "Plotas": "area_sqm",
        "Aukštas": "floor",
        "Aukštų sk.": "floor_total",
        "Metai" : "year_of_creation",
        "Įrengimas" : "interior",
        "Pastato tipas" : "building_type",
        "Šildymas" : "heating",
        "Ypatybės" : "peculiars",
        "Papildomos patalpos" : "extra_spaces",
        "Papildoma įranga" : "extra_equipment",
        "Apsauga" : "security",
        "Nuoroda" : "url",
        "Įvestas" : "entry_date",
        "Redaguotas" : "redacted_date",
        "Aktyvus iki" : "active_till_date",
        "Namo numeris" : "house_number",
        "Langų orientacija" : "window_orientation",
        "Įsiminė" : "favorited",
        "Peržiūrėjo" : "views",
        "Buto numeris": "flat_number",
        "Pastato energijos suvartojimo klasė": "building_energy_class",
        "Sklypo plotas" : "plot_area",
        "Namo tipas" : "house_type",
        "Vanduo" : "water",
        "Iki vandens telkinio (m)" : "distance_to_water",
        "Artimiausias vandens telkinys" : "closest_water"
    }


def translate_label(label, mapping):
    label = label.strip()
    if label in mapping:
        return mapping[label]
    else:
        with open("labels.txt", 'a') as f:
            f.write(f"No English key for label: {label}\n")
        return None
    
class Html_ext:
    def __init__(self):
        self.mvf = MULTI_VALUE_FIELDS
        self.schema = SCHEMA
        self.lten = LT_EN_DICT
    #is puslapio istraukia visu nuosavybiu nuorodas
    def ext_links(self, html):
        links = []
        seen = set()

        soup = BeautifulSoup(html, "html.parser")

        anchors = soup.find_all("a", class_="object-image-link-big_thumbs")
        for a in anchors:
            link = a.get("href")
            parsed = urlparse(link)
            unique_key = parsed.path
            
            #kadangi gali patekti vienodi url  kuriu kodas skirtingas mes naudojam raktus uztikrinti unkaluma
            if unique_key not in seen:
                seen.add(unique_key)
                links.append(a.get("href"))
        return links
    
    def ext_data_old(self, html):
    #tuscia skelbimo struktura
        listing = {k: None for k in self.schema}

        soup = BeautifulSoup(html, "html.parser")
        #istraukiama pagrindine informacija
        
        basic_info =  soup.select_one("div.advert-heading-col.title-col h1")
        price = soup.select_one(".main-price").get_text(strip=True)
        if basic_info:
            header = basic_info.get_text(strip=True)
            location = [x.strip() for x in header.split(",")]
            #print(f"{location} gauta info")
            #reikia sita sutvarkyti yra listingu kur nera rajono bet yra gatve kuri visada paskutine
            if len(location) == 3:
                listing["city"] = location[0]
                listing["hood"] = location[1]
                listing["street"] = location[2]
            elif len(location) == 2:
                listing["city"] = location[0]
                listing["street"] = location[1]


        extra_info = soup.select("dl > dt")
        for dt in extra_info:
            label = dt.get_text(strip=True)
            label = translate_label(label, self.lten)
            dd = dt.find_next_sibling("dd")
            if label in self.mvf:
                values = [span.get_text(strip=True) for span in dd.find_all("span")]
                value = ";".join(values)
            else:
                value = dd.get_text(strip=True)
            listing[label] = value
        return listing
    
    #sutvarkita funkcija
    def ext_data(self, html):
    #tuscia skelbimo struktura
        listing = {k: None for k in self.schema}

        soup = BeautifulSoup(html, "html.parser")
        #istraukiama pagrindine informacija
        
        basic_info =  soup.select("div.advert-heading-col.title-col h1")
        #print(f"skaicius headeriu{len(basic_info)}")

        #Yra pirmas reklaminis headeris coliving erdvem ir visokiem grupiniam pastatams
        if len(basic_info) > 1:
            basic_info = basic_info[1]
        else:
            basic_info = basic_info[0]

        price = soup.select_one(".main-price").get_text(strip=True)
        listing["price"] = price
        if basic_info:
            header = basic_info.get_text(strip=True)
            location = [x.strip() for x in header.split(",")]
            #print(f"{location} gauta info")
            #reikia sita sutvarkyti yra listingu kur nera rajono bet yra gatve kuri visada paskutine
            if len(location) == 3:
                listing["city"] = location[0]
                listing["hood"] = location[1]
                listing["street"] = location[2]
            elif len(location) == 2:
                listing["city"] = location[0]
                listing["street"] = location[1]


        extra_info = soup.select("dl > dt")
        for dt in extra_info:
            label = dt.get_text(strip=True)
            label = translate_label(label, self.lten)
            if label is None:      # ⬅ skip unknown fields safely
                continue
            dd = dt.find_next_sibling("dd")
            if label in self.mvf:
                values = [span.get_text(strip=True) for span in dd.find_all("span")]
                value = ";".join(values)
            else:
                value = dd.get_text(strip=True)
            listing[label] = value
        return listing
    


# def main():
#     h = Html_ext()

#     with open("aruodas_scrape/link_page.html", "r") as f:
#         html = f.read()
#         links = h.ext_links(html)
#         print(links)
#         for link in links:
#             print("Link ")
#             print(link)

#     with open("aruodas_scrape/listing.html", "r") as f:
#         html = f.read()
#         data = h.ext_data(html)
#         print(data)
        
# if __name__ == "__main__":
#     main()