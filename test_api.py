import json

import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Test API - Carpla",
    layout="wide",
)


# ============================================================
# API DEV
# ============================================================

API_URL = (
    "https://dev-synerlynk.carpla.vn/"
    "api/report.repair.order.api/"
    "method_not_record/get_repair_order_report"
)


# ============================================================
# TITLE
# ============================================================

st.title("Test API DMS - Carpla")

st.caption(
    "Môi trường DEV - dữ liệu test"
)


# ============================================================
# INPUT
# ============================================================

date_from = st.date_input(
    "Từ ngày",
    value="2026-07-01",
)

date_to = st.date_input(
    "Đến ngày",
    value="2026-07-31",
)

branch_codes_text = st.text_input(
    "Branch codes",
    value="CSHN.HY",
    help="Nếu nhiều mã, nhập cách nhau bằng dấu phẩy",
)


# ============================================================
# TEST BUTTON
# ============================================================

if st.button(
    "Test API",
    type="primary",
):

    # --------------------------------------------------------
    # LẤY SECRET
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
        st.stop()

    cookie = ""

    try:
        cookie = (
            st.secrets["api"].get(
                "cookie",
                "",
            )
        )

    except Exception:
        pass

    # --------------------------------------------------------
    # BRANCH CODES
    # --------------------------------------------------------

    branch_codes = [
        code.strip()
        for code
        in branch_codes_text.split(",")
        if code.strip()
    ]

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
            "Đang gọi API..."
        ):

            response = (
                requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
            )

    except requests.RequestException as error:

        st.error(
            "Không kết nối được API."
        )

        st.exception(
            error
        )

        st.stop()

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    st.subheader(
        "HTTP Status"
    )

    if response.status_code == 200:
        st.success(
            f"API OK - Status {response.status_code}"
        )

    else:
        st.error(
            f"API lỗi - Status {response.status_code}"
        )

        st.code(
            response.text
        )

        st.stop()

    # --------------------------------------------------------
    # JSON RESPONSE
    # --------------------------------------------------------

    try:
        data = response.json()

    except ValueError:

        st.error(
            "API không trả JSON."
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
        type(data).__name__
    )

    # --------------------------------------------------------
    # TOP LEVEL
    # --------------------------------------------------------

    if isinstance(
        data,
        dict,
    ):

        st.subheader(
            "Top-level keys"
        )

        st.write(
            list(
                data.keys()
            )
        )

        # ----------------------------------------------------
        # TÌM LIST RECORD
        # ----------------------------------------------------

        found_records = False

        for key, value in data.items():

            if isinstance(
                value,
                list,
            ):

                st.subheader(
                    f"{key}"
                )

                st.write(
                    f"Số record: {len(value)}"
                )

                if value:

                    first_record = (
                        value[0]
                    )

                    if isinstance(
                        first_record,
                        dict,
                    ):

                        found_records = True

                        st.markdown(
                            "### Field API trả về"
                        )

                        fields = (
                            list(
                                first_record.keys()
                            )
                        )

                        st.write(
                            fields
                        )

                        st.markdown(
                            "### Record đầu tiên"
                        )

                        st.json(
                            first_record
                        )

                        st.markdown(
                            "### Preview dữ liệu"
                        )

                        try:

                            import pandas as pd

                            df = pd.DataFrame(
                                value
                            )

                            st.dataframe(
                                df.head(50),
                                use_container_width=True,
                            )

                        except Exception:
                            pass

        if not found_records:

            st.markdown(
                "### Full response"
            )

            st.json(
                data
            )

    elif isinstance(
        data,
        list,
    ):

        st.write(
            f"Số record: {len(data)}"
        )

        if data:

            st.markdown(
                "### Field API trả về"
            )

            st.write(
                list(
                    data[0].keys()
                )
                if isinstance(
                    data[0],
                    dict,
                )
                else "Không phải dict"
            )

            st.markdown(
                "### Record đầu tiên"
            )

            st.json(
                data[0]
            )

            try:

                import pandas as pd

                df = pd.DataFrame(
                    data
                )

                st.markdown(
                    "### Preview dữ liệu"
                )

                st.dataframe(
                    df.head(50),
                    use_container_width=True,
                )

            except Exception:
                pass

    else:

        st.write(
            data
        )
