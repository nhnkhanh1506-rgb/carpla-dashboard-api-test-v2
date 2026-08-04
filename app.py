import pandas as pd
import streamlit as st

from calculations import (
    calculate_dashboard_metrics,
    calculate_target_plan,
    calculate_working_days,
)

from charts import (
    render_brand_section,
    render_daily_charts,
    render_payment_section,
)

from components import (
    fmt_m,
    render_dashboard_header,
    render_homepage,
    render_interactive_target_planner,
    render_sidebar,
    render_top_kpis,
)

from config import (
    DATA_FILES,
    LOGO_FILE,
    TARGETS,
    WORKSHOP_NAME_MAP,
)

from data_loader import load_all_data
from styles import apply_global_style


# ============================================================
# HÀM ĐỊNH DẠNG BẢNG
# ============================================================

def style_white_table(dataframe):
    return (
        dataframe.style
        .set_properties(
            **{
                "background-color": "#FFFFFF",
                "color": "#1F2937",
                "border-color": "#E5E7EB",
                "font-weight": "500",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        (
                            "background-color",
                            "#F3F4F6",
                        ),
                        (
                            "color",
                            "#6B7280",
                        ),
                        (
                            "font-weight",
                            "600",
                        ),
                        (
                            "border-color",
                            "#E5E7EB",
                        ),
                        (
                            "text-align",
                            "left",
                        ),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        (
                            "background-color",
                            "#FFFFFF",
                        ),
                        (
                            "color",
                            "#1F2937",
                        ),
                        (
                            "border-color",
                            "#E5E7EB",
                        ),
                    ],
                },
            ],
            overwrite=False,
        )
        .hide(axis="index")
    )


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dashboard DMS - Carpla Service",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. GLOBAL STYLE
# ============================================================

apply_global_style()


# ============================================================
# 3. LOAD DATA
# ============================================================

data_raw, parts_data, accessory_data = (
    load_all_data(
        data_files=DATA_FILES,
        workshop_name_map=(
            WORKSHOP_NAME_MAP
        ),
    )
)


# ============================================================
# 4. SIDEBAR FILTER
# ============================================================

selection = render_sidebar(
    data_raw=data_raw
)


# ============================================================
# 5. HOME PAGE
# ============================================================

if not selection[
    "show_dashboard"
]:
    render_homepage(
        logo_path=LOGO_FILE
    )

    st.stop()


# ============================================================
# 6. SELECTED FILTERS
# ============================================================

selected_branch = selection[
    "branch"
]

selected_workshop = selection[
    "workshop"
]

year = int(
    selection["year"]
)

month = selection["month"]

if month != "All":
    month = int(month)


# ============================================================
# 7. CALCULATE METRICS
# ============================================================

metrics = calculate_dashboard_metrics(
    data_raw=data_raw,
    parts_data=parts_data,
    accessory_data=accessory_data,
    selected_branch=selected_branch,
    selected_workshop=(
        selected_workshop
    ),
    year=year,
    month=month,
    targets=TARGETS,
)


# ============================================================
# 8. GET METRICS
# ============================================================

data = metrics["data"]
merged_data = metrics[
    "merged_data"
]

actual_ro = metrics[
    "actual_ro"
]

matched_orders = metrics[
    "matched_orders"
]

missing_orders = metrics[
    "missing_orders"
]

service_revenue = metrics[
    "service_revenue"
]

labor_revenue = metrics[
    "labor_revenue"
]

parts_revenue = metrics[
    "parts_revenue"
]

accessory_revenue = metrics[
    "accessory_revenue"
]

actual_revenue = metrics[
    "actual_revenue"
]

total_after_tax = metrics[
    "total_after_tax"
]

target_available = metrics[
    "target_available"
]

target_ro = metrics[
    "target_ro"
]

target_revenue = metrics[
    "target_revenue"
]

ro_rate = metrics[
    "ro_rate"
]

