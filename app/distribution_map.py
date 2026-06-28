from typing import Any

COUNTRY_NAME_TO_ALPHA3: dict[str, str] = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Angola": "AGO",
    "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT",
    "Azerbaijan": "AZE", "Bahamas": "BHS", "Bahrain": "BHR", "Bangladesh": "BGD",
    "Belarus": "BLR", "Belgium": "BEL", "Belize": "BLZ", "Benin": "BEN",
    "Bhutan": "BTN", "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH", "Botswana": "BWA",
    "Brazil": "BRA", "Brunei": "BRN", "Bulgaria": "BGR", "Burkina Faso": "BFA",
    "Burundi": "BDI", "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Cape Verde": "CPV", "Central African Republic": "CAF", "Chad": "TCD", "Chile": "CHL",
    "China": "CHN", "Colombia": "COL", "Comoros": "COM", "Congo": "COG",
    "Costa Rica": "CRI", "Croatia": "HRV", "Cuba": "CUB", "Cyprus": "CYP",
    "Czechia": "CZE", "Czechoslovakia": "CZE",
    "Democratic Republic of the Congo": "COD", "Denmark": "DNK", "Djibouti": "DJI",
    "Dominican Republic": "DOM", "East Timor": "TLS", "Ecuador": "ECU", "Egypt": "EGY",
    "El Salvador": "SLV", "Equatorial Guinea": "GNQ", "Eritrea": "ERI", "Estonia": "EST",
    "Eswatini": "SWZ", "Ethiopia": "ETH", "Fiji": "FJI", "Finland": "FIN",
    "France": "FRA", "Gabon": "GAB", "Gambia": "GMB", "Georgia": "GEO", "Germany": "DEU",
    "Ghana": "GHA", "Great Britain": "GBR", "Greece": "GRC", "Guatemala": "GTM",
    "Guinea": "GIN", "Guinea-Bissau": "GNB", "Guyana": "GUY", "Haiti": "HTI",
    "Honduras": "HND", "Hungary": "HUN", "Iceland": "ISL", "India": "IND",
    "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL", "Israel": "ISR",
    "Italy": "ITA", "Ivory Coast": "CIV", "Jamaica": "JAM", "Japan": "JPN",
    "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN", "Kuwait": "KWT",
    "Kyrgyzstan": "KGZ", "Laos": "LAO", "Latvia": "LVA", "Lebanon": "LBN",
    "Lesotho": "LSO", "Liberia": "LBR", "Libya": "LBY", "Lithuania": "LTU",
    "Luxembourg": "LUX", "Madagascar": "MDG", "Malawi": "MWI", "Malaysia": "MYS",
    "Maldives": "MDV", "Mali": "MLI", "Mauritania": "MRT", "Mauritius": "MUS",
    "Mexico": "MEX", "Moldova": "MDA", "Mongolia": "MNG", "Montenegro": "MNE",
    "Morocco": "MAR", "Mozambique": "MOZ", "Myanmar": "MMR", "Namibia": "NAM",
    "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL", "Nicaragua": "NIC",
    "Niger": "NER", "Nigeria": "NGA", "North Korea": "PRK", "North Macedonia": "MKD",
    "Norway": "NOR", "Oman": "OMN", "Pakistan": "PAK", "Panama": "PAN",
    "Papua New Guinea": "PNG", "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL",
    "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT", "Romania": "ROU", "Russia": "RUS",
    "Rwanda": "RWA", "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
    "Sierra Leone": "SLE", "Singapore": "SGP", "Slovakia": "SVK", "Slovenia": "SVN",
    "Somalia": "SOM", "South Africa": "ZAF", "South Korea": "KOR", "South Sudan": "SSD",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN", "Suriname": "SUR",
    "Sweden": "SWE", "Switzerland": "CHE", "Syria": "SYR", "Taiwan": "TWN",
    "Tajikistan": "TJK", "Tanzania": "TZA", "Thailand": "THA", "Togo": "TGO",
    "Trinidad and Tobago": "TTO", "Tunisia": "TUN", "Turkey": "TUR",
    "Turkmenistan": "TKM", "Uganda": "UGA", "Ukraine": "UKR",
    "United Arab Emirates": "ARE", "United Kingdom": "GBR", "United States": "USA",
    "Uruguay": "URY", "Uzbekistan": "UZB", "Venezuela": "VEN", "Vietnam": "VNM",
    "Yemen": "YEM", "Zambia": "ZMB", "Zimbabwe": "ZWE",
}

