from datetime import date

import pandas as pd
import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Test API Production - Carpla",
    layout="wide",
)


# ============================================================
# API PRODUCTION
# ============================================================

API_URL = (
    "https://synerlynk.carpla.vn/"
    "api/report.repair.order.api/"
    "method_not_record/get_repair_order_report"
)


# ============================================================
# TITLE
# ============================================================

st.title("Test API DMS - Carpla")

st.caption(
    "Môi trường PRODUCTION - dữ liệu thật"
)


# ============================================================
# INPUT
# ============================================================

date_from = st.date_input(
    "Từ ngày",
    value=date(2026, 7, 1),
)

date_to = st.date_input(
    "Đến ngày",
    value=date(2026, 7, 31),
)

branch_codes_text = st.text_input(
    "Branch codes",
    value="CSHN.HY",
    help=(
        "Nếu nhiều mã xưởng, nhập cách nhau bằng dấu phẩy. "
        "Ví dụ: CSHN.HY, CSHN.LB"
    ),
)


# ============================================================
# HÀM CHUYỂN BRANCH CODES
# ============================================================

def parse_branch_codes(text):
    return [
        code.strip()
        for code in text.split(",")
        if code.strip()
    ]


# ============================================================
# HÀM TÌM DATA TRONG RESPONSE
# ============================================================

def extract_records(response_json):
    """
    API hiện tại trả cấu trúc:

    {
        "success": {
            ...
            "data": [...]
        }
    }

    Hàm này cố gắng lấy list record một cách an toàn.
    """

    if not isinstance(
        response_json,
        dict,
    ):
        return []

    success_data = response_json.get(
        "success"
    )

    if isinstance(
        success_data,
        dict,
    ):
        records = success_data.get(
            "data"
        )

        if isinstance(
            records,
            list,
        ):
            return records

    records = response_json.get(
        "data"
    )

    if isinstance(
        records,
        list,
    ):
        return records

    return []


# ============================================================
# TEST BUTTON
# ============================================================

