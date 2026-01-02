import requests
import json
import os
from datetime import datetime
import time


WEATHER_URL = "https://open-meteo.com/en/docs?hourly=&latitude=52.520001&longitude=13.410001&current=temperature_2m,is_day,wind_speed_10m,wind_direction_10m,weather_code"
RETRIES = 3
RETRY_CODES = [
    429, # TOO_MANY_REQUESTS
    500, #  INTERNAL_SERVER_ERROR
    502, # BAD_GATEWAY,
    503, # SERVICE_UNAVAILABLE
    504, # GATEWAY_TIMEOUT
]

PARIS_ARRONDISSEMENTS = (
    (48.8625, 2.2875, "1er"),
    (48.8656, 2.3422, "2e"),
    (48.8684, 2.3490, "3e"),
    (48.8606, 2.3622, "4e"),
    (48.8546, 2.3750, "5e"),
    (48.8422, 2.3500, "6e"),
    (48.8350, 2.3211, "7e"),
    (48.8789, 2.3125, "8e"),
    (48.8764, 2.3311, "9e"),
    (48.8867, 2.3431, "10e"),
    (48.8719, 2.3667, "11e"),
    (48.8566, 2.3794, "12e"),
    (48.8244, 2.3600, "13e"),
    (48.8281, 2.3400, "14e"),
    (48.8325, 2.3100, "15e"),
    (48.9019, 2.3083, "16e"),
    (48.8950, 2.3200, "17e"),
    (48.8861, 2.3700, "18e"),
    (48.8850, 2.4000, "19e"),
    (48.8744, 2.4100, "20e"),
)

