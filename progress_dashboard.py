# ============================================================
# progress_dashboard.py
# GIAO DIỆN BẢNG THEO DÕI TIẾN ĐỘ SỬA CHỮA
# ============================================================

import html
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st

from progress_data_loader import load_progress_data


# ============================================================
# 1. COLOR
# ============================================================

NAVY = "#0B2A52"
BLUE = "#3478F6"
GREEN = "#20A779"
ORANGE = "#F59E0B"
RED = "#E85454"
PURPLE = "#7457D9"
TEAL = "#1697A6"
SLATE = "#65758B"


# ============================================================
# 2. TEXT NORMALIZATION
# ============================================================

def _norm(value):
    if pd.isna(value):
        return ""

    text = str(value).strip().upper()
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(r"\s+", " ", text)
    return text


def _contains(series, keyword):
    key = _norm(keyword)

    normalized = (
        series.fillna("")
        .astype(str)
        .map(_norm)
    )

    return normalized.str.contains(
        re.escape(key),
        regex=True,
        na=False,
    )


def _is_tasco(series):
    return _contains(series, "TASCO")


# ============================================================
# 3. DEDUP / FILTER
# ============================================================

def _latest_order_rows(data):
    """
    Một lệnh có thể xuất hiện nhiều dòng trong Google Sheet.
    Dashboard KPI cấp xe/lệnh phải tính 1 lần / Số lệnh.
    """

    if data.empty:
        return data.copy()

    result = data.copy()

    # Sort theo thời điểm mới nhất có thể.
    sort_columns = [
        c for c in [
            "thoi_gian_giao_xe",
            "ngay_hoa_don",
            "ngay_quyet_toan",
            "thoi_gian_tao",
        ]
        if c in result.columns
    ]

    if sort_columns:
        result = result.sort_values(
            sort_columns,
            na_position="first",
        )

    return (
        result.drop_duplicates(
            subset=["so_lenh"],
            keep="last",
        )
        .reset_index(drop=True)
    )


def _month_options(data):
    values = (
        data.get("month_key", pd.Series(dtype="object"))
        .fillna("")
        .astype(str)
    )

    values = sorted(
        [v for v in values.unique() if v],
        reverse=True,
    )

    return values


def _month_label(month_key):
    try:
        year, month = month_key.split("-")
        return f"T{int(month)}/{year}"
    except Exception:
        return month_key


def _apply_progress_filters(
    data,
    selected_month,
    selected_workshop,
    selected_brand,
    selected_repair_type,
):
    filtered = data.copy()

    if selected_month != "Tất cả":
        filtered = filtered[
            filtered["month_key"] == selected_month
        ].copy()

    if selected_workshop != "Tất cả":
        filtered = filtered[
            filtered["xuong_dich_vu"] == selected_workshop
        ].copy()

    if selected_brand != "Tất cả":
        filtered = filtered[
            filtered["hang_xe"] == selected_brand
        ].copy()

    if selected_repair_type != "Tất cả":
        filtered = filtered[
            filtered["loai_hinh_sua_chua"]
            == selected_repair_type
        ].copy()

    return filtered


# ============================================================
# 4. KPI CALCULATION
# ============================================================

