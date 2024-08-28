POSITION_SPREADSHEET_NAME = "AAAA"
ROOF_SPREADSHEET_NAME = "Dach"
FOUNDATION_SPREADSHEET_NAME = "Fundament"
INSULATION_SPREADSHEET_NAME = "Ocieplenie"

DEFAULT_POSITION_CSV_PATH = "resources/pozycje.csv"
DEFAULT_ROOF_CSV_PATH = "resources/dach.csv"
DEFAULT_FOUNDATION_CSV_PATH = "resources/fundamenty.csv"
DEFAULT_INSULATION_CSV_PATH = "resources/ocieplenie.csv"

SPREADSHEET_PROPERTY_DEFAULTS = \
    [["pow.siatki", "=2.15*5"],
     ["DŁUGOŚĆ BUDYNKU W m", "6.47"],
     ["SZEROKOŚĆ BUDYNKU W m", "5.47"],
     ["ILOŚĆ SZKLANEK", "6"],
     ["ŚCIANKI DZIAŁOWE NA PARTERZE W MB", "5.3"],
     ["DŁUGOŚĆ POŁACI", "7.85"],
     ["ŚCIANKI DZIAŁOWE NA PIĘTRZE W MB", "11"],
     ["WYOKOŚĆ ŚCIANKI KOLANKOWEJ", "0.8"],
     ["WYSOKOŚĆ ŚCIAN PARTERU", "2.8"],
     ["CZY DOM POWYŻĘJ 70M2?", "0"],
     ["CZY PODDASZE UŻYTKOWE?", "0"],
     ["CZY KOMIN?", "1"],

     ["OBWÓD", "=(Właściwości!B2+Właściwości!B3)*2"],
     ["POWIERZCHNIA FUNDAMENTU", "=Właściwości!B2*Właściwości!B3"],
     ["ILOŚĆ KROKWII", "=Właściwości!B2/0.6"],
     ["DŁUGOŚĆ KROKWII", "=Właściwości!B3*0.9"],
     ["M2 ŚCIAN PARTERU", "=Właściwości!B13*Właściwości!B9"],
     ["M2 ŚCIANYKOLANKOWEJ", "=Właściwości!B8*Właściwości!B13"],
     ["M2 SZCZYTÓW", "=Właściwości!B3*Właściwości!B9"],
     ["M2 ŚCIAN ZEWNETRZNYCH", "=Właściwości!B19*Właściwości!B18*Właściwości!B17"],
     ["DŁUGOŚĆ OKAPU", "=IF(Właściwości!B3>6;0.8;0.6)"],
     ["DŁUGOŚĆ WYPUSTU", "=IF(Właściwości!B2>7;0.8;0.6)"],
     ]

MATERIAL_COLUMN = ("MATERIAŁ", "A")
ID_COLUMN = ("ID", "B")
DESCRIPTION_COLUMN = ("OPIS", "C")
UOM_COLUMN = ("J.M.", "D")
QUANTITY_COLUMN = ("ILOŚĆ", "E")
PRICE_COLUMN = ("CENA", "F")
NET_VALUE_COLUMN = ("WARTOŚĆ NETTO", "G")

COLUMNS = [
    MATERIAL_COLUMN,
    ID_COLUMN,
    DESCRIPTION_COLUMN,
    UOM_COLUMN,
    QUANTITY_COLUMN,
    PRICE_COLUMN,
    NET_VALUE_COLUMN
]
