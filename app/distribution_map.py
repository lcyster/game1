from typing import Any

TDWG_REGION_TO_ALPHA3: dict[str, list[str]] = {
    "Northern America": ["CAN", "USA", "GRL", "SPM"],
    "Mexico": ["MEX"],
    "Central America": ["GTM", "BLZ", "HND", "SLV", "NIC", "CRI", "PAN"],
    "Caribbean": [
        "BHS", "CUB", "JAM", "HTI", "DOM", "PRI", "TTO", "BRB", "ATG", "DMA",
        "GRD", "KNA", "LCA", "VCT", "SXM", "ABW", "CUW", "CYM", "MAF", "VIR",
        "VGB", "AIA", "BMU", "TCA",
    ],
    "Northern South America": ["VEN", "COL", "GUY", "SUR", "GUF"],
    "Western South America": ["ECU", "PER", "BOL"],
    "Brazil": ["BRA"],
    "Southern South America": ["CHL", "ARG", "PRY", "URY"],
    "Northern Europe": ["SWE", "NOR", "FIN", "DNK", "ISL", "GBR", "IRL", "EST", "LVA", "LTU", "FRO"],
    "Middle Europe": ["DEU", "FRA", "NLD", "BEL", "LUX", "CHE", "AUT", "POL", "CZE", "SVK", "HUN", "LIE"],
    "Southwestern Europe": ["ESP", "PRT", "GIB", "AND", "MCO"],
    "Southeastern Europe": [
        "ITA", "HRV", "BIH", "SRB", "MNE", "MKD", "ALB", "GRC", "BGR", "ROU", "SVN",
    ],
    "Eastern Europe": ["RUS", "UKR", "BLR", "MDA"],
    "Northern Africa": ["MAR", "DZA", "TUN", "LBY", "EGY", "ESH"],
    "Macaronesia": ["CPV"],
    "West Tropical Africa": [
        "SEN", "GMB", "MLI", "BFA", "GIN", "SLE", "LBR", "CIV", "GHA", "TGO",
        "BEN", "NER", "NGA", "MRT",
    ],
    "West-Central Tropical Africa": ["TCD", "CMR", "CAF", "COG", "COD", "GNQ", "GAB", "STP"],
    "Northeast Tropical Africa": ["SDN", "ERI", "DJI", "SOM", "ETH"],
    "East Tropical Africa": ["KEN", "UGA", "TZA", "BDI", "RWA"],
    "Southern Africa": ["ZAF", "NAM", "BWA", "SWZ", "LSO"],
    "South Tropical Africa": ["AGO", "ZMW", "MWI", "MOZ", "ZWE"],
    "Western Indian Ocean": ["MDG", "MUS", "SYC", "COM", "MYT", "REU"],
    "Arabian Peninsula": ["SAU", "YEM", "OMN", "ARE", "QAT", "BHR", "KWT"],
    "Western Asia": ["TUR", "SYR", "LBN", "ISR", "JOR", "IRQ", "IRN", "CYP"],
    "Caucasus": ["GEO", "ARM", "AZE"],
    "Central Asia": ["KAZ", "UZB", "TKM", "TJK", "KGZ", "AFG"],
    "Siberia": ["RUS"],
    "Russian Far East": ["RUS"],
    "China": ["CHN"],
    "Mongolia": ["MNG"],
    "Eastern Asia": ["JPN", "KOR", "PRK", "TWN"],
    "Indian Subcontinent": ["IND", "PAK", "BGD", "LKA", "NPL", "BTN", "MDV"],
    "Indo-China": ["THA", "VNM", "KHM", "LAO", "MMR"],
    "Malesia": ["MYS", "IDN", "PHL", "BRN", "TLS", "SGP"],
    "Papua New Guinea": ["PNG"],
    "Australia": ["AUS"],
    "New Zealand": ["NZL"],
    "Pacific": [
        "FJI", "WSM", "TON", "VUT", "SLB", "KIR", "MHL", "FSM", "PLW", "NRU",
        "COK", "NIU", "NFK", "TKL", "PYF", "GUM", "MNP", "ASM",
    ],
    "Subarctic America": ["CAN", "GRL"],
    "Subantarctic Islands": ["ATA"],
}