if st.button(
    "Test API Production",
    type="primary",
):

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if date_from > date_to:
        st.error(
            "Từ ngày không được lớn hơn Đến ngày."
        )
        st.stop()

    branch_codes = parse_branch_codes(
        branch_codes_text
    )

    if not branch_codes:
        st.error(
            "Bạn cần nhập ít nhất 1 branch code."
        )
        st.stop()

    # --------------------------------------------------------
    # LẤY AUTHORIZATION TỪ STREAMLIT SECRETS
    # --------------------------------------------------------

    try:
        authorization = (
            st.secrets["api"]["authorization"]
        )

    except Exception:
        st.error(
            "Chưa cấu hình Authorization "
            "trong Streamlit Secrets."
        )

        st.info(
            'Vào Manage app → Settings → Secrets và thêm:\n\n'
            '[api]\n'
            'authorization = "AUTH_KEY_PRODUCTION"'
        )

        st.stop()

    # --------------------------------------------------------
    # COOKIE - KHÔNG BẮT BUỘC
    # --------------------------------------------------------

    cookie = ""

    try:
        cookie = (
            st.secrets["api"].get(
                "cookie",
                "",
            )
        )

    except Exception:
        cookie = ""

    # --------------------------------------------------------
    # HEADERS
    # --------------------------------------------------------

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    if cookie:
        headers["Cookie"] = cookie

    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload = {
        "date_from": (
            date_from.strftime(
                "%Y-%m-%d"
            )
        ),
        "date_to": (
            date_to.strftime(
                "%Y-%m-%d"
            )
        ),
        "branch_ids": [],
        "branch_codes": branch_codes,
    }

    # --------------------------------------------------------
    # HIỂN THỊ REQUEST
    # --------------------------------------------------------

    st.subheader(
        "Request"
    )

    st.json(
        payload
    )

    # --------------------------------------------------------
    # CALL API
    # --------------------------------------------------------

    try:

        with st.spinner(
            "Đang gọi API Production..."
        ):

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=120,
            )

    except requests.Timeout:

        st.error(
            "API bị timeout."
        )

        st.stop()

    except requests.ConnectionError as error:

        st.error(
            "Streamlit không kết nối được tới API Production."
        )

        st.exception(
            error
        )

        st.stop()

    except requests.RequestException as error:

        st.error(
            "Có lỗi khi gọi API."
        )

        st.exception(
            error
        )

        st.stop()

    # --------------------------------------------------------
    # HTTP STATUS
    # --------------------------------------------------------

    st.subheader(
        "HTTP Status"
    )

    if response.status_code == 200:

        st.success(
            "API PRODUCTION OK - Status 200"
        )

    else:

        st.error(
            f"API lỗi - Status {response.status_code}"
        )

        st.markdown(
            "### Response"
        )

        st.code(
            response.text
        )

        st.stop()

    # --------------------------------------------------------
    # CONVERT JSON
    # --------------------------------------------------------

    try:

        response_json = (
            response.json()
        )

    except ValueError:

        st.error(
            "API không trả dữ liệu JSON."
        )

        st.code(
            response.text
        )

        st.stop()

    # --------------------------------------------------------
    # RESPONSE TYPE
    # --------------------------------------------------------

    st.subheader(
        "Response type"
    )

    st.write(
        type(
            response_json
        ).__name__
    )

    # --------------------------------------------------------
    # TOP LEVEL KEYS
    # --------------------------------------------------------

    if isinstance(
        response_json,
        dict,
    ):

        st.subheader(
            "Top-level keys"
        )

        st.write(
            list(
                response_json.keys()
            )
        )

    # --------------------------------------------------------
    # SUCCESS INFO
    # --------------------------------------------------------

    success_data = None

    if isinstance(
        response_json,
        dict,
    ):

        success_data = (
            response_json.get(
                "success"
            )
        )

    if isinstance(
        success_data,
        dict,
    ):

        info_columns = st.columns(
            4
        )

        with info_columns[0]:
            st.metric(
                "Date from",
                success_data.get(
                    "date_from",
                    "—",
                ),
            )

        with info_columns[1]:
            st.metric(
                "Date to",
                success_data.get(
                    "date_to",
                    "—",
                ),
            )

        with info_columns[2]:
            st.metric(
                "Total count",
                success_data.get(
                    "total_count",
                    0,
                ),
            )

        with info_columns[3]:

            branch_ids = (
                success_data.get(
                    "branch_ids",
                    [],
                )
            )

            st.metric(
                "Branch IDs",
                str(
                    branch_ids
                ),
            )

    # --------------------------------------------------------
    # LẤY DATA RECORDS
    # --------------------------------------------------------

    records = extract_records(
        response_json
    )

    st.subheader(
        "Records"
    )

    st.write(
        f"Số record nhận được: {len(records):,}"
    )

    # --------------------------------------------------------
    # KHÔNG CÓ DATA
    # --------------------------------------------------------

    if not records:

        st.warning(
            "API trả Status 200 nhưng không có record."
        )

        st.markdown(
            "### Full response"
        )

        st.json(
            response_json
        )

        st.stop()

    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(
        records
    )

    # --------------------------------------------------------
    # FIELD LIST
    # --------------------------------------------------------

    st.subheader(
        "Field API trả về"
    )

    st.write(
        list(
            df.columns
        )
    )

    # --------------------------------------------------------
    # KIỂM TRA CÁC FIELD QUAN TRỌNG
    # --------------------------------------------------------

    st.subheader(
        "Kiểm tra field Dashboard"
    )

    expected_fields = [
        "Số lệnh sửa chữa",
        "Ngày lập lệnh",
        "Ngày quyết toán",
        "Ngày DT",
        "Trạng thái lệnh",
        "Nguồn khách",
        "Hãng xe",
        "Dòng xe",
        "Khách hàng",
        "Doanh thu công việc",
        "Doanh thu phụ tùng",
        "Tổng doanh thu",
        "Tổng thanh toán",
        "Khách hàng (2)",
        "Bảo hiểm",
        "Chi nhánh",
    ]

    field_check = []

    for field in expected_fields:

        field_check.append(
            {
                "Field": field,
                "Có trong API": (
                    "Có"
                    if field in df.columns
                    else "Thiếu"
                ),
            }
        )

    field_check_df = pd.DataFrame(
        field_check
    )

    st.dataframe(
        field_check_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # KIỂM TRA NGÀY DT
    # --------------------------------------------------------

    if "Ngày DT" in df.columns:

        st.subheader(
            "Kiểm tra Ngày DT"
        )

        ngay_dt = pd.to_datetime(
            df["Ngày DT"],
            errors="coerce",
        )

        total_records = len(
            df
        )

        null_ngay_dt = (
            ngay_dt.isna().sum()
        )

        valid_ngay_dt = (
            ngay_dt.notna().sum()
        )

        dt_cols = st.columns(
            3
        )

        with dt_cols[0]:

            st.metric(
                "Tổng record",
                f"{total_records:,}",
            )

        with dt_cols[1]:

            st.metric(
                "Có Ngày DT",
                f"{valid_ngay_dt:,}",
            )

        with dt_cols[2]:

            st.metric(
                "Ngày DT null",
                f"{null_ngay_dt:,}",
            )

        if valid_ngay_dt > 0:

            st.write(
                "Ngày DT nhỏ nhất:",
                ngay_dt.min(),
            )

            st.write(
                "Ngày DT lớn nhất:",
                ngay_dt.max(),
            )

    # --------------------------------------------------------
    # KIỂM TRA RO UNIQUE
    # --------------------------------------------------------

    if "Số lệnh sửa chữa" in df.columns:

        st.subheader(
            "Kiểm tra RO"
        )

        ro_series = (
            df[
                "Số lệnh sửa chữa"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        ro_series = (
            ro_series[
                ro_series != ""
            ]
        )

        total_rows = len(
            df
        )

        unique_ro = (
            ro_series.nunique()
        )

        duplicate_rows = (
            total_rows
            - unique_ro
        )

        ro_cols = st.columns(
            3
        )

        with ro_cols[0]:

            st.metric(
                "Số dòng",
                f"{total_rows:,}",
            )

        with ro_cols[1]:

            st.metric(
                "RO unique",
                f"{unique_ro:,}",
            )

        with ro_cols[2]:

            st.metric(
                "Dòng có thể trùng RO",
                f"{duplicate_rows:,}",
            )

    # --------------------------------------------------------
    # KIỂM TRA DOANH THU
    # --------------------------------------------------------

    revenue_fields = [
        "Doanh thu công việc",
        "Doanh thu phụ tùng",
        "Tổng doanh thu",
        "Tổng thanh toán",
    ]

    available_revenue_fields = [
        field
        for field in revenue_fields
        if field in df.columns
    ]

    if available_revenue_fields:

        st.subheader(
            "Kiểm tra doanh thu"
        )

        revenue_summary = []

        for field in (
            available_revenue_fields
        ):

            values = pd.to_numeric(
                df[field],
                errors="coerce",
            ).fillna(0)

            revenue_summary.append(
                {
                    "Chỉ tiêu": field,
                    "Tổng": values.sum(),
                    "Số dòng âm": (
                        values < 0
                    ).sum(),
                    "Số dòng = 0": (
                        values == 0
                    ).sum(),
                }
            )

        revenue_summary_df = (
            pd.DataFrame(
                revenue_summary
            )
        )

        st.dataframe(
            revenue_summary_df,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # RECORD ĐẦU TIÊN
    # --------------------------------------------------------

    st.subheader(
        "Record đầu tiên"
    )

    st.json(
        records[0]
    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.subheader(
        "Preview dữ liệu"
    )

    st.dataframe(
        df.head(
            100
        ),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # CHỈ HIỂN THỊ CỘT QUAN TRỌNG
    # --------------------------------------------------------

    important_columns = [
        column
        for column in [
            "Số lệnh sửa chữa",
            "Ngày lập lệnh",
            "Ngày quyết toán",
            "Ngày DT",
            "Trạng thái lệnh",
            "Nguồn khách",
            "Hãng xe",
            "Dòng xe",
            "Doanh thu công việc",
            "Doanh thu phụ tùng",
            "Tổng doanh thu",
            "Tổng thanh toán",
            "Khách hàng (2)",
            "Bảo hiểm",
            "Chi nhánh",
        ]
        if column in df.columns
    ]

    if important_columns:

        st.subheader(
            "Preview các cột dùng cho Dashboard"
        )

        st.dataframe(
            df[
                important_columns
            ].head(
                100
            ),
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # FULL RESPONSE
    # --------------------------------------------------------

    with st.expander(
        "Xem full JSON response"
    ):

        st.json(
            response_json
        )
