from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st


# ============================================================
# ĐƯỜNG DẪN GỐC
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
WORKSHOP_MANAGER_FILE = BASE_DIR / "workshop_manager.xlsx"


# ============================================================
# HÀM HỖ TRỢ
# ============================================================

def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_status(value):
    """
    Chuẩn hóa trạng thái để tránh lỗi do:
    - khoảng trắng thừa
    - khoảng trắng không ngắt dòng
    - khác biệt viết hoa / viết thường
    - có hoặc không có dấu tiếng Việt
    """
    text = clean_text(value)

    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)

    text = unicodedata.normalize(
        "NFD",
        text,
    )

    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )

    text = (
        text.replace("đ", "d")
        .replace("Đ", "D")
    )

    return text.casefold().strip()


def clean_optional_path(value):
    path_text = clean_text(value)

    if not path_text:
        return None

    return BASE_DIR / Path(path_text)


def parse_integer(value, field_name, row_number):
    if pd.isna(value) or clean_text(value) == "":
        st.error(
            f"Dòng {row_number} trong workshop_manager.xlsx "
            f"chưa có {field_name}."
        )
        st.stop()

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
        st.error(
            f"Dòng {row_number} trong workshop_manager.xlsx "
            f"có {field_name} không hợp lệ: {value}"
        )
        st.stop()


# ============================================================
# ĐỌC FILE QUẢN LÝ XƯỞNG
# ============================================================

@st.cache_data
def load_workshop_manager():
    if not WORKSHOP_MANAGER_FILE.exists():
        st.error(
            "Không tìm thấy workshop_manager.xlsx "
            "ở thư mục chính của repository."
        )
        st.stop()

    try:
        manager = pd.read_excel(
            WORKSHOP_MANAGER_FILE,
            sheet_name="Workshop Manager",
            header=1,
        )
    except ValueError:
        st.error(
            "Không tìm thấy sheet 'Workshop Manager' "
            "trong workshop_manager.xlsx."
        )
        st.stop()

    manager.columns = [
        str(column).strip()
        for column in manager.columns
    ]

    required_columns = [
        "Chi nhánh",
        "Xưởng",
        "Năm",
        "Tháng",
        "File lệnh sửa chữa",
        "File tổng hợp phụ tùng",
        "File phụ kiện",
        "Target RO",
        "Target doanh thu",
        "Trạng thái",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in manager.columns
    ]

    if missing_columns:
        st.error(
            "workshop_manager.xlsx thiếu các cột: "
            + ", ".join(missing_columns)
        )
        st.stop()

    manager = manager.dropna(how="all").copy()

    manager["Chi nhánh"] = manager["Chi nhánh"].apply(clean_text)
    manager["Xưởng"] = manager["Xưởng"].apply(clean_text)
    manager["Trạng thái"] = manager["Trạng thái"].apply(clean_text)
    manager["trang_thai_key"] = manager["Trạng thái"].apply(
        normalize_status
    )

    manager = manager[
        (manager["Chi nhánh"] != "")
        & (manager["Xưởng"] != "")
    ].copy()

    manager = manager[
        manager["trang_thai_key"].eq(
            "dang hoat dong"
        )
    ].copy()

    if manager.empty:
        st.error(
            "Không có xưởng nào mang trạng thái "
            "'Đang hoạt động' trong workshop_manager.xlsx."
        )
        st.stop()

    return manager


# ============================================================
# TẠO CẤU HÌNH TỪ EXCEL
# ============================================================

def build_configuration():
    manager = load_workshop_manager()

    workshop_config = {}
    targets = {}

    for dataframe_index, row in manager.iterrows():
        excel_row_number = int(dataframe_index) + 3

        branch_name = clean_text(row["Chi nhánh"])
        workshop_name = clean_text(row["Xưởng"])

        year = parse_integer(
            row["Năm"],
            "Năm",
            excel_row_number,
        )

        month = parse_integer(
            row["Tháng"],
            "Tháng",
            excel_row_number,
        )

        service_file = clean_optional_path(
            row["File lệnh sửa chữa"]
        )

        parts_file = clean_optional_path(
            row["File tổng hợp phụ tùng"]
        )

        accessory_file = clean_optional_path(
            row["File phụ kiện"]
        )

        target_ro = parse_integer(
            row["Target RO"],
            "Target RO",
            excel_row_number,
        )

        target_revenue = parse_integer(
            row["Target doanh thu"],
            "Target doanh thu",
            excel_row_number,
        )

        if service_file is None:
            st.error(
                f"Dòng {excel_row_number} chưa có "
                "File lệnh sửa chữa."
            )
            st.stop()

        if workshop_name in workshop_config:
            st.error(
                f"Xưởng '{workshop_name}' xuất hiện nhiều dòng "
                "trong workshop_manager.xlsx. "
                "Tên xưởng hiện cần là duy nhất."
            )
            st.stop()

        workshop_config[workshop_name] = {
            "chi_nhanh": branch_name,
            "service_file": service_file,
            "parts_file": parts_file,
            "accessory_file": accessory_file,
        }

        targets[
            (
                branch_name,
                workshop_name,
                year,
                month,
            )
        ] = {
            "ro": target_ro,
            "revenue": target_revenue,
        }

    return workshop_config, targets


WORKSHOP_CONFIG, TARGETS = build_configuration()


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

LOGO_FILE = BASE_DIR / "carpla_services_logo_hd.png"
