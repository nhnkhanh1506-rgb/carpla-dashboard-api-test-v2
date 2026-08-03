from pathlib import Path

import pandas as pd


# ============================================================
# ĐƯỜNG DẪN GỐC
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LOGO_FILE = BASE_DIR / "carpla_services_logo_hd.png"
WORKSHOP_MANAGER_FILE = BASE_DIR / "workshop_manager.xlsx"


# ============================================================
# 7 CHI NHÁNH TOÀN HỆ THỐNG
# ============================================================

BRANCH_ORDER = [
    "Hà Nội",
    "Tây Bắc Bộ",
    "Đông Bắc Bộ",
    "TP. HCM",
    "Cần Thơ",
    "Nghệ An",
    "Đà Nẵng",
]


# ============================================================
# FILE DỮ LIỆU TỔNG HỢP THEO CHI NHÁNH
# ============================================================
# Bước đầu mới dùng Hà Nội.
# Upload file tổng hợp Hà Nội vào thư mục data và đổi tên:
#     ha_noi_2026.xlsx
#
# Sau này chỉ cần thêm các chi nhánh còn lại vào đây.

DATA_FILES = {
    "Hà Nội": DATA_DIR / "ha_noi_2026.xlsx",
}


# ============================================================
# CHUẨN HÓA TÊN 8 XƯỞNG HÀ NỘI
# ============================================================
# Key  : tên đang nằm trong cột "Chi nhánh" của file DMS.
# Value: tên muốn hiển thị trên sidebar/dashboard.

WORKSHOP_NAME_MAP = {
    "CHI NHÁNH HÀ NỘI - PVĐ": "Phạm Văn Đồng",
    "CN Hà Nội-Giải Phóng": "Giải Phóng",
    "CN Hà Nội-Hà Đông": "Hà Đông",
    "CN Hà Nội-Hải Dương": "Hải Dương",
    "CN Hà Nội-Long Biên": "Long Biên",
    "CN Hà Nội- Hà Nam": "Hà Nam",
    "CN Hà Nội-Hưng Yên": "Hưng Yên",
    "CN Hà Nội-Ninh Bình": "Ninh Bình",
}


# ============================================================
# TARGET - CHỈ ÁP DỤNG THÁNG 7/2026
# ============================================================
# Quy tắc:
# - Chỉ có target khi:
#     Chi nhánh = Hà Nội
#     Xưởng = 1 xưởng cụ thể
#     Năm = 2026
#     Tháng = 7
#
# - Không có target khi:
#     Tháng = 1..6
#     Tháng = All
#     Xưởng = All
#     Chi nhánh = All / Toàn HO
#     Các chi nhánh khác
#
# Không cộng target các xưởng để tạo target Chi nhánh / HO.

TARGETS = {
    ("Hà Nội", "Phạm Văn Đồng", 2026, 7): {
        "ro": 714,
        "revenue": 1_429_000_000,
    },
    ("Hà Nội", "Long Biên", 2026, 7): {
        "ro": 643,
        "revenue": 1_287_000_000,
    },
    ("Hà Nội", "Giải Phóng", 2026, 7): {
        "ro": 527,
        "revenue": 1_055_000_000,
    },
    ("Hà Nội", "Hà Đông", 2026, 7): {
        "ro": 427,
        "revenue": 855_000_000,
    },
    ("Hà Nội", "Hưng Yên", 2026, 7): {
        "ro": 216,
        "revenue": 432_000_000,
    },
    ("Hà Nội", "Hà Nam", 2026, 7): {
        "ro": 154,
        "revenue": 309_000_000,
    },
    ("Hà Nội", "Hải Dương", 2026, 7): {
        "ro": 287,
        "revenue": 575_000_000,
    },
    ("Hà Nội", "Ninh Bình", 2026, 7): {
        "ro": 74,
        "revenue": 148_000_000,
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
# GIỮ BIẾN CŨ ĐỂ TƯƠNG THÍCH
# ============================================================

WORKING_DAYS = 27
