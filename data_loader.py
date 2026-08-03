from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st


# ============================================================
# HÀM CHUẨN HÓA
# ============================================================

def normalize_text(value):
    value = str(value).strip()

    value = unicodedata.normalize(
        "NFD",
        value,
    )

    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    return value.strip("_")


def normalize_order_number(series):
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .replace({
            "": pd.NA,
            "NAN": pd.NA,
            "NONE": pd.NA,
        })
    )


def parse_money(series):
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(
            ",",
            "",
            regex=False,
        )
        .str.replace(
            " ",
            "",
            regex=False,
        )
        .str.replace(
            r"[^\d\-.]",
            "",
            regex=True,
        )
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    ).fillna(0)


# ============================================================
# ĐỌC FILE VÀ TỰ TÌM HEADER
# ============================================================

def read_excel_with_header_detection(
    file_path: Path,
    expected_columns,
    preferred_sheet="Báo cáo",
):
    if not file_path.exists():
        st.error(
            f"Không tìm thấy file dữ liệu: "
            f"{file_path.name}"
        )
        st.stop()

    excel_file = pd.ExcelFile(
        file_path
    )

    if preferred_sheet in excel_file.sheet_names:
        sheet_name = preferred_sheet
    else:
        sheet_name = excel_file.sheet_names[0]

    preview = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None,
        nrows=30,
    )

    normalized_expected = {
        normalize_text(column)
        for column in expected_columns
    }

    header_row = None

    for row_index in range(len(preview)):
        row_values = {
            normalize_text(value)
            for value in preview.iloc[
                row_index
            ].dropna()
        }

        if normalized_expected.issubset(
            row_values
        ):
            header_row = row_index
            break

    if header_row is None:
        st.error(
            f"Không tìm được dòng tiêu đề "
            f"trong file {file_path.name}."
        )
        st.stop()

    data = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=header_row,
    )

    data = data.dropna(
        how="all"
    ).copy()

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    return data


# ============================================================
# ĐỌC FILE TỔNG HỢP 1 CHI NHÁNH
# ============================================================