revenue_rate = metrics[
    "revenue_rate"
]


# ============================================================
# 10. DASHBOARD HEADER
# ============================================================

render_dashboard_header(
    branch=selected_branch,
    workshop=selected_workshop,
    year=year,
    month=month,
)


# ============================================================
# 10.1 THÔNG BÁO KỲ DỮ LIỆU
# ============================================================
# Nếu chọn All tháng nhưng file mới chỉ có dữ liệu
# đến 31/07 thì hiển thị đúng phạm vi hiện có.

valid_dates = data[
    "ngay_hoa_don"
].dropna()

if (
    month == "All"
    and not valid_dates.empty
):
    min_date = (
        valid_dates.min()
    )

    max_date = (
        valid_dates.max()
    )

    st.caption(
        "Dữ liệu hiện có: "
        f"{min_date:%d/%m/%Y} "
        "→ "
        f"{max_date:%d/%m/%Y}"
    )


# ============================================================
# 11. TOP KPI CARDS
# ============================================================

render_top_kpis(
    metrics
)


# ============================================================
# 12. TÍNH SỐ NGÀY LÀM VIỆC
# ============================================================

working_day_info = (
    calculate_working_days(
        year=year,
        month=month,
        data=data,
    )
)

actual_working_days = (
    working_day_info[
        "total_working_days"
    ]
)


# ============================================================
# 13. INTERACTIVE TARGET PLANNER
# ============================================================

if target_available:
    render_interactive_target_planner(
        actual_ro=actual_ro,
        target_ro=target_ro,
        actual_revenue=(
            actual_revenue
        ),
        target_revenue=(
            target_revenue
        ),
        working_day_info=(
            working_day_info
        ),
        calculate_target_plan_function=(
            calculate_target_plan
        ),
    )


# ============================================================
# 14-15. BẢNG KPI + CƠ CẤU TỔNG DOANH THU
# ============================================================
# Layout:
# - Cột trái: 2 bảng xếp trên/dưới, thu gọn.
# - Cột phải: card "Cơ cấu tổng doanh thu" + donut.
# - Tiêu đề "Cơ cấu tổng doanh thu" nằm trong card chart.

if target_available:
    summary_kpi = pd.DataFrame(
        {
            "Hạng mục": [
                "Lượt xe / RO",
                "Tổng Doanh thu",
            ],
            "Thực hiện": [
                f"{actual_ro:,.0f}",
                fmt_m(
                    actual_revenue
                ),
            ],
            "Chỉ tiêu": [
                f"{target_ro:,.0f}",
                fmt_m(
                    target_revenue
                ),
            ],
            "% đạt": [
                f"{ro_rate:.0%}",
                f"{revenue_rate:.0%}",
            ],
        }
    )
else:
    summary_kpi = pd.DataFrame(
        {
            "Hạng mục": [
                "Lượt xe / RO",
                "Tổng Doanh thu",
            ],
            "Thực hiện": [
                f"{actual_ro:,.0f}",
                fmt_m(
                    actual_revenue
                ),
            ],
        }
    )


# ============================================================
# DỮ LIỆU CƠ CẤU DOANH THU
# ============================================================

revenue_breakdown = pd.DataFrame(
    {
        "Nguồn doanh thu": [
            "Doanh thu công việc",
            "Doanh thu phụ tùng",
            "Doanh thu phụ kiện",
        ],
        "Giá trị": [
            labor_revenue,
            parts_revenue,
            accessory_revenue,
        ],
    }
)

revenue_breakdown[
    "Tỷ trọng"
] = revenue_breakdown[
    "Giá trị"
].apply(
    lambda value:
    value / actual_revenue
    if actual_revenue
    else 0
)

revenue_display = (
    revenue_breakdown.copy()
)

revenue_display[
    "Giá trị"
] = revenue_display[
    "Giá trị"
].map(
    fmt_m
)

