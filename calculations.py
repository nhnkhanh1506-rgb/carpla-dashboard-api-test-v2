import calendar
from datetime import date

import pandas as pd


# ============================================================
# TRẠNG THÁI KHÔNG ĐƯỢC TÍNH
# ============================================================

EXCLUDED_STATUS = [
    "Báo giá",
    "Hủy",
    "Không thực hiện",
    "Không duyệt",
    "Nháp",
]


# ============================================================
# HÀM CHIA AN TOÀN
# ============================================================

def safe_div(a, b):
    return a / b if b else 0


# ============================================================
# HÀM LỌC PHẠM VI
# ============================================================

def filter_scope(
    data_raw,
    selected_branch,
    selected_workshop,
    year,
    month,
):
    data = data_raw.copy()

    if selected_branch != "All":
        data = data[
            data["chi_nhanh"]
            == selected_branch
        ].copy()

    if selected_workshop != "All":
        data = data[
            data["xuong"]
            == selected_workshop
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

    return data


# ============================================================
# CỘNG TARGET THEO PHẠM VI ĐANG CHỌN
# ============================================================

def get_target_for_scope(
    targets,
    selected_branch,
    selected_workshop,
    year,
    month,
):
    """
    Target chỉ tồn tại cho đúng 1 xưởng Hà Nội,
    tháng 7/2026.

    Không cộng target khi:
    - Chi nhánh = All
    - Xưởng = All
    - Tháng = All
    - Tháng khác 7
    - Chi nhánh khác Hà Nội
    """

    if selected_branch == "All":
        return {
            "available": False,
            "ro": 0,
            "revenue": 0,
        }

    if selected_workshop == "All":
        return {
            "available": False,
            "ro": 0,
            "revenue": 0,
        }

    if month == "All":
        return {
            "available": False,
            "ro": 0,
            "revenue": 0,
        }

    key = (
        selected_branch,
        selected_workshop,
        int(year),
        int(month),
    )

    target_info = targets.get(key)

    if not target_info:
        return {
            "available": False,
            "ro": 0,
            "revenue": 0,
        }

    return {
        "available": True,
        "ro": target_info.get("ro", 0),
        "revenue": target_info.get(
            "revenue",
            0,
        ),
    }


# ============================================================
# TÍNH TOÀN BỘ KPI DASHBOARD
# ============================================================

def calculate_dashboard_metrics(
    data_raw,
    parts_data,
    accessory_data,
    selected_branch,
    selected_workshop,
    year,
    month,
    targets,
):
    # --------------------------------------------------------
    # 1. LỌC CHI NHÁNH / XƯỞNG / NĂM / THÁNG
    # --------------------------------------------------------

    scoped_data = filter_scope(
        data_raw=data_raw,
        selected_branch=selected_branch,
        selected_workshop=(
            selected_workshop
        ),
        year=year,
        month=month,
    )

    scoped_data = scoped_data[
        ~scoped_data[
            "trang_thai"
        ].isin(EXCLUDED_STATUS)
    ].copy()

    scoped_data = scoped_data[
        scoped_data["ro_key"].notna()
    ].copy()

    # --------------------------------------------------------
    # 2. LỆNH SỬA CHỮA LSC
    # --------------------------------------------------------
    # Dashboard hiện tại về RO, daily, hãng xe,
    # thanh toán vẫn dùng LSC giống logic cũ.

    data = scoped_data[
        scoped_data["loai_lenh"]
        == "LSC"
    ].copy()

    data = data[
        data["doanh_thu_truoc_thue"]
        > 0
    ].copy()

    data = (
        data.sort_values(
            "ngay_hoa_don"
        )
        .drop_duplicates(
            subset=["ro_key"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    actual_ro = (
        data["ro_key"].nunique()
    )

    # --------------------------------------------------------
    # 3. CƠ CẤU DOANH THU LSC
    # --------------------------------------------------------

    labor_revenue = pd.to_numeric(
        data[
            "doanh_thu_cong_viec"
        ],
        errors="coerce",
    ).fillna(0).sum()

    parts_revenue = pd.to_numeric(
        data[
            "doanh_thu_phu_tung"
        ],
        errors="coerce",
    ).fillna(0).sum()

    service_revenue = pd.to_numeric(
        data[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0).sum()

    # --------------------------------------------------------
    # 4. PHỤ KIỆN LPK
    # --------------------------------------------------------

    accessory_orders = scoped_data[
        scoped_data["loai_lenh"]
        == "LPK"
    ].copy()

    accessory_orders = accessory_orders[
        accessory_orders[
            "doanh_thu_truoc_thue"
        ] > 0
    ].copy()

    accessory_revenue = pd.to_numeric(
        accessory_orders[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0).sum()

    # --------------------------------------------------------
    # 5. TỔNG DOANH THU
    # --------------------------------------------------------
    # Giữ logic dashboard hiện tại:
    # Tổng DT = DT từ LSC + DT phụ kiện LPK.

    actual_revenue = (
        service_revenue
        + accessory_revenue
    )

    # --------------------------------------------------------
    # 6. TỔNG THANH TOÁN SAU THUẾ
    # --------------------------------------------------------

    total_after_tax = pd.to_numeric(
        data[
            "tong_tien_sau_thue"
        ],
        errors="coerce",
    ).fillna(0).sum()

    # --------------------------------------------------------
    # 7. TARGET
    # --------------------------------------------------------

    target_info = get_target_for_scope(
        targets=targets,
        selected_branch=selected_branch,
        selected_workshop=(
            selected_workshop
        ),
        year=year,
        month=month,
    )

    target_available = target_info[
        "available"
    ]

    target_ro = target_info["ro"]
    target_revenue = (
        target_info["revenue"]
    )

    # --------------------------------------------------------
    # 8. TỶ LỆ
    # --------------------------------------------------------

    ro_rate = safe_div(
        actual_ro,
        target_ro,
    )

    revenue_rate = safe_div(
        actual_revenue,
        target_revenue,
    )

    revenue_per_ro = safe_div(
        actual_revenue,
        actual_ro,
    )

    # --------------------------------------------------------
    # 9. ĐỐI CHIẾU
    # --------------------------------------------------------
    # File mới đã có doanh thu phụ tùng trực tiếp.
    # Giữ merged_data để app cũ không lỗi.

    merged_data = data.copy()

    merged_data[
        "tim_thay_trong_bang_tong_hop"
    ] = True

    matched_orders = actual_ro
    missing_orders = 0

    return {
        "data": data,
        "scoped_data": scoped_data,
        "accessory_orders": (
            accessory_orders
        ),
        "merged_data": merged_data,

        "selected_branch": (
            selected_branch
        ),
        "selected_workshop": (
            selected_workshop
        ),
        "year": year,
        "month": month,

        "actual_ro": actual_ro,
        "matched_orders": (
            matched_orders
        ),
        "missing_orders": (
            missing_orders
        ),

        "service_revenue": (
            service_revenue
        ),
        "labor_revenue": (
            labor_revenue
        ),
        "parts_revenue": (
            parts_revenue
        ),
        "accessory_revenue": (
            accessory_revenue
        ),
        "actual_revenue": (
            actual_revenue
        ),
        "total_after_tax": (
            total_after_tax
        ),

        "target_available": (
            target_available
        ),
        "target_ro": target_ro,
        "target_revenue": (
            target_revenue
        ),

        "ro_rate": ro_rate,
        "revenue_rate": revenue_rate,
        "revenue_per_ro": (
            revenue_per_ro
        ),
    }


# ============================================================
# TÍNH NGÀY LÀM VIỆC
# KHÔNG BAO GỒM CHỦ NHẬT
# ============================================================

def calculate_working_days(
    year,
    month,
    data,
):
    year = int(year)

    # --------------------------------------------------------
    # NẾU THÁNG = ALL:
    # TÍNH TOÀN BỘ NĂM
    # --------------------------------------------------------

    if month == "All":
        start_date = date(
            year,
            1,
            1,
        )

        end_date = date(
            year,
            12,
            31,
        )

        full_range = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D",
        )

        working_dates = [
            timestamp.date()
            for timestamp in full_range
            if timestamp.weekday() != 6
        ]
    else:
        month = int(month)

        days_in_month = (
            calendar.monthrange(
                year,
                month,
            )[1]
        )

        working_dates = [
            date(
                year,
                month,
                day,
            )
            for day in range(
                1,
                days_in_month + 1,
            )
            if date(
                year,
                month,
                day,
            ).weekday() != 6
        ]

    total_working_days = len(
        working_dates
    )

    valid_dates = data[
        "ngay_hoa_don"
    ].dropna()

    if valid_dates.empty:
        data_cutoff_date = (
            working_dates[0]
            if working_dates
            else date(
                year,
                1,
                1,
            )
        )
    else:
        data_cutoff_date = (
            valid_dates.max().date()
        )

    remaining_working_dates = [
        working_date
        for working_date
        in working_dates
        if working_date
        > data_cutoff_date
    ]

    elapsed_working_dates = [
        working_date
        for working_date
        in working_dates
        if working_date
        <= data_cutoff_date
    ]

    return {
        "data_cutoff_date": (
            data_cutoff_date
        ),
        "total_working_days": (
            total_working_days
        ),
        "elapsed_working_days": (
            len(
                elapsed_working_dates
            )
        ),
        "remaining_working_days": (
            len(
                remaining_working_dates
            )
        ),
        "remaining_working_dates": (
            remaining_working_dates
        ),
    }


# ============================================================
# TÍNH YÊU CẦU BÌNH QUÂN CHO MỤC TIÊU
# ============================================================

def calculate_target_plan(
    actual_value,
    monthly_target,
    desired_percentage,
    remaining_working_days,
):
    desired_value = (
        monthly_target
        * desired_percentage
        / 100
    )

    remaining_required = max(
        desired_value - actual_value,
        0,
    )

    if remaining_working_days > 0:
        average_required = (
            remaining_required
            / remaining_working_days
        )
    else:
        average_required = 0

    already_achieved = (
        actual_value
        >= desired_value
    )

    return {
        "desired_value": desired_value,
        "remaining_required": (
            remaining_required
        ),
        "average_required": (
            average_required
        ),
        "already_achieved": (
            already_achieved
        ),
    }
