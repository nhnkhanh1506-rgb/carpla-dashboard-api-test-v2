import calendar
import re
import unicodedata
from datetime import date

import pandas as pd
import requests
import streamlit as st

from config import (
    API_BUFFER_MONTHS,
    API_CACHE_TTL_SECONDS,
    API_TIMEOUT_SECONDS,
    API_URL,
    API_WORKSHOP_BRANCH_MAP,
    API_WORKSHOP_NAME_MAP,
    BRANCH_ORDER,
    BRANCH_WORKSHOP_CODES,
)


# ============================================================
# HÀM CHUẨN HÓA
# ============================================================

def normalize_order_number(series):
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
        .replace({
            "": pd.NA,
            "NAN": pd.NA,
            "NONE": pd.NA,
        })
    )


def parse_money(series):
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(
            series,
            errors="coerce",
        ).fillna(0)

    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(r"[^\d\-.]", "", regex=True)
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    ).fillna(0)


# ============================================================
# HÀM THỜI GIAN
# ============================================================

def _month_start(year, month):
    return pd.Timestamp(
        year=int(year),
        month=int(month),
        day=1,
    )


def _month_end(year, month):
    last_day = calendar.monthrange(
        int(year),
        int(month),
    )[1]

    end = pd.Timestamp(
        year=int(year),
        month=int(month),
        day=last_day,
    )

    today = pd.Timestamp(date.today())

    if (
        int(year) == today.year
        and int(month) == today.month
    ):
        end = min(
            end,
            today,
        )

    return end


def _shift_months(timestamp, months):
    return (
        pd.Timestamp(timestamp)
        + pd.DateOffset(months=int(months))
    )


def _iter_month_batches(start_date, end_date):
    cursor = pd.Timestamp(
        year=start_date.year,
        month=start_date.month,
        day=1,
    )

    end_date = pd.Timestamp(end_date)

    while cursor <= end_date:
        batch_start = cursor

        batch_end = pd.Timestamp(
            year=cursor.year,
            month=cursor.month,
            day=calendar.monthrange(
                cursor.year,
                cursor.month,
            )[1],
        )

        batch_start = max(
            batch_start,
            pd.Timestamp(start_date),
        )

        batch_end = min(
            batch_end,
            end_date,
        )

        yield (
            batch_start,
            batch_end,
        )

        cursor = (
            cursor
            + pd.DateOffset(months=1)
        )


# ============================================================
# XÁC ĐỊNH PHẠM VI API
# ============================================================

def get_branch_codes(
    selected_branch,
    selected_workshop,
):
    if selected_branch == "All":
        codes = []

        for branch_name in BRANCH_ORDER:
            for workshop_codes in (
                BRANCH_WORKSHOP_CODES
                .get(branch_name, {})
                .values()
            ):
                codes.extend(
                    workshop_codes
                )

        return sorted(
            set(codes)
        )

    workshop_map = (
        BRANCH_WORKSHOP_CODES.get(
            selected_branch,
            {},
        )
    )

    if selected_workshop == "All":
        codes = []

        for workshop_codes in (
            workshop_map.values()
        ):
            codes.extend(
                workshop_codes
            )

        return sorted(
            set(codes)
        )

    return sorted(
        set(
            workshop_map.get(
                selected_workshop,
                [],
            )
        )
    )


def get_api_raw_window(
    year,
    month,
):
    year = int(year)
    today = pd.Timestamp(
        date.today()
    )

    if month == "All":
        dashboard_start = pd.Timestamp(
            year=year,
            month=1,
            day=1,
        )

        if year == today.year:
            dashboard_end = today
        else:
            dashboard_end = pd.Timestamp(
                year=year,
                month=12,
                day=31,
            )

        api_start = _shift_months(
            dashboard_start,
            -API_BUFFER_MONTHS,
        )

        api_end = dashboard_end

    else:
        month = int(month)

        dashboard_start = _month_start(
            year,
            month,
        )

        dashboard_end = _month_end(
            year,
            month,
        )

        api_start = _shift_months(
            dashboard_start,
            -API_BUFFER_MONTHS,
        )

        api_end = dashboard_end

    return {
        "dashboard_start": dashboard_start,
        "dashboard_end": dashboard_end,
        "api_start": api_start,
        "api_end": api_end,
    }


