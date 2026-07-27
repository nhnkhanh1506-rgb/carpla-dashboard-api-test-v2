from pathlib import Path


# ============================================================
# CẤU HÌNH CHI NHÁNH, XƯỞNG VÀ FILE DỮ LIỆU
# ============================================================

WORKSHOP_CONFIG = {
    "Phạm Văn Đồng": {
        "chi_nhanh": "Hà Nội",

        "service_file": Path(
            "hn_pvd_service_2026_07.xlsx"
        ),

        "parts_file": Path(
            "summary_repair_orders.xlsx"
        ),

        "accessory_file": None,
    },
}


# ============================================================
# TARGET THEO CHI NHÁNH, XƯỞNG, NĂM, THÁNG
# ============================================================

TARGETS = {
    ("Hà Nội", "Phạm Văn Đồng", 2026, 7): {
        "ro": 714,
        "revenue": 1_429_000_000,
    },
}


# ============================================================
# PHÂN NHÓM QUAN HỆ THƯƠNG HIỆU
# ============================================================

TASCO_OFFICIAL_BRANDS = [
    "GEELY",
    "LYNK & CO",
    "ZEEKR",
    "LOTUS",
]

PARTNER_BRANDS = [
    "HYUNDAI",
    "TOYOTA",
    "KIA",
    "MAZDA",
    "MITSUBISHI",
    "FORD",
    "HONDA",
    "VOLVO",
    "MERCEDES-BENZ",
    "BMW",
    "AUDI",
    "LEXUS",
    "PORSCHE",
    "LAND ROVER",
    "JAGUAR",
    "PEUGEOT",
    "VOLKSWAGEN",
    "SUZUKI",
    "MG",
    "VINFAST",
    "OMODA & JAECOO",
    "WULING",
]


# ============================================================
# PHÂN NHÓM PHÂN KHÚC XE
# ============================================================

LUXURY_BRANDS = [
    "AUDI",
    "BMW",
    "JAGUAR",
    "LAND ROVER",
    "LEXUS",
    "LOTUS",
    "MERCEDES-BENZ",
    "PORSCHE",
    "VOLVO",
    "ZEEKR",
]

MASS_MARKET_BRANDS = [
    "FORD",
    "GEELY",
    "HONDA",
    "HYUNDAI",
    "KIA",
    "LYNK & CO",
    "MAZDA",
    "MG",
    "MITSUBISHI",
    "OMODA & JAECOO",
    "PEUGEOT",
    "SUZUKI",
    "TOYOTA",
    "VINFAST",
    "VOLKSWAGEN",
    "WULING",
]


# ============================================================
# CẤU HÌNH CHUNG
# ============================================================

WORKING_DAYS = 27

LOGO_FILE = Path(
    "carpla_services_logo_hd.png"
)
