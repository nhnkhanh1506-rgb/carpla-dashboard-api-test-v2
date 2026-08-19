import json

import requests


# ============================================================
# API DEV - CARPLA
# ============================================================

API_URL = (
    "https://dev-synerlynk.carpla.vn/"
    "api/report.repair.order.api/"
    "method_not_record/get_repair_order_report"
)


# ============================================================
# THÔNG TIN XÁC THỰC
# ============================================================
# Không commit token thật lên GitHub public.
#
# Khi test local:
# điền token vào đây tạm thời.
#
# Sau khi test xong chúng ta sẽ chuyển sang
# Streamlit Secrets.

AUTHORIZATION = "DAN_TOKEN_VAO_DAY"

# Cookie có thể không bắt buộc nếu Authorization đã đủ.
# Bước đầu để trống và test trước.
COOKIE = ""


# ============================================================
# HÀM CALL API
# ============================================================

def call_repair_order_api(
    date_from,
    date_to,
    branch_codes,
):
    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": "application/json",
    }

    if COOKIE:
        headers["Cookie"] = COOKIE

    payload = {
        "date_from": date_from,
        "date_to": date_to,
        "branch_ids": [],
        "branch_codes": branch_codes,
    }

    print("=" * 80)
    print("CALL API")
    print("=" * 80)

    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
    )

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

    except requests.RequestException as error:
        print("\nLỖI KẾT NỐI API:")
        print(error)
        return None

    print("\nHTTP STATUS:")
    print(response.status_code)

    print("\nCONTENT TYPE:")
    print(
        response.headers.get(
            "Content-Type"
        )
    )

    if not response.ok:
        print("\nAPI TRẢ VỀ LỖI:")
        print(response.text)
        return None

    try:
        data = response.json()

    except ValueError:
        print("\nAPI KHÔNG TRẢ JSON:")
        print(response.text)
        return None

    return data


# ============================================================
# HÀM XEM CẤU TRÚC RESPONSE
# ============================================================

def inspect_response(data):
    print("\n")
    print("=" * 80)
    print("KIỂM TRA RESPONSE")
    print("=" * 80)

    print("\nTYPE:")
    print(type(data))

    if isinstance(data, dict):

        print("\nTOP LEVEL KEYS:")

        for key in data.keys():
            print(
                f"- {key}"
            )

        # ----------------------------------------------------
        # Tìm thử các list nằm trong response
        # ----------------------------------------------------

        list_candidates = []

        for key, value in data.items():
            if isinstance(
                value,
                list,
            ):
                list_candidates.append(
                    (
                        key,
                        value,
                    )
                )

        if list_candidates:

            print(
                "\nCÁC FIELD DẠNG LIST:"
            )

            for (
                key,
                value,
            ) in list_candidates:
                print(
                    f"- {key}: "
                    f"{len(value)} records"
                )

                if value:
                    first_record = (
                        value[0]
                    )

                    if isinstance(
                        first_record,
                        dict,
                    ):

                        print(
                            "\nFIELD CỦA "
                            "RECORD ĐẦU TIÊN:"
                        )

                        for field in (
                            first_record.keys()
                        ):
                            print(
                                f"  - {field}"
                            )

                        print(
                            "\nRECORD ĐẦU TIÊN:"
                        )

                        print(
                            json.dumps(
                                first_record,
                                ensure_ascii=False,
                                indent=2,
                                default=str,
                            )
                        )

                        return

    elif isinstance(
        data,
        list,
    ):

        print(
            "\nSỐ RECORD:"
        )
        print(
            len(data)
        )

        if data:

            first_record = (
                data[0]
            )

            if isinstance(
                first_record,
                dict,
            ):

                print(
                    "\nFIELD CỦA "
                    "RECORD ĐẦU TIÊN:"
                )

                for field in (
                    first_record.keys()
                ):
                    print(
                        f"- {field}"
                    )

                print(
                    "\nRECORD ĐẦU TIÊN:"
                )

                print(
                    json.dumps(
                        first_record,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )
                )

    else:
        print(
            "\nRESPONSE:"
        )
        print(
            data
        )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # TEST 1:
    # 1 XƯỞNG
    # --------------------------------------------------------

    print("\n\n")
    print("#" * 80)
    print("TEST 1 - MỘT XƯỞNG")
    print("#" * 80)

    data = call_repair_order_api(
        date_from="2026-07-01",
        date_to="2026-07-31",
        branch_codes=[
            "CSHN.HY",
        ],
    )

    if data is not None:
        inspect_response(
            data
        )