# ============================================================
# CALL API - CACHE THEO TỪNG BATCH 1 THÁNG
# ============================================================

def _get_authorization():
    try:
        authorization = (
            st.secrets["api"]["authorization"]
        )
    except Exception:
        st.error(
            "Chưa cấu hình API Production Authorization "
            "trong Streamlit Secrets."
        )
        st.stop()

    if not authorization:
        st.error(
            "API Production Authorization đang trống."
        )
        st.stop()

    return authorization


def _call_api_batch_uncached(
    date_from_text,
    date_to_text,
    branch_codes_tuple,
    authorization,
):
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    payload = {
        "date_from": date_from_text,
        "date_to": date_to_text,
        "branch_ids": [],
        "branch_codes": list(
            branch_codes_tuple
        ),
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=API_TIMEOUT_SECONDS,
    )

    response.raise_for_status()

    response_json = response.json()

    if not isinstance(
        response_json,
        dict,
    ):
        raise ValueError(
            "API không trả response dạng dict."
        )

    success_data = response_json.get(
        "success"
    )

    if not isinstance(
        success_data,
        dict,
    ):
        raise ValueError(
            "API response không có object 'success'."
        )

    records = success_data.get(
        "data",
        [],
    )

    if records is None:
        records = []

    if not isinstance(
        records,
        list,
    ):
        raise ValueError(
            "API response success.data không phải list."
        )

    return records


@st.cache_data(
    ttl=86_400,
    show_spinner=False,
)
def _call_api_batch_historical_cached(
    date_from_text,
    date_to_text,
    branch_codes_tuple,
    authorization,
):
    return _call_api_batch_uncached(
        date_from_text=date_from_text,
        date_to_text=date_to_text,
        branch_codes_tuple=branch_codes_tuple,
        authorization=authorization,
    )


@st.cache_data(
    ttl=API_CACHE_TTL_SECONDS,
    show_spinner=False,
)
def _call_api_batch_current_cached(
    date_from_text,
    date_to_text,
    branch_codes_tuple,
    authorization,
):
    return _call_api_batch_uncached(
        date_from_text=date_from_text,
        date_to_text=date_to_text,
        branch_codes_tuple=branch_codes_tuple,
        authorization=authorization,
    )


def call_api_raw(
    selected_branch,
    selected_workshop,
    year,
    month,
):
    branch_codes = get_branch_codes(
        selected_branch=selected_branch,
        selected_workshop=selected_workshop,
    )

    if not branch_codes:
        st.error(
            "Không tìm thấy branch code cho phạm vi đã chọn."
        )
        st.stop()

    window = get_api_raw_window(
        year=year,
        month=month,
    )

    authorization = _get_authorization()

    all_records = []

    batches = list(
        _iter_month_batches(
            window["api_start"],
            window["api_end"],
        )
    )

    progress_text = (
        "Đang lấy dữ liệu DMS từ API Production..."
    )

    with st.spinner(
        progress_text
    ):
        for (
            batch_start,
            batch_end,
        ) in batches:
            try:
                current_month_start = pd.Timestamp(
                    year=date.today().year,
                    month=date.today().month,
                    day=1,
                )

                cache_function = (
                    _call_api_batch_historical_cached
                    if batch_end < current_month_start
                    else _call_api_batch_current_cached
                )

                records = (
                    cache_function(
                        date_from_text=(
                            batch_start.strftime(
                                "%Y-%m-%d"
                            )
                        ),
                        date_to_text=(
                            batch_end.strftime(
                                "%Y-%m-%d"
                            )
                        ),
                        branch_codes_tuple=tuple(
                            branch_codes
                        ),
                        authorization=authorization,
                    )
                )
            except requests.HTTPError as error:
                status_code = (
                    error.response.status_code
                    if error.response is not None
                    else "?"
                )

                st.error(
                    "API Production trả lỗi "
                    f"HTTP {status_code} cho batch "
                    f"{batch_start:%d/%m/%Y} → "
                    f"{batch_end:%d/%m/%Y}."
                )
                st.stop()

            except requests.RequestException as error:
                st.error(
                    "Không kết nối được API Production cho batch "
                    f"{batch_start:%d/%m/%Y} → "
                    f"{batch_end:%d/%m/%Y}."
                )
                st.exception(
                    error
                )
                st.stop()

            except Exception as error:
                st.error(
                    "Không đọc được response API Production."
                )
                st.exception(
                    error
                )
                st.stop()

            all_records.extend(
                records
            )

    return (
        all_records,
        window,
    )