ALPHA3_TO_NAME: dict[str, str] = {
    "CAN": "Canada", "USA": "United States", "GRL": "Greenland", "SPM": "Saint Pierre and Miquelon",
    "MEX": "Mexico", "GTM": "Guatemala", "BLZ": "Belize", "HND": "Honduras", "SLV": "El Salvador",
    "NIC": "Nicaragua", "CRI": "Costa Rica", "PAN": "Panama",
    "BHS": "Bahamas", "CUB": "Cuba", "JAM": "Jamaica", "HTI": "Haiti", "DOM": "Dominican Republic",
    "PRI": "Puerto Rico", "TTO": "Trinidad and Tobago", "BRB": "Barbados", "ATG": "Antigua and Barbuda",
    "DMA": "Dominica", "GRD": "Grenada", "KNA": "Saint Kitts and Nevis", "LCA": "Saint Lucia",
    "VCT": "Saint Vincent and the Grenadines", "ABW": "Aruba", "CUW": "Curaçao", "CYM": "Cayman Islands",
    "VIR": "U.S. Virgin Islands", "VGB": "British Virgin Islands", "BMU": "Bermuda",
    "VEN": "Venezuela", "COL": "Colombia", "GUY": "Guyana", "SUR": "Suriname", "GUF": "French Guiana",
    "ECU": "Ecuador", "PER": "Peru", "BOL": "Bolivia", "BRA": "Brazil",
    "CHL": "Chile", "ARG": "Argentina", "PRY": "Paraguay", "URY": "Uruguay",
    "SWE": "Sweden", "NOR": "Norway", "FIN": "Finland", "DNK": "Denmark", "ISL": "Iceland",
    "GBR": "United Kingdom", "IRL": "Ireland", "EST": "Estonia", "LVA": "Latvia", "LTU": "Lithuania",
    "FRO": "Faroe Islands",
    "DEU": "Germany", "FRA": "France", "NLD": "Netherlands", "BEL": "Belgium", "LUX": "Luxembourg",
    "CHE": "Switzerland", "AUT": "Austria", "POL": "Poland", "CZE": "Czechia", "SVK": "Slovakia",
    "HUN": "Hungary", "LIE": "Liechtenstein",
    "ESP": "Spain", "PRT": "Portugal", "GIB": "Gibraltar", "AND": "Andorra", "MCO": "Monaco",
    "ITA": "Italy", "HRV": "Croatia", "BIH": "Bosnia and Herzegovina", "SRB": "Serbia",
    "MNE": "Montenegro", "MKD": "North Macedonia", "ALB": "Albania", "GRC": "Greece",
    "BGR": "Bulgaria", "ROU": "Romania", "SVN": "Slovenia",
    "RUS": "Russia", "UKR": "Ukraine", "BLR": "Belarus", "MDA": "Moldova",
    "MAR": "Morocco", "DZA": "Algeria", "TUN": "Tunisia", "LBY": "Libya", "EGY": "Egypt", "ESH": "Western Sahara",
    "CPV": "Cape Verde",
    "SEN": "Senegal", "GMB": "Gambia", "MLI": "Mali", "BFA": "Burkina Faso", "GIN": "Guinea",
    "SLE": "Sierra Leone", "LBR": "Liberia", "CIV": "Ivory Coast", "GHA": "Ghana", "TGO": "Togo",
    "BEN": "Benin", "NER": "Niger", "NGA": "Nigeria", "MRT": "Mauritania",
    "TCD": "Chad", "CMR": "Cameroon", "CAF": "Central African Republic", "COG": "Republic of the Congo",
    "COD": "Democratic Republic of the Congo", "GNQ": "Equatorial Guinea", "GAB": "Gabon", "STP": "São Tomé and Príncipe",
    "SDN": "Sudan", "ERI": "Eritrea", "DJI": "Djibouti", "SOM": "Somalia", "ETH": "Ethiopia",
    "KEN": "Kenya", "UGA": "Uganda", "TZA": "Tanzania", "BDI": "Burundi", "RWA": "Rwanda",
    "ZAF": "South Africa", "NAM": "Namibia", "BWA": "Botswana", "SWZ": "Eswatini", "LSO": "Lesotho",
    "AGO": "Angola", "ZMW": "Zambia", "MWI": "Malawi", "MOZ": "Mozambique", "ZWE": "Zimbabwe",
    "MDG": "Madagascar", "MUS": "Mauritius", "SYC": "Seychelles", "COM": "Comoros",
    "SAU": "Saudi Arabia", "YEM": "Yemen", "OMN": "Oman", "ARE": "United Arab Emirates",
    "QAT": "Qatar", "BHR": "Bahrain", "KWT": "Kuwait",
    "TUR": "Turkey", "SYR": "Syria", "LBN": "Lebanon", "ISR": "Israel", "JOR": "Jordan",
    "IRQ": "Iraq", "IRN": "Iran", "CYP": "Cyprus",
    "GEO": "Georgia", "ARM": "Armenia", "AZE": "Azerbaijan",
    "KAZ": "Kazakhstan", "UZB": "Uzbekistan", "TKM": "Turkmenistan", "TJK": "Tajikistan",
    "KGZ": "Kyrgyzstan", "AFG": "Afghanistan",
    "CHN": "China", "MNG": "Mongolia",
    "JPN": "Japan", "KOR": "South Korea", "PRK": "North Korea", "TWN": "Taiwan",
    "IND": "India", "PAK": "Pakistan", "BGD": "Bangladesh", "LKA": "Sri Lanka", "NPL": "Nepal",
    "BTN": "Bhutan", "MDV": "Maldives",
    "THA": "Thailand", "VNM": "Vietnam", "KHM": "Cambodia", "LAO": "Laos", "MMR": "Myanmar",
    "MYS": "Malaysia", "IDN": "Indonesia", "PHL": "Philippines", "BRN": "Brunei", "TLS": "Timor-Leste", "SGP": "Singapore",
    "PNG": "Papua New Guinea", "AUS": "Australia", "NZL": "New Zealand",
    "FJI": "Fiji", "WSM": "Samoa", "TON": "Tonga", "VUT": "Vanuatu", "SLB": "Solomon Islands",
    "KIR": "Kiribati", "MHL": "Marshall Islands", "FSM": "Micronesia", "PLW": "Palau", "NRU": "Nauru",
    "COK": "Cook Islands", "NIU": "Niue", "NFK": "Norfolk Island", "PYF": "French Polynesia",
    "GUM": "Guam", "MNP": "Northern Mariana Islands", "ASM": "American Samoa",
    "ATA": "Antarctica",
}


def region_names_to_country_codes(region_names: list[str]) -> list[str]:
    alpha3_codes: set[str] = set()
    for region_name in region_names:
        codes = TDWG_REGION_TO_ALPHA3.get(region_name, [])
        alpha3_codes.update(codes)
    return sorted(alpha3_codes)


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

    region_names: list[str] = []
    for entry in native:
        if isinstance(entry, str):
            region_names.append(entry)
        elif isinstance(entry, dict):
            name = entry.get("name")
            if isinstance(name, str):
                region_names.append(name)

    return region_names_to_country_codes(region_names)