def calculate_progress_metrics(data):
    orders = _latest_order_rows(data)

    if orders.empty:
        return {
            "received": 0,
            "delivered": 0,
            "late_delivery": 0,
            "not_delivered": 0,
            "waiting_delivery": 0,
            "late_progress": 0,
            "stopped": 0,
            "waiting_parts": 0,
            "rework": 0,
            "tasco_inspection": 0,
            "other_inspection": 0,
            "tasco_price": 0,
            "other_insurance": 0,
        }

    stage = orders["cong_doan"]
    repair_status = orders["trang_thai_sua_chua"]
    abnormal = orders["cac_bat_thuong"]
    insurer = orders["bao_hiem"]
    delivery_status = orders["trang_thai_giao_xe"]

    delivered_mask = (
        _contains(delivery_status, "DA GIAO")
        & ~_contains(delivery_status, "CHUA GIAO")
    )

    not_delivered_mask = (
        _contains(delivery_status, "CHUA GIAO")
        | (
            delivery_status.fillna("").astype(str).str.strip().eq("")
            & orders["thoi_gian_giao_xe"].isna()
        )
    )

    # Giao trễ: ưu tiên so sánh actual vs promised;
    # đồng thời bắt các status có chữ trễ.
    late_delivery_mask = _contains(
        delivery_status,
        "TRE",
    )

    has_dates = (
        orders["thoi_gian_giao_xe"].notna()
        & orders["thoi_gian_hen_giao"].notna()
    )

    late_delivery_mask = (
        late_delivery_mask
        | (
            has_dates
            & (
                orders["thoi_gian_giao_xe"]
                > orders["thoi_gian_hen_giao"]
            )
        )
    )

    inspection_mask = _contains(
        stage,
        "GIAM DINH",
    )

    approval_mask = (
        _contains(stage, "CHO DUYET")
        | _contains(stage, "DUYET SC")
        | _contains(stage, "DUYET GIA")
    )

    insurer_nonempty = (
        insurer.fillna("")
        .astype(str)
        .str.strip()
        .ne("")
    )

    tasco_mask = _is_tasco(insurer)

    metrics = {
        "received": int(orders["so_lenh"].nunique()),
        "delivered": int(delivered_mask.sum()),
        "late_delivery": int(late_delivery_mask.sum()),
        "not_delivered": int(not_delivered_mask.sum()),
        "waiting_delivery": int(
            _contains(stage, "CHO GIAO XE").sum()
        ),
        "late_progress": int(
            _contains(repair_status, "TRE TIEN DO").sum()
        ),
        "stopped": int(
            (
                _contains(stage, "DUNG CONG VIEC")
                | _contains(stage, "DUNG SUA CHUA")
            ).sum()
        ),
        "waiting_parts": int(
            (
                _contains(stage, "CHO PHU TUNG")
                | _contains(abnormal, "CHO PHU TUNG")
                | _contains(abnormal, "THIEU PHU TUNG")
            ).sum()
        ),
        "rework": int(
            (
                _contains(abnormal, "SUA CHUA LAI")
                | _contains(repair_status, "SUA CHUA LAI")
            ).sum()
        ),
        "tasco_inspection": int(
            (inspection_mask & tasco_mask).sum()
        ),
        "other_inspection": int(
            (
                inspection_mask
                & insurer_nonempty
                & ~tasco_mask
            ).sum()
        ),
        "tasco_price": int(
            (approval_mask & tasco_mask).sum()
        ),
        "other_insurance": int(
            (
                approval_mask
                & insurer_nonempty
                & ~tasco_mask
            ).sum()
        ),
    }

    return metrics


# ============================================================
# 5. TABLE CALCULATION
# ============================================================

WAITING_STAGE_KEYWORDS = [
    "CHO",
    "DUNG",
]


REPAIRING_STAGE_KEYWORDS = [
    "DANG",
    "KIEM TRA",
    "CHAN DOAN",
    "LAP RAP",
]