COMMUNE_COORDS = (
    #  (48.86018924132697, 2.343754739899097, "Paris"), # Not used bc we have arrondissements
    (48.910739591375574, 2.381001197922404, "Aubervilliers"),
    (48.83492373554233, 2.2406308198105607, "Boulogne-Billancourt"),
    (48.907241006602995, 2.4466627352231165, "Bobigny"),
    (48.823318606259996, 2.4058189234193947, "Charenton-le-Pont"),
    (48.84728224080477, 2.4362137010806055, "Vincennes"),
    (48.79702105058296, 2.312270259157995, "Bagneux"),
    (48.78856978131531, 2.3928041334185566, "Vitry-sur-Seine"),
    (48.78357322981106, 2.457536040718331, "Créteil"),
    (48.79091412961593, 2.361583716703601, "Villejuif"),
    (48.8241686703982, 2.2655242942778773, "Issy-les-Moulineaux"),
    (48.94779052455933, 2.242807255777806, "Argenteuil"),
    (48.915469562263006, 2.290485477680803, "Asnières-sur-Seine"),
    (48.8929956304761, 2.2090994485092024, "Nanterre"),
    (48.817946965465744, 2.5078573748125708, "Champigny-sur-Marne"),
    (48.86075664795748, 2.4379702338694242, "Montreuil"),
    (48.83585455528355, 2.483586892435502, "Nogent-sur-Marne"),
    (48.8853338192091, 2.4078145813853062, "Le Pré-Saint-Gervais"),
    (48.811126269101614, 2.359313964843758, "Le Kremlin-Bicêtre"),
    (48.8138919295751, 2.386242217199632, "Ivry-sur-Seine"),
    (48.89716714859252, 2.4081247299078243, "Pantin"),
    (48.87474098608689, 2.1847799121770235, "Rueil-Malmaison"),
    (48.81945980015803, 2.3020433077620166, "Malakoff"),
    (48.893327828388166, 2.2878801703493172, "Levallois-Perret"),
    (48.82171431345048, 2.2894208190655, "Vanves"),
    (48.88469415459622, 2.267713903763469, "Neuilly-sur-Seine"),
    (48.76758510779692, 2.4083393812179437, "Choisy-le-Roi"),
    (48.92742663343053, 2.357858744899814, "Saint-Denis"),
    (48.801566843457856, 2.422035698602648, "Alfortville"),
    (48.92719422685667, 2.3914155547515, "La Courneuve"),
    (48.883139311261736, 2.240030316114091, "Puteaux"),
    (48.84126107948734, 2.418280538070361, "Saint-Mandé"),
    (48.80642003848464, 2.3317663781633295, "Arcueil"),
    (48.907591799644194, 2.2448421453470533, "La Garenne-Colombes"),
    (48.921504986291545, 2.246920144778286, "Colombes"),
    (48.86960224085198, 2.221320239162874, "Suresnes"),
    (48.844587116454605, 2.18777829123576, "Garches"),
    (48.868578262268024, 2.419474781490851, "Bagnolet"),
    (48.850873824412226, 2.4713615127411583, "Fontenay-sous-Bois"),
    (48.907695580651605, 2.334371081824578, "Saint-Ouen-sur-Seine"),
    (48.781349275430834, 2.2910302703089998, "Sceaux"),
    (48.880024556088976, 2.4183701835163385, "Les Lilas"),
    (48.778949695386906, 2.314436630707188, "Bourg-la-Reine"),
    (48.90295528911043, 2.307324834914607, "Clichy"),
    (48.81565297301805, 2.3180615439749372, "Montrouge"),
    (48.8106718780591, 2.2361337791806246, "Meudon"),
    (48.82237552197236, 2.2117311401088258, "Sèvres"),
    (48.85212972125408, 2.219544441744995, "Saint-Cloud"),
    (48.79003205492572, 2.33164733089149, "Cachan"),
    (48.79113630377592, 2.2872599714282478, "Fontenay-aux-Roses"),
    (48.8814625527214, 2.439162401943216, "Romainville"),
    (48.81335498578116, 2.3418669838352466, "Gentilly"),
    (48.80502251373242, 2.436781103239848, "Maisons-Alfort"),
    (48.818453982638765, 2.4335912911806425, "Saint-Maurice"),
    (48.7990088417526, 2.2589135356787495, "Clamart"),
    (48.7616085724035, 2.39815236061945, "Thiais"),
    (48.929651571905104, 2.2981717358976397, "Gennevilliers"),
    (48.900450848176085, 2.260499945539382, "Courbevoie"),
    (48.819970772485505, 2.4690916383384502, "Joinville-le-Pont"),
    (48.80359986093131, 2.2887187694035407, "Châtillon"),
    (48.826073335699, 2.1894485725692, "Ville-d'Avray"),
    (48.8728903200868, 2.490847064182167, "Rosny-sous-Bois"),
    (48.89994040289543, 2.4617817473939194, "Noisy-le-Sec"),
    (48.80889642194803, 2.189528793096553, "Chaville"),
    (48.934296670484, 2.3283150821606333, "Villeneuve-la-Garenne"),
    (48.935421446598, 2.3408389473018, "L'Île-Saint-Denis"),
    (48.9189893870885, 2.27003273514055, "Bois-Colombes")
)

def fetch_weather_for_points():
    results = []

    print("Fetching weather data...", flush=True)
    counter = 0
    length = len(COMMUNE_COORDS) + len(PARIS_ARRONDISSEMENTS)
    for (lat, lon, label) in (COMMUNE_COORDS + PARIS_ARRONDISSEMENTS):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,is_day,wind_speed_10m,wind_direction_10m,weather_code"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            meteo = r.json().get("current", {})
            results.append({
                "arrondissement": label,
                "latitude": lat,
                "longitude": lon,
                "weather": meteo
            })
            counter += 1
            print(f"[{counter:4}/{length}] {label:25} OK", end="\r")
            time.sleep(0.5)  # to avoid hitting rate limits

        except Exception as e:
            print(f"EXCEPTION {label}: {e}", flush=True)

    folder = "../data/00_raw/json/weather_data_json"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved weather data for {len(results)} locations to {filename}.", flush=True)
    return filename, results

"""
if __name__ == "__main__":
    fetch_weather_for_points()
"""
