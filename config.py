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
# TARGET
# ============================================================
# Nếu workshop_manager.xlsx còn tồn tại thì vẫn đọc target
# từ file đó để không làm mất cơ chế target hiện tại.
#
# Target được lưu theo:
# (Chi nhánh, Xưởng, Năm, Tháng)
#
# Khi chọn Xưởng = All hoặc Tháng = All,
# calculations.py sẽ tự cộng các target phù hợp.

def _clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def _parse_number(value):
    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return int(value)

    cleaned = (
        str(value)
        .strip()
        .replace(".", "")
        .replace(",", "")
        .replace(" ", "")
    )

    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def load_targets():
    targets = {}

    if not WORKSHOP_MANAGER_FILE.exists():
        return targets

    try:
        manager = pd.read_excel(
            WORKSHOP_MANAGER_FILE,
            sheet_name="Workshop Manager",
            header=1,
        )
    except Exception:
        return targets

    manager.columns = [
        str(column).strip()
        for column in manager.columns
    ]

    required = [
        "Chi nhánh",
        "Xưởng",
        "Năm",
        "Tháng",
        "Target RO",
        "Target doanh thu",
    ]

    if any(
        column not in manager.columns
        for column in required
    ):
        return targets

    if "Trạng thái" in manager.columns:
        active_mask = (
            manager["Trạng thái"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
            == "đang hoạt động".casefold()
        )
        manager = manager[active_mask].copy()

    for _, row in manager.iterrows():
        branch = _clean_text(row["Chi nhánh"])
        workshop = _clean_text(row["Xưởng"])

        year = _parse_number(row["Năm"])
        month = _parse_number(row["Tháng"])

        if not branch or not workshop or not year or not month:
            continue

        targets[
            (
                branch,
                workshop,
                year,
                month,
            )
        ] = {
            "ro": _parse_number(
                row["Target RO"]
            ),
            "revenue": _parse_number(
                row["Target doanh thu"]
            ),
        }

    return targets


TARGETS = load_targets()


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