revenue_display[
    "Tỷ trọng"
] = revenue_display[
    "Tỷ trọng"
].map(
    lambda value:
    f"{value:.0%}"
)

total_row = pd.DataFrame(
    {
        "Nguồn doanh thu": [
            "TỔNG DOANH THU"
        ],
        "Giá trị": [
            fmt_m(
                actual_revenue
            )
        ],
        "Tỷ trọng": [
            "100%"
        ],
    }
)

revenue_display = pd.concat(
    [
        revenue_display,
        total_row,
    ],
    ignore_index=True,
)


# ============================================================
# LAYOUT 2 CỘT
# ============================================================

left_summary_column, right_pie_column = (
    st.columns(
        [1.10, 0.90],
        gap="medium",
    )
)


# ============================================================
# CỘT TRÁI: 2 BẢNG XẾP TRÊN / DƯỚI
# ============================================================

with left_summary_column:
    # Bảng thực hiện / chỉ tiêu - thu gọn
    st.dataframe(
        style_white_table(
            summary_kpi
        ),
        use_container_width=True,
        hide_index=True,
        height=120,
    )

    st.markdown(
        "<div style='height:10px;'></div>",
        unsafe_allow_html=True,
    )

    # Bảng cơ cấu doanh thu
    st.dataframe(
        style_white_table(
            revenue_display
        ),
        use_container_width=True,
        hide_index=True,
        height=178,
    )


# ============================================================
# CỘT PHẢI: TITLE NẰM TRONG CARD + DONUT ĐẨY LÊN
# ============================================================