# ============================================================
# CHUẨN HÓA RESPONSE API → FORMAT DASHBOARD
# ============================================================

def prepare_api_data(
    records,
):
    if not records:
        return pd.DataFrame()

    data = pd.DataFrame(
        records
    )

    # --------------------------------------------------------
    # 1. ĐỔI TÊN CỘT
    # --------------------------------------------------------

    data = data.rename(
        columns={
            "Số lệnh sửa chữa": "ro",
            "Ngày DT": "ngay_hoa_don",
            "Ngày quyết toán": "ngay_quyet_toan",
            "Ngày lập lệnh": "ngay_lap_lenh",
            "Trạng thái lệnh": "trang_thai",
            "Nguồn khách": "nguon_khach",
            "Hãng xe": "hang_xe",
            "Dòng xe": "dong_xe",
            "Khách hàng": "ten_khach_hang",
            "Doanh thu công việc": "doanh_thu_cong_viec",
            "Doanh thu phụ tùng": "doanh_thu_phu_tung",
            "Tổng doanh thu": "doanh_thu_truoc_thue",
            "Tổng thanh toán": "tong_tien_sau_thue",
            "Khách hàng (2)": "khach_hang_chi_tra",
            "Khách hàng.1": "khach_hang_chi_tra",
            "Bảo hiểm": "bao_hiem_chi_tra",
            "Chi nhánh": "xuong_dms",
        }
    )

    required_columns = [
        "ro",
        "ngay_hoa_don",
        "ngay_quyet_toan",
        "ngay_lap_lenh",
        "trang_thai",
        "nguon_khach",
        "hang_xe",
        "doanh_thu_cong_viec",
        "doanh_thu_phu_tung",
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "xuong_dms",
    ]

    for column in required_columns:
        if column not in data.columns:
            data[column] = pd.NA

    # --------------------------------------------------------
    # 2. RO
    # --------------------------------------------------------

    data["ro"] = (
        data["ro"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data["ro_key"] = (
        normalize_order_number(
            data["ro"]
        )
    )

    data = data[
        data["ro_key"].notna()
    ].copy()

    # API có thể trả:
    #   LSC.2026...
    #   CSHN.HY.LSC.2607...
    # nên tìm loại lệnh ở bất kỳ segment nào trong Số lệnh.
    data["loai_lenh"] = (
        data["ro_key"]
        .astype(str)
        .str.extract(
            r"(?:^|\.)(LSC|LPK|LPT)(?:\.|$)",
            expand=False,
        )
    )

    data = data[
        data["loai_lenh"].notna()
    ].copy()

    # --------------------------------------------------------
    # 3. NGÀY
    # --------------------------------------------------------

    for column in [
        "ngay_hoa_don",
        "ngay_quyet_toan",
        "ngay_lap_lenh",
    ]:
        data[column] = pd.to_datetime(
            data[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # 4. CHI NHÁNH / XƯỞNG
    # --------------------------------------------------------

    data["xuong_dms"] = (
        data["xuong_dms"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data["xuong"] = (
        data["xuong_dms"]
        .map(
            API_WORKSHOP_NAME_MAP
        )
        .fillna(
            data["xuong_dms"]
        )
    )

    data["chi_nhanh"] = (
        data["xuong_dms"]
        .map(
            API_WORKSHOP_BRANCH_MAP
        )
    )

    # --------------------------------------------------------
    # 5. CỘT TIỀN
    # --------------------------------------------------------

    money_columns = [
        "doanh_thu_cong_viec",
        "doanh_thu_phu_tung",
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "khach_hang_chi_tra",
        "bao_hiem_chi_tra",
    ]

    for column in money_columns:
        if column not in data.columns:
            data[column] = 0

        data[column] = parse_money(
            data[column]
        )

    # --------------------------------------------------------
    # 6. TRẠNG THÁI
    # --------------------------------------------------------

    data["trang_thai"] = (
        data["trang_thai"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 7. HÃNG XE
    # --------------------------------------------------------

    data["hang_xe"] = (
        data["hang_xe"]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.upper()
        .str.strip()
        .replace({
            "HUYNDAI": "HYUNDAI",
            "HYNDAI": "HYUNDAI",
            "MERCEDES BENZ": "MERCEDES-BENZ",
            "LYNK&CO": "LYNK & CO",
            "LYNK AND CO": "LYNK & CO",
        })
    )

    # --------------------------------------------------------
    # 8. NGUỒN KHÁCH
    # --------------------------------------------------------

    data["nguon_khach"] = (
        data["nguon_khach"]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.strip()
        .replace(
            "",
            "KHÔNG XÁC ĐỊNH",
        )
    )

    # --------------------------------------------------------
    # 9. DÒNG XE / KHÁCH HÀNG
    # --------------------------------------------------------

    if "dong_xe" not in data.columns:
        data["dong_xe"] = ""

    if "ten_khach_hang" not in data.columns:
        data["ten_khach_hang"] = ""

    return data.reset_index(
        drop=True
    )


# ============================================================
# LỌC CHÍNH THỨC THEO NGÀY DT
# ============================================================

def filter_by_dashboard_period(
    data,
    year,
    month,
):
    if data.empty:
        return data

    data = data[
        data["ngay_hoa_don"].notna()
    ].copy()

    data = data[
        data["ngay_hoa_don"].dt.year
        == int(year)
    ].copy()

    if month != "All":
        data = data[
            data["ngay_hoa_don"].dt.month
            == int(month)
        ].copy()

    # Nếu API raw có một RO lặp lại do nguồn trả trùng,
    # chỉ giữ bản ghi cuối cùng sau khi sort theo Ngày DT.
    data = (
        data.sort_values(
            [
                "ngay_hoa_don",
                "ngay_quyet_toan",
            ],
            na_position="first",
        )
        .drop_duplicates(
            subset=["ro_key"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    return data


# ============================================================
# LOAD TOÀN BỘ DỮ LIỆU CHO DASHBOARD
# ============================================================

def load_all_data(
    selected_branch,
    selected_workshop,
    year,
    month,
):
    records, window = call_api_raw(
        selected_branch=selected_branch,
        selected_workshop=selected_workshop,
        year=year,
        month=month,
    )

    raw_data = prepare_api_data(
        records
    )

    if raw_data.empty:
        st.warning(
            "API không trả dữ liệu cho phạm vi đã chọn."
        )

        data_raw = raw_data
    else:
        data_raw = filter_by_dashboard_period(
            data=raw_data,
            year=year,
            month=month,
        )

    # Giữ 3 output để calculations/app hiện tại tương thích.
    parts_data = {}
    accessory_data = {}

    return (
        data_raw,
        parts_data,
        accessory_data,
    )