def read_branch_file(
    file_path: Path,
    branch_name: str,
    workshop_name_map: dict,
):
    data = read_excel_with_header_detection(
        file_path=file_path,
        expected_columns=[
            "Số lệnh sửa chữa",
            "Ngày DT",
            "Chi nhánh",
            "Tổng doanh thu",
        ],
        preferred_sheet="Báo cáo",
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
            "Doanh thu công việc": (
                "doanh_thu_cong_viec"
            ),
            "Doanh thu phụ tùng": (
                "doanh_thu_phu_tung"
            ),
            "Tổng doanh thu": (
                "doanh_thu_truoc_thue"
            ),
            "Tổng thanh toán": (
                "tong_tien_sau_thue"
            ),
            "Khách hàng.1": (
                "khach_hang_chi_tra"
            ),
            "Bảo hiểm": (
                "bao_hiem_chi_tra"
            ),
            "Chi nhánh": (
                "xuong_dms"
            ),
        }
    )

    required_columns = [
        "ro",
        "ngay_hoa_don",
        "trang_thai",
        "hang_xe",
        "doanh_thu_cong_viec",
        "doanh_thu_phu_tung",
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "xuong_dms",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            f"File {file_path.name} thiếu các cột: "
            + ", ".join(missing_columns)
        )
        st.stop()

    # --------------------------------------------------------
    # 2. CHỈ GIỮ CÁC DÒNG LỆNH THẬT
    # --------------------------------------------------------
    # File tổng hợp có:
    # - dòng Tổng cộng
    # - dòng tiêu đề theo ngày
    # Các dòng đó không phải lệnh.

    data["ro"] = (
        data["ro"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    real_order_mask = (
        data["ro"]
        .str.upper()
        .str.match(
            r"^(LSC|LPK|LPT)\.",
            na=False,
        )
    )

    data = data[
        real_order_mask
    ].copy()

    # --------------------------------------------------------
    # 3. LOẠI LỆNH TRÙNG
    # --------------------------------------------------------

    data["ro_key"] = normalize_order_number(
        data["ro"]
    )

    data = data[
        data["ro_key"].notna()
    ].copy()

    # Nếu cùng một số lệnh xuất hiện nhiều dòng,
    # chỉ giữ bản ghi cuối cùng.
    data = (
        data.drop_duplicates(
            subset=["ro_key"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # 4. LOẠI LỆNH
    # --------------------------------------------------------

    data["loai_lenh"] = (
        data["ro_key"]
        .astype(str)
        .str[:3]
    )

    # --------------------------------------------------------
    # 5. CHI NHÁNH / XƯỞNG
    # --------------------------------------------------------

    data["chi_nhanh"] = branch_name

    data["xuong_dms"] = (
        data["xuong_dms"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data["xuong"] = (
        data["xuong_dms"]
        .map(workshop_name_map)
        .fillna(data["xuong_dms"])
    )

    # --------------------------------------------------------
    # 6. NGÀY
    # --------------------------------------------------------

    for column in [
        "ngay_hoa_don",
        "ngay_quyet_toan",
        "ngay_lap_lenh",
    ]:
        if column in data.columns:
            data[column] = pd.to_datetime(
                data[column],
                errors="coerce",
                dayfirst=True,
            )

    # --------------------------------------------------------
    # 6.1. GIỚI HẠN PHẠM VI NGÀY DT CHO FILE HÀ NỘI
    # --------------------------------------------------------
    # File hiện tại được xác định là dữ liệu từ:
    # 01/01/2026 đến 31/07/2026.
    #
    # Vì vậy các dòng có Ngày DT ngoài phạm vi này
    # sẽ bị loại khỏi dashboard, kể cả khi chúng vẫn còn
    # xuất hiện trong file nguồn.

    if branch_name == "Hà Nội":
        start_date = pd.Timestamp(
            "2026-01-01"
        )

        end_date = pd.Timestamp(
            "2026-07-31"
        )

        data = data[
            data[
                "ngay_hoa_don"
            ].between(
                start_date,
                end_date,
                inclusive="both",
            )
        ].copy()

    # --------------------------------------------------------
    # 7. CỘT TIỀN
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
    # 8. TRẠNG THÁI
    # --------------------------------------------------------

    data["trang_thai"] = (
        data["trang_thai"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 9. HÃNG XE
    # --------------------------------------------------------

    data["hang_xe"] = (
        data["hang_xe"]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    data["hang_xe"] = (
        data["hang_xe"]
        .replace({
            "HUYNDAI": "HYUNDAI",
            "HYNDAI": "HYUNDAI",
            "MERCEDES BENZ": "MERCEDES-BENZ",
            "LYNK&CO": "LYNK & CO",
            "LYNK AND CO": "LYNK & CO",
        })
    )

    # --------------------------------------------------------
    # 10. NGUỒN KHÁCH
    # --------------------------------------------------------

    if "nguon_khach" not in data.columns:
        data["nguon_khach"] = ""

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

    return data


# ============================================================
# LOAD TOÀN BỘ DỮ LIỆU
# ============================================================

@st.cache_data
def load_all_data(
    data_files,
    workshop_name_map,
):
    frames = []

    for (
        branch_name,
        file_path,
    ) in data_files.items():
        if not file_path.exists():
            st.warning(
                f"Chưa có file dữ liệu cho "
                f"Chi nhánh {branch_name}: "
                f"{file_path.name}"
            )
            continue

        branch_data = read_branch_file(
            file_path=file_path,
            branch_name=branch_name,
            workshop_name_map=(
                workshop_name_map
            ),
        )

        frames.append(
            branch_data
        )

    if not frames:
        st.error(
            "Không có dữ liệu để hiển thị."
        )
        st.stop()

    data_raw = pd.concat(
        frames,
        ignore_index=True,
    )

    # Giữ 3 output để app cũ vẫn tương thích.
    # File tổng hợp mới đã có trực tiếp DT công việc,
    # DT phụ tùng và DT phụ kiện theo loại lệnh,
    # nên không còn cần parts_data/accessory_data riêng.
    parts_data = {}
    accessory_data = {}

    return (
        data_raw,
        parts_data,
        accessory_data,
    )