EXACT_TREFLE_TO_ALPHA3: dict[str, str] = {
    "Alabama": "USA", "Alaska": "USA", "Arizona": "USA", "Arkansas": "USA",
    "California": "USA", "Colorado": "USA", "Connecticut": "USA", "Delaware": "USA",
    "Florida": "USA", "Georgia": "USA", "Hawaii": "USA", "Idaho": "USA", "Illinois": "USA",
    "Indiana": "USA", "Iowa": "USA", "Kansas": "USA", "Kentucky": "USA", "Louisiana": "USA",
    "Maine": "USA", "Maryland": "USA", "Massachusetts": "USA", "Michigan": "USA",
    "Minnesota": "USA", "Mississippi": "USA", "Missouri": "USA", "Montana": "USA",
    "Nebraska": "USA", "Nevada": "USA", "New Hampshire": "USA", "New Jersey": "USA",
    "New Mexico": "USA", "New York": "USA", "North Carolina": "USA", "North Dakota": "USA",
    "Ohio": "USA", "Oklahoma": "USA", "Oregon": "USA", "Pennsylvania": "USA",
    "Rhode Island": "USA", "South Carolina": "USA", "South Dakota": "USA", "Tennessee": "USA",
    "Texas": "USA", "Utah": "USA", "Vermont": "USA", "Virginia": "USA", "Washington": "USA",
    "West Virginia": "USA", "Wisconsin": "USA", "Wyoming": "USA",
    "Baleares": "ESP", "Canary Is.": "ESP", "Corse": "FRA", "Sardegna": "ITA",
    "Sicilia": "ITA", "Korea": "KOR", "Tristan da Cunha": "SHN",
    "Greenland": "GRL", "Puerto Rico": "PRI", "Haiti": "HTI", "Jamaica": "JAM",
    "New South Wales": "AUS", "Queensland": "AUS", "South Australia": "AUS",
    "Tasmania": "AUS", "Victoria": "AUS", "Western Australia": "AUS",
}

