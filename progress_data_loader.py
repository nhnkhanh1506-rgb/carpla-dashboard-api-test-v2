# ============================================================
# progress_data_loader.py
# LOAD BẢNG TIẾN ĐỘ TỪ 7 GOOGLE SHEET
# ============================================================

from io import StringIO
from urllib.parse import quote

import pandas as pd
import streamlit as st

from progress_config import (
    PROGRESS_CACHE_SECONDS,
    PROGRESS_EXPECTED_COLUMNS,
    PROGRESS_SHEETS,
)


# ============================================================
# 1. COLUMN MAPPING
# ============================================================

COLUMN_MAPPING = {
    "Số": "so_lenh",
    "Nguồn khách": "nguon_khach",
    "Biển số xe": "bien_so_xe",
    "Trạng thái": "trang_thai",
    "Loại hình sửa chữa": "loai_hinh_sua_chua",
    "Thời gian tạo": "thoi_gian_tao",
    "Ngày quyết toán": "ngay_quyet_toan",
    "Tổng trước thuế": "tong_truoc_thue",
    "Thuế": "thue",
    "Tổng tiền": "tong_tien",
    "Khách hàng": "khach_hang",
    "Số điện thoại": "so_dien_thoai",
    "Yêu cầu từ KH": "yeu_cau_tu_kh",
    "Ngày hóa đơn": "ngay_hoa_don",
    "Số tiền đề xuất hóa đơn": "so_tien_de_xuat_hoa_don",
    "Tình trạng hóa đơn": "tinh_trang_hoa_don",
    "Tình trạng xuất kho": "tinh_trang_xuat_kho",
    "Hãng xe": "hang_xe",
    "Cố vấn dịch vụ": "co_van_dich_vu",
    "Lý do không sử dụng": "ly_do_khong_su_dung",
    "Công đoạn": "cong_doan",
    "Kỹ thuật viên thực hiện": "ky_thuat_vien",
    "Trạng thái sửa chữa": "trang_thai_sua_chua",
    "Các bất thường": "cac_bat_thuong",
    "Bảo Hiểm": "bao_hiem",
    "Bảo hiểm": "bao_hiem",
    "Thời gian hẹn": "thoi_gian_hen",
    "Thời gian hẹn giao": "thoi_gian_hen_giao",
    "Thời gian giao xe": "thoi_gian_giao_xe",
    "Trạng thái giao xe": "trang_thai_giao_xe",
    "Tháng lập lệnh": "thang_lap_lenh",
    "Tháng quyết toán": "thang_quyet_toan",
    "Xưởng dịch vụ": "xuong_dich_vu",
}


DATETIME_COLUMNS = [
    "thoi_gian_tao",
    "ngay_quyet_toan",
    "ngay_hoa_don",
    "thoi_gian_hen",
    "thoi_gian_hen_giao",
    "thoi_gian_giao_xe",
]


# ============================================================
# 2. HELPERS
# ============================================================