def _stage_summary(data, mode):
    orders = _latest_order_rows(data)

    if orders.empty:
        return []

    stage = (
        orders["cong_doan"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    stage_norm = stage.map(_norm)

    if mode == "waiting":
        mask = stage_norm.map(
            lambda value:
            any(
                keyword in value
                for keyword in WAITING_STAGE_KEYWORDS
            )
            and "DANG" not in value
        )
    else:
        mask = stage_norm.map(
            lambda value:
            any(
                keyword in value
                for keyword in REPAIRING_STAGE_KEYWORDS
            )
            and "CHO" not in value
        )

    selected = orders.loc[mask].copy()

    if selected.empty:
        return [("Tổng cộng", 0)]

    grouped = (
        selected.groupby(
            "cong_doan",
            dropna=False,
        )["so_lenh"]
        .nunique()
        .sort_values(
            ascending=False
        )
    )

    rows = [
        (str(name), int(value))
        for name, value in grouped.items()
        if str(name).strip()
    ]

    total = int(
        selected["so_lenh"].nunique()
    )

    return [
        ("Tổng cộng", total),
        *rows[:7],
    ]


def _abnormal_summary(data):
    orders = _latest_order_rows(data)

    if orders.empty:
        return []

    abnormal = (
        orders["cac_bat_thuong"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    selected = orders[
        abnormal.ne("")
    ].copy()

    if selected.empty:
        return []

    grouped = (
        selected.groupby(
            "cac_bat_thuong",
            dropna=False,
        )["so_lenh"]
        .nunique()
        .sort_values(
            ascending=False
        )
    )

    return [
        (str(name), int(value))
        for name, value in grouped.items()
        if str(name).strip()
    ][:8]


# ============================================================
# 6. CSS
# ============================================================

def apply_progress_style():
    st.markdown(
        """
        <style>
        .progress-top-shell {
            background:
                linear-gradient(
                    135deg,
                    #FFFFFF 0%,
                    #F7FAFE 100%
                );
            border:1px solid #E7ECF3;
            border-radius:20px;
            padding:24px 26px 20px 26px;
            margin:4px 0 18px 0;
            box-shadow:0 5px 22px rgba(26,47,81,.045);
        }

        .progress-title {
            color:#0B2A52;
            font-size:30px;
            line-height:1.15;
            font-weight:900;
            letter-spacing:-0.55px;
            margin-bottom:7px;
        }

        .progress-subtitle {
            color:#667085;
            font-size:14px;
            font-weight:500;
        }

        .progress-meta {
            margin-top:10px;
            color:#98A2B3;
            font-size:11.5px;
            font-weight:600;
        }

        .progress-section-title {
            color:#173359;
            font-size:18px;
            font-weight:850;
            margin:21px 0 12px 0;
        }

        .progress-kpi-card {
            position:relative;
            background:#FFFFFF;
            border:1px solid #E7ECF3;
            border-radius:15px;
            min-height:112px;
            padding:17px;
            box-sizing:border-box;
            display:flex;
            align-items:center;
            gap:14px;
            overflow:hidden;
            box-shadow:0 4px 15px rgba(26,47,81,.045);
        }

        .progress-kpi-topline {
            position:absolute;
            top:0;
            left:0;
            right:0;
            height:3px;
        }

        .progress-kpi-icon {
            min-width:48px;
            width:48px;
            height:48px;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:21px;
            font-weight:850;
        }

        .progress-kpi-label {
            color:#667085;
            font-size:12px;
            font-weight:650;
            line-height:1.2;
            margin-bottom:4px;
        }

        .progress-kpi-value {
            font-size:32px;
            line-height:1;
            font-weight:900;
            letter-spacing:-.7px;
        }

        .progress-detail-card {
            background:#FFFFFF;
            border:1px solid #E7ECF3;
            border-radius:15px;
            overflow:hidden;
            min-height:390px;
            box-shadow:0 4px 16px rgba(20,40,80,.045);
        }

        .progress-detail-header {
            padding:15px 16px;
            border-bottom:1px solid #EEF1F5;
            color:#173359;
            font-size:13px;
            font-weight:850;
        }

        .progress-table-wrap {
            padding:6px 14px 14px 14px;
        }

        .progress-table {
            width:100%;
            border-collapse:collapse;
            table-layout:fixed;
        }

        .progress-table th {
            text-align:left;
            color:#98A2B3;
            font-size:9px;
            font-weight:850;
            padding:8px 7px;
            border-bottom:1px solid #EEF1F5;
        }

        .progress-table td {
            padding:8px 7px;
            color:#344054;
            font-size:11px;
            border-bottom:1px solid #F2F4F7;
            vertical-align:middle;
        }

        .progress-table td:last-child,
        .progress-table th:last-child {
            text-align:right;
            width:70px;
        }

        .progress-table td:last-child {
            color:#175CD3;
            font-weight:850;
        }

        div[data-testid="stSelectbox"] label {
            color:#667085 !important;
            font-weight:650 !important;
            font-size:12px !important;
        }

        div[data-testid="stSelectbox"]
        div[data-baseweb="select"] > div {
            min-height:43px;
            border-radius:11px;
            border:1px solid #E1E7EF;
            background:#FFFFFF;
        }

        div[data-testid="stSegmentedControl"] {
            margin-bottom:10px;
        }

        @media (max-width:1100px) {
            .progress-title {
                font-size:25px;
            }

            .progress-kpi-value {
                font-size:27px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. HTML COMPONENTS
# ============================================================

def _rgba(hex_color, alpha=0.11):
    value = hex_color.lstrip("#")
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _metric_card(title, value, icon, color):
    return f"""
    <div class="progress-kpi-card">
        <div
            class="progress-kpi-topline"
            style="background:{color};">
        </div>
        <div
            class="progress-kpi-icon"
            style="
                color:{color};
                background:{_rgba(color)};
            ">
            {icon}
        </div>
        <div>
            <div class="progress-kpi-label">
                {html.escape(str(title))}
            </div>
            <div
                class="progress-kpi-value"
                style="color:{color};">
                {int(value):,}
            </div>
        </div>
    </div>
    """


def _render_metric(title, value, icon, color):
    st.markdown(
        _metric_card(
            title,
            value,
            icon,
            color,
        ),
        unsafe_allow_html=True,
    )


def _detail_card(title, rows, value_header, abnormal=False):
    # IMPORTANT:
    # HTML phải không có indent 4 spaces ở đầu dòng.
    # Nếu có, Markdown sẽ render thành code block (<tr> ...),
    # đúng lỗi đang thấy trên Streamlit.

    if not rows:
        body = (
            '<tr>'
            '<td colspan="3" '
            'style="text-align:center;color:#98A2B3;padding:28px 8px;">'
            'Không có dữ liệu'
            '</td>'
            '</tr>'
        )
    else:
        row_parts = []

        for index, (label, value) in enumerate(rows, start=1):
            row_parts.append(
                '<tr>'
                f'<td style="width:26px;color:#98A2B3;">{index}</td>'
                f'<td>{html.escape(str(label))}</td>'
                f'<td>{int(value):,}</td>'
                '</tr>'
            )

        body = "".join(row_parts)

    first_header = (
        "CÁC BẤT THƯỜNG"
        if abnormal
        else "CÔNG ĐOẠN"
    )

    return (
        '<div class="progress-detail-card">'
        '<div class="progress-detail-header">'
        f'{html.escape(title)}'
        '</div>'
        '<div class="progress-table-wrap">'
        '<table class="progress-table">'
        '<thead>'
        '<tr>'
        '<th style="width:26px;">#</th>'
        f'<th>{first_header}</th>'
        f'<th>{html.escape(value_header)}</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{body}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


# ============================================================
# 8. VIEW SELECTOR
# ============================================================



# ============================================================
# 9. MAIN
# ============================================================

def render_progress_dashboard(
    selected_branch="All",
    initial_workshop="All",
):
    apply_progress_style()

    branch_label = (
        "Toàn hệ thống"
        if selected_branch == "All"
        else f"CN {selected_branch}"
    )

    # --------------------------------------------------------
    # LOAD GOOGLE SHEET
    # --------------------------------------------------------
    with st.spinner(
        "Đang tải Bảng tiến độ..."
    ):
        try:
            raw = load_progress_data(
                selected_branch=selected_branch,
            )
        except Exception as exc:
            st.error(
                "Không tải được dữ liệu Bảng tiến độ."
            )
            st.code(str(exc))
            st.info(
                "Nếu file Google Sheet đang để Restricted, "
                "hãy share file cho service-account email của Streamlit "
                "hoặc bật 'Anyone with the link – Viewer'."
            )
            return

    errors = raw.attrs.get(
        "load_errors",
        [],
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------
    st.markdown(
        f"""
        <div class="progress-top-shell">
            <div class="progress-title">
                Bảng theo dõi tiến độ sửa chữa – {html.escape(branch_label)}
            </div>
            <div class="progress-subtitle">
                Theo dõi tình trạng xe, tiến độ sửa chữa,
                công đoạn chờ và các bất thường vận hành
            </div>
            <div class="progress-meta">
                Google Sheet gần real-time · Cache 60 giây ·
                Cập nhật giao diện lúc {datetime.now():%d/%m/%Y %H:%M}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if errors:
        with st.expander(
            f"⚠️ Có {len(errors)} chi nhánh chưa tải được",
            expanded=False,
        ):
            for item in errors:
                st.write(item)

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------
    month_keys = _month_options(raw)
    month_label_map = {
        _month_label(key): key
        for key in month_keys
    }

    month_labels = [
        "Tất cả",
        *month_label_map.keys(),
    ]

    workshops = sorted(
        [
            value
            for value in raw[
                "xuong_dich_vu"
            ].dropna().astype(str).str.strip().unique()
            if value
        ]
    )

    brands = sorted(
        [
            value
            for value in raw[
                "hang_xe"
            ].dropna().astype(str).str.strip().unique()
            if value
        ]
    )

    repair_types = sorted(
        [
            value
            for value in raw[
                "loai_hinh_sua_chua"
            ].dropna().astype(str).str.strip().unique()
            if value
        ]
    )

    default_workshop_index = 0

    if (
        initial_workshop
        and initial_workshop != "All"
        and initial_workshop in workshops
    ):
        default_workshop_index = (
            ["Tất cả", *workshops]
            .index(initial_workshop)
        )

    f1, f2, f3, f4 = st.columns(
        4,
        gap="medium",
    )

    with f1:
        selected_month_label = st.selectbox(
            "📅 Tháng lập lệnh",
            month_labels,
            index=0,
            key="progress_month_filter",
        )

    with f2:
        selected_workshop = st.selectbox(
            "🔧 Xưởng dịch vụ",
            ["Tất cả", *workshops],
            index=default_workshop_index,
            key="progress_workshop_filter",
        )

    with f3:
        selected_brand = st.selectbox(
            "🚘 Hãng xe",
            ["Tất cả", *brands],
            index=0,
            key="progress_brand_filter",
        )

    with f4:
        selected_repair_type = st.selectbox(
            "📋 Loại hình sửa chữa",
            ["Tất cả", *repair_types],
            index=0,
            key="progress_repair_type_filter",
        )

    selected_month = (
        "Tất cả"
        if selected_month_label == "Tất cả"
        else month_label_map[
            selected_month_label
        ]
    )

    data = _apply_progress_filters(
        raw,
        selected_month=selected_month,
        selected_workshop=selected_workshop,
        selected_brand=selected_brand,
        selected_repair_type=selected_repair_type,
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------
    metrics = calculate_progress_metrics(
        data
    )

    st.markdown(
        '<div class="progress-section-title">Tổng quan tiến độ</div>',
        unsafe_allow_html=True,
    )

    row1 = st.columns(5, gap="medium")

    with row1[0]:
        _render_metric(
            "Tổng số xe đã nhận",
            metrics["received"],
            "▤",
            BLUE,
        )

    with row1[1]:
        _render_metric(
            "Tổng số xe đã giao",
            metrics["delivered"],
            "✓",
            GREEN,
        )

    with row1[2]:
        _render_metric(
            "Tổng xe giao trễ hẹn",
            metrics["late_delivery"],
            "◷",
            ORANGE,
        )

    with row1[3]:
        _render_metric(
            "Tổng xe chưa giao",
            metrics["not_delivered"],
            "🚗",
            RED,
        )

    with row1[4]:
        _render_metric(
            "Tổng xe chờ giao",
            metrics["waiting_delivery"],
            "▣",
            PURPLE,
        )

    st.markdown(
        "<div style='height:12px'></div>",
        unsafe_allow_html=True,
    )

    row2 = st.columns(4, gap="medium")

    with row2[0]:
        _render_metric(
            "Tổng xe trễ tiến độ",
            metrics["late_progress"],
            "⌛",
            ORANGE,
        )

    with row2[1]:
        _render_metric(
            "Tổng xe dừng sửa chữa",
            metrics["stopped"],
            "Ⅱ",
            SLATE,
        )

    with row2[2]:
        _render_metric(
            "Tổng xe chờ phụ tùng",
            metrics["waiting_parts"],
            "◆",
            BLUE,
        )

    with row2[3]:
        _render_metric(
            "Tổng xe sửa chữa lại",
            metrics["rework"],
            "↻",
            PURPLE,
        )

    st.markdown(
        "<div style='height:12px'></div>",
        unsafe_allow_html=True,
    )

    row3 = st.columns(4, gap="medium")

    with row3[0]:
        _render_metric(
            "Chờ giám định Tasco",
            metrics["tasco_inspection"],
            "♙",
            BLUE,
        )

    with row3[1]:
        _render_metric(
            "Chờ giám định BH khác",
            metrics["other_inspection"],
            "♢",
            TEAL,
        )

    with row3[2]:
        _render_metric(
            "Chờ duyệt giá Tasco",
            metrics["tasco_price"],
            "▧",
            ORANGE,
        )

    with row3[3]:
        _render_metric(
            "Chờ duyệt BH khác",
            metrics["other_insurance"],
            "▤",
            RED,
        )

    # --------------------------------------------------------
    # DETAIL TABLES
    # --------------------------------------------------------
    waiting_rows = _stage_summary(
        data,
        mode="waiting",
    )

    repairing_rows = _stage_summary(
        data,
        mode="repairing",
    )

    abnormal_rows = _abnormal_summary(
        data
    )

    st.markdown(
        '<div class="progress-section-title">Chi tiết vận hành</div>',
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(
        3,
        gap="medium",
    )

    with d1:
        st.markdown(
            _detail_card(
                "◷  Công đoạn – SL xe chờ",
                waiting_rows,
                "SL XE CHỜ",
            ),
            unsafe_allow_html=True,
        )

    with d2:
        st.markdown(
            _detail_card(
                "🔧  Công đoạn – SL xe đang sửa chữa",
                repairing_rows,
                "SL XE",
            ),
            unsafe_allow_html=True,
        )

    with d3:
        st.markdown(
            _detail_card(
                "⚠  Các bất thường – Tổng SL xe",
                abnormal_rows,
                "TỔNG SL XE",
                abnormal=True,
            ),
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # RAW DETAIL
    # --------------------------------------------------------
    with st.expander(
        "Xem dữ liệu chi tiết Bảng tiến độ"
    ):
        display_columns = [
            c for c in [
                "chi_nhanh",
                "xuong_dich_vu",
                "so_lenh",
                "bien_so_xe",
                "hang_xe",
                "loai_hinh_sua_chua",
                "cong_doan",
                "trang_thai_sua_chua",
                "cac_bat_thuong",
                "bao_hiem",
                "thoi_gian_hen_giao",
                "thoi_gian_giao_xe",
                "trang_thai_giao_xe",
            ]
            if c in data.columns
        ]

        st.dataframe(
            data[display_columns],
            use_container_width=True,
            hide_index=True,
        )