PREFIX_TREFLE_TO_ALPHA3: list[tuple[str, str]] = sorted(
    [
        ("Mexico", "MEX"), ("Argentina", "ARG"), ("Australia", "AUS"), ("Brazil", "BRA"),
        ("China", "CHN"), ("India", "IND"), ("Russia", "RUS"), ("New Zealand", "NZL"),
        ("Japan", "JPN"), ("Indonesia", "IDN"), ("Colombia", "COL"), ("Chile", "CHL"),
        ("Peru", "PER"), ("Ecuador", "ECU"), ("Venezuela", "VEN"), ("Bolivia", "BOL"),
        ("Paraguay", "PRY"), ("Guyana", "GUY"), ("Suriname", "SUR"),
        ("South Africa", "ZAF"), ("Nigeria", "NGA"), ("Kenya", "KEN"),
        ("Tanzania", "TZA"), ("Ethiopia", "ETH"), ("Ghana", "GHA"),
        ("Cameroon", "CMR"), ("Mozambique", "MOZ"), ("Madagascar", "MDG"),
        ("Zimbabwe", "ZWE"), ("Angola", "AGO"), ("Zambia", "ZMB"),
        ("Senegal", "SEN"), ("Mali", "MLI"), ("Burkina Faso", "BFA"),
        ("Niger", "NER"), ("Guinea", "GIN"), ("Ivory Coast", "CIV"),
        ("Benin", "BEN"), ("Togo", "TGO"), ("Sierra Leone", "SLE"),
        ("Liberia", "LBR"), ("Gambia", "GMB"), ("Mauritania", "MRT"),
        ("Namibia", "NAM"), ("Botswana", "BWA"), ("Lesotho", "LSO"),
        ("Eswatini", "SWZ"), ("Gabon", "GAB"), ("Congo", "COG"),
        ("Uganda", "UGA"), ("Rwanda", "RWA"), ("Burundi", "BDI"),
        ("Malawi", "MWI"), ("Sudan", "SDN"), ("Somalia", "SOM"),
        ("Djibouti", "DJI"), ("Eritrea", "ERI"),
        ("Thailand", "THA"), ("Vietnam", "VNM"), ("Cambodia", "KHM"),
        ("Laos", "LAO"), ("Myanmar", "MMR"), ("Malaysia", "MYS"),
        ("Philippines", "PHL"), ("Nepal", "NPL"), ("Pakistan", "PAK"),
        ("Bangladesh", "BGD"), ("Sri Lanka", "LKA"), ("Afghanistan", "AFG"),
        ("Iran", "IRN"), ("Iraq", "IRQ"), ("Turkey", "TUR"),
        ("Saudi Arabia", "SAU"), ("Yemen", "YEM"), ("Oman", "OMN"),
        ("Syria", "SYR"), ("Jordan", "JOR"), ("Israel", "ISR"),
        ("Lebanon", "LBN"), ("Kuwait", "KWT"),
        ("France", "FRA"), ("Spain", "ESP"), ("Portugal", "PRT"),
        ("Germany", "DEU"), ("Italy", "ITA"), ("Sweden", "SWE"),
        ("Norway", "NOR"), ("Finland", "FIN"), ("Poland", "POL"),
        ("Romania", "ROU"), ("Ukraine", "UKR"), ("Belarus", "BLR"),
        ("Greece", "GRC"), ("Hungary", "HUN"), ("Austria", "AUT"),
        ("Switzerland", "CHE"), ("Netherlands", "NLD"), ("Belgium", "BEL"),
        ("Ireland", "IRL"), ("Denmark", "DNK"), ("Croatia", "HRV"),
        ("Serbia", "SRB"), ("Bosnia and Herzegovina", "BIH"),
        ("Albania", "ALB"), ("Bulgaria", "BGR"), ("Slovakia", "SVK"),
        ("Czechia", "CZE"), ("Lithuania", "LTU"), ("Latvia", "LVA"),
        ("Estonia", "EST"),
        ("Morocco", "MAR"), ("Tunisia", "TUN"), ("Libya", "LBY"),
        ("Egypt", "EGY"),
        ("Cuba", "CUB"), ("Dominican Republic", "DOM"),
        ("Costa Rica", "CRI"), ("Panama", "PAN"), ("Guatemala", "GTM"),
        ("Honduras", "HND"), ("Nicaragua", "NIC"), ("Belize", "BLZ"),
        ("El Salvador", "SLV"),
    ],
    key=lambda pair: len(pair[0]),
    reverse=True,
)


def trefle_region_to_alpha3(region_name: str) -> str | None:
    if region_name in EXACT_TREFLE_TO_ALPHA3:
        return EXACT_TREFLE_TO_ALPHA3[region_name]

    if region_name in COUNTRY_NAME_TO_ALPHA3:
        return COUNTRY_NAME_TO_ALPHA3[region_name]

    for prefix, alpha3 in PREFIX_TREFLE_TO_ALPHA3:
        if region_name.startswith(prefix):
            return alpha3

    return None


def get_distribution_country_codes(trefle_data: dict[str, Any]) -> list[str]:
    data = trefle_data.get("data")
    if not isinstance(data, dict):
        return []

    distribution = data.get("distribution")
    if not isinstance(distribution, dict):
        return []

    native = distribution.get("native")
    if not isinstance(native, list):
        return []

    alpha3_codes: set[str] = set()
    for entry in native:
        region_name = entry if isinstance(entry, str) else (
            entry.get("name") if isinstance(entry, dict) else None
        )
        if not isinstance(region_name, str):
            continue
        code = trefle_region_to_alpha3(region_name)
        if code:
            alpha3_codes.add(code)

    return sorted(alpha3_codes)