def _clean_column_name(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def _normalize_dataframe(df, branch_name):
    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()
    data.columns = [_clean_column_name(c) for c in data.columns]

    # Bỏ cột rỗng / Unnamed.
    keep_columns = [
        c for c in data.columns
        if c and not c.lower().startswith("unnamed")
    ]
    data = data[keep_columns].copy()

    # Rename những cột đã biết.
    rename_map = {
        c: COLUMN_MAPPING[c]
        for c in data.columns
        if c in COLUMN_MAPPING
    }
    data = data.rename(columns=rename_map)

    # Nếu Google Sheet có duplicate header thì pandas thêm .1, .2...
    # Giữ bản đầu tiên để tránh lỗi downstream.
    data = data.loc[:, ~data.columns.duplicated()].copy()

    # Chỉ giữ dòng có Số lệnh.
    if "so_lenh" not in data.columns:
        return pd.DataFrame()

    data["so_lenh"] = (
        data["so_lenh"]
        .astype(str)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )
    data = data[data["so_lenh"] != ""].copy()

    # Chuẩn hóa text.
    text_columns = [
        "nguon_khach",
        "bien_so_xe",
        "trang_thai",
        "loai_hinh_sua_chua",
        "khach_hang",
        "hang_xe",
        "co_van_dich_vu",
        "cong_doan",
        "ky_thuat_vien",
        "trang_thai_sua_chua",
        "cac_bat_thuong",
        "bao_hiem",
        "trang_thai_giao_xe",
        "thang_lap_lenh",
        "thang_quyet_toan",
        "xuong_dich_vu",
    ]

    for col in text_columns:
        if col not in data.columns:
            data[col] = ""
        data[col] = (
            data[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Parse datetime.
    for col in DATETIME_COLUMNS:
        if col not in data.columns:
            data[col] = pd.NaT
        else:
            data[col] = pd.to_datetime(
                data[col],
                errors="coerce",
                dayfirst=True,
            )

    # Numeric.
    for col in [
        "tong_truoc_thue",
        "thue",
        "tong_tien",
        "so_tien_de_xuat_hoa_don",
    ]:
        if col in data.columns:
            data[col] = pd.to_numeric(
                data[col],
                errors="coerce",
            ).fillna(0)

    data["chi_nhanh"] = branch_name

    # Tạo month key chuẩn YYYY-MM.
    data["month_key"] = _build_month_key(data)

    return data.reset_index(drop=True)


def _build_month_key(data):
    # Ưu tiên cột Tháng lập lệnh có dạng 3-2026 / 03-2026.
    raw = (
        data.get("thang_lap_lenh", pd.Series("", index=data.index))
        .fillna("")
        .astype(str)
        .str.strip()
    )

    extracted = raw.str.extract(
        r"^\s*(\d{1,2})\s*[-/]\s*(\d{4})\s*$"
    )

    month_num = pd.to_numeric(
        extracted[0],
        errors="coerce",
    )
    year_num = pd.to_numeric(
        extracted[1],
        errors="coerce",
    )

    result = pd.Series("", index=data.index, dtype="object")

    valid = month_num.notna() & year_num.notna()
    result.loc[valid] = (
        year_num.loc[valid].astype(int).astype(str)
        + "-"
        + month_num.loc[valid].astype(int).astype(str).str.zfill(2)
    )

    # Fallback theo Thời gian tạo nếu Tháng lập lệnh trống.
    if "thoi_gian_tao" in data.columns:
        fallback = data["thoi_gian_tao"]
        missing = result.eq("") & fallback.notna()
        result.loc[missing] = fallback.loc[missing].dt.strftime("%Y-%m")

    return result


def _looks_like_raw_sheet(df):
    if df is None or df.empty:
        return False

    columns = {
        _clean_column_name(c)
        for c in df.columns
    }

    # Không bắt buộc đủ 100%; chỉ cần phần lớn các cột cốt lõi.
    matched = len(PROGRESS_EXPECTED_COLUMNS.intersection(columns))
    return matched >= 3 and "Số" in columns


# ============================================================
# 3. PUBLIC GOOGLE SHEET MODE
# ============================================================

def _read_public_sheet(spreadsheet_id, sheet_name):
    url = (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(sheet_name)}"
    )

    df = pd.read_csv(url)

    if not _looks_like_raw_sheet(df):
        raise ValueError(
            f"Tab '{sheet_name}' không giống tab dữ liệu tiến độ."
        )

    return df


# ============================================================
# 4. SERVICE ACCOUNT MODE (OPTIONAL)
# ============================================================

def _get_service_account_client():
    """
    Chỉ dùng khi st.secrets có:
    [gcp_service_account]
    type = "service_account"
    project_id = "..."
    private_key_id = "..."
    private_key = "-----BEGIN PRIVATE KEY-----\\n..."
    client_email = "..."
    client_id = "..."
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url = "..."
    """

    if "gcp_service_account" not in st.secrets:
        return None

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        return None

    credentials_info = dict(st.secrets["gcp_service_account"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=scopes,
    )

    return gspread.authorize(credentials)


def _read_private_sheet(
    spreadsheet_id,
    candidate_names,
):
    client = _get_service_account_client()

    if client is None:
        raise RuntimeError(
            "Không có Google service account trong Streamlit secrets."
        )

    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheets = spreadsheet.worksheets()

    # 1) Match đúng candidate.
    normalized_candidates = {
        name.strip().upper()
        for name in candidate_names
    }

    for ws in worksheets:
        if ws.title.strip().upper() in normalized_candidates:
            values = ws.get_all_values()
            if not values:
                continue
            df = pd.DataFrame(values[1:], columns=values[0])
            if _looks_like_raw_sheet(df):
                return df, ws.title

    # 2) Nếu tên tab khác dự kiến, tự dò tất cả tab bắt đầu bằng CN.
    for ws in worksheets:
        title_upper = ws.title.strip().upper()

        if title_upper in {"DASHBOARD", "HƯỚNG DẪN"}:
            continue

        if not title_upper.startswith("CN"):
            continue

        values = ws.get_all_values()
        if not values:
            continue

        df = pd.DataFrame(values[1:], columns=values[0])

        if _looks_like_raw_sheet(df):
            return df, ws.title

    raise ValueError(
        "Không tìm được tab raw tiến độ phù hợp trong Google Sheet."
    )


# ============================================================
# 5. LOAD 1 BRANCH
# ============================================================

@st.cache_data(
    ttl=PROGRESS_CACHE_SECONDS,
    show_spinner=False,
)
def load_progress_branch(branch_name):
    if branch_name not in PROGRESS_SHEETS:
        raise KeyError(
            f"Chưa cấu hình Google Sheet cho chi nhánh: {branch_name}"
        )

    cfg = PROGRESS_SHEETS[branch_name]
    spreadsheet_id = cfg["spreadsheet_id"]
    candidates = cfg["sheet_candidates"]

    errors = []

    # --------------------------------------------------------
    # A. THỬ PUBLIC CSV TRƯỚC
    # --------------------------------------------------------
    for sheet_name in candidates:
        try:
            raw = _read_public_sheet(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
            )

            data = _normalize_dataframe(
                raw,
                branch_name=branch_name,
            )

            if not data.empty:
                return data

        except Exception as exc:
            errors.append(
                f"Public/{sheet_name}: {exc}"
            )

    # --------------------------------------------------------
    # B. FALLBACK SERVICE ACCOUNT
    # --------------------------------------------------------
    try:
        raw, detected_sheet = _read_private_sheet(
            spreadsheet_id=spreadsheet_id,
            candidate_names=candidates,
        )

        data = _normalize_dataframe(
            raw,
            branch_name=branch_name,
        )

        if not data.empty:
            return data

    except Exception as exc:
        errors.append(
            f"Service account: {exc}"
        )

    raise RuntimeError(
        "Không đọc được Bảng tiến độ của "
        f"{branch_name}. "
        "Nếu Google Sheet đang Restricted, hãy share file cho "
        "service-account email hoặc chuyển sang Anyone with the link. "
        "Chi tiết: "
        + " | ".join(errors[-4:])
    )


# ============================================================
# 6. LOAD SCOPE
# ============================================================

@st.cache_data(
    ttl=PROGRESS_CACHE_SECONDS,
    show_spinner=False,
)
def load_progress_data(selected_branch="All"):
    if selected_branch != "All":
        return load_progress_branch(selected_branch)

    frames = []
    errors = []

    for branch_name in PROGRESS_SHEETS:
        try:
            frame = load_progress_branch(branch_name)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            errors.append(
                f"{branch_name}: {exc}"
            )

    if not frames:
        raise RuntimeError(
            "Không đọc được dữ liệu tiến độ từ chi nhánh nào. "
            + " | ".join(errors)
        )

    data = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    # Lưu lỗi để dashboard có thể hiển thị cảnh báo nhẹ.
    data.attrs["load_errors"] = errors

    return data