with right_pie_column:
    import plotly.graph_objects as go

    revenue_mix_card = st.container(
        key="revenue_mix_donut_card"
    )

    with revenue_mix_card:
        st.markdown(
            """
            <div style="
                font-size:24px;
                line-height:1.15;
                font-weight:800;
                color:#1F2937;
                margin:2px 0 -14px 4px;
            ">
                Cơ cấu tổng doanh thu
            </div>
            """,
            unsafe_allow_html=True,
        )

        revenue_mix_figure = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Doanh thu công việc",
                        "Doanh thu phụ tùng",
                        "Doanh thu phụ kiện",
                    ],
                    values=[
                        labor_revenue,
                        parts_revenue,
                        accessory_revenue,
                    ],
                    hole=0.60,
                    sort=False,
                    direction="clockwise",

                    marker=dict(
                        colors=[
                            "#386FAE",
                            "#F86D53",
                            "#F9B43A",
                        ],
                        line=dict(
                            color="#FFFFFF",
                            width=3,
                        ),
                    ),

                    textinfo="percent",
                    texttemplate="%{percent:.0%}",

                    textfont=dict(
                        color="#FFFFFF",
                        size=14,
                    ),

                    domain=dict(
                        x=[0.08, 0.92],
                        y=[0.13, 0.98],
                    ),

                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Giá trị: %{value:,.0f}<br>"
                        "Tỷ trọng: %{percent:.1%}"
                        "<extra></extra>"
                    ),
                )
            ]
        )

        revenue_mix_figure.add_annotation(
            x=0.5,
            y=0.57,
            text=(
                f"<b>{fmt_m(actual_revenue)}</b>"
                "<br><span style='font-size:12px;'>"
                "Tổng doanh thu"
                "</span>"
            ),
            showarrow=False,
            font=dict(
                color="#1F2937",
                size=16,
            ),
            align="center",
        )

        revenue_mix_figure.update_layout(
            template="simple_white",
            height=315,

            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0,
            ),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            showlegend=False,
        )

        st.plotly_chart(
            revenue_mix_figure,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

        st.markdown(
            """
            <div style="
                display:flex;
                justify-content:center;
                gap:18px;
                flex-wrap:nowrap;
                margin-top:-22px;
                padding-bottom:4px;
                font-size:13px;
                color:#475467;
                font-weight:600;
            ">
                <div style="
                    display:flex;
                    align-items:center;
                    gap:6px;
                    white-space:nowrap;
                ">
                    <span style="
                        width:10px;
                        height:10px;
                        border-radius:50%;
                        background:#386FAE;
                        display:inline-block;
                    "></span>
                    <span>Công việc</span>
                </div>

                <div style="
                    display:flex;
                    align-items:center;
                    gap:6px;
                    white-space:nowrap;
                ">
                    <span style="
                        width:10px;
                        height:10px;
                        border-radius:50%;
                        background:#F86D53;
                        display:inline-block;
                    "></span>
                    <span>Phụ tùng</span>
                </div>

                <div style="
                    display:flex;
                    align-items:center;
                    gap:6px;
                    white-space:nowrap;
                ">
                    <span style="
                        width:10px;
                        height:10px;
                        border-radius:50%;
                        background:#F9B43A;
                        display:inline-block;
                    "></span>
                    <span>Phụ kiện</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 16. DAILY / MONTHLY CHARTS
# ============================================================
# Tháng cụ thể:
#   chart giữ nguyên theo ngày.
#
# Tháng = All:
#   chart giữ nguyên hình dáng/màu sắc,
#   chỉ chuyển dữ liệu trục X sang 12 tháng.

if selected_branch == "All":
    chart_scope_name = (
        "TOÀN HO"
    )
elif selected_workshop == "All":
    chart_scope_name = (
        selected_branch
    )
else:
    chart_scope_name = (
        selected_workshop
    )

render_daily_charts(
    data=data,
    year=year,
    month=month,
    workshop=(
        chart_scope_name
    ),
    target_ro=target_ro,
    target_revenue=(
        target_revenue
    ),
    working_days=(
        actual_working_days
    ),
    target_available=(
        target_available
    ),
)


# ============================================================
# 17. BRAND SECTION
# ============================================================

render_brand_section(
    data=data
)


# ============================================================
# 18. PAYMENT STRUCTURE
# ============================================================

total_payment = (
    render_payment_section(
        data=data
    )
)


# ============================================================
# 19. CHECK TOTAL
# ============================================================

with st.expander(
    "Kiểm tra đối chiếu tổng"
):
    st.write(
        "Số ngày làm việc:",
        f"{actual_working_days:,.0f}",
    )

    st.write(
        "Số lệnh sửa chữa LSC:",
        f"{actual_ro:,.0f}",
    )

    st.write(
        "Doanh thu công việc:",
        fmt_m(
            labor_revenue
        ),
    )

    st.write(
        "Doanh thu phụ tùng:",
        fmt_m(
            parts_revenue
        ),
    )

    st.write(
        "Doanh thu phụ kiện:",
        fmt_m(
            accessory_revenue
        ),
    )

    st.write(
        "Tổng doanh thu:",
        fmt_m(
            actual_revenue
        ),
    )

    st.write(
        "Tổng thanh toán:",
        fmt_m(
            total_after_tax
        ),
    )

    st.write(
        "Tổng cơ cấu nguồn thanh toán:",
        fmt_m(
            total_payment
        ),
    )

    st.write(
        "Chênh lệch cơ cấu thanh toán:",
        fmt_m(
            total_after_tax
            - total_payment
        ),
    )


# ============================================================
# 20. RAW DATA
# ============================================================

with st.expander(
    "Xem dữ liệu lệnh sửa chữa"
):
    st.dataframe(
        data,
        use_container_width=True,
    )


with st.expander(
    "Xem dữ liệu đối chiếu phụ tùng"
):
    display_columns = [
        column
        for column in [
            "ro",
            "ngay_hoa_don",
            "doanh_thu_cong_viec",
            "doanh_thu_phu_tung",
            "doanh_thu_truoc_thue",
            "nguon_khach",
            "xuong",
        ]
        if column
        in merged_data.columns
    ]

    st.dataframe(
        merged_data[
            display_columns
        ],
        use_container_width=True,
        hide_index=True,
    )
