import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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
# 2.1 LOCAL STYLE FOR SUMMARY SECTION
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   COMPACT HTML TABLES
   ========================================================== */

.compact-dashboard-table {
    width: 100%;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    overflow: hidden;
    margin: 0;
    padding: 0;
}

.compact-dashboard-table table {
    width: 100%;
    border-collapse: collapse;
    border-spacing: 0;
    table-layout: fixed;
    margin: 0;
    padding: 0;
}

.compact-dashboard-table th {
    background: #F3F4F6;
    color: #6B7280;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.2;
    text-align: left;

    padding: 10px 10px;

    border-right: 1px solid #E5E7EB;
    border-bottom: 1px solid #E5E7EB;
}

.compact-dashboard-table td {
    background: #FFFFFF;
    color: #1F2937;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.2;
    text-align: left;

    padding: 10px 10px;

    border-right: 1px solid #E5E7EB;
    border-bottom: 1px solid #E5E7EB;
}

.compact-dashboard-table th:last-child,
.compact-dashboard-table td:last-child {
    border-right: none;
}

.compact-dashboard-table tbody tr:last-child td {
    border-bottom: none;
}

.compact-dashboard-table .total-row td {
    font-weight: 700;
}


/* ==========================================================
   PIE CARD
   ========================================================== */

.revenue-pie-card {
    width: 100%;
    background: #FFFFFF;

    border: 1px solid #E5E7EB;
    border-radius: 18px;

    padding: 16px 18px 12px 18px;

    box-sizing: border-box;
}

.revenue-pie-title {
    color: #1F2937;

    font-size: 24px;
    font-weight: 800;
    line-height: 1.15;

    padding: 0;
    margin: 0 0 2px 2px;
}

.revenue-pie-legend {
    display: flex;
    justify-content: center;
    align-items: center;

    gap: 18px;
    flex-wrap: nowrap;

    margin-top: -10px;
    margin-bottom: 2px;

    font-size: 13px;
    color: #475467;
    font-weight: 600;
}

.revenue-pie-legend-item {
    display: flex;
    align-items: center;
    gap: 6px;

    white-space: nowrap;
}

.revenue-pie-dot {
    width: 10px;
    height: 10px;

    border-radius: 50%;
    display: inline-block;

    flex: 0 0 10px;
}


/* ==========================================================
   SUMMARY SECTION SPACING
   ========================================================== */

.summary-table-gap {
    height: 28px;
}


/* giảm khoảng trống mặc định trong vertical block */
div[data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}


/* riêng Plotly trong revenue card */
div[data-testid="stPlotlyChart"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPER: HTML TABLE
# ============================================================

def render_compact_table(
    dataframe,
    column_widths=None,
):
    columns = list(
        dataframe.columns
    )

    if column_widths is None:
        column_widths = [
            100 / len(columns)
        ] * len(columns)

    colgroup_html = ""

    for width in column_widths:
        colgroup_html += (
            f'<col style="width:{width}%;">'
        )

    header_html = ""

    for column in columns:
        header_html += (
            f"<th>{column}</th>"
        )

    body_html = ""

    for _, row in dataframe.iterrows():

        first_value = (
            str(row.iloc[0])
            .strip()
            .upper()
        )

        is_total = (
            first_value
            == "TỔNG DOANH THU"
        )

        row_class = (
            "total-row"
            if is_total
            else ""
        )

        body_html += (
            f'<tr class="{row_class}">'
        )

        for value in row:
            body_html += (
                f"<td>{value}</td>"
            )

        body_html += "</tr>"

    table_html = f"""
<div class="compact-dashboard-table">
    <table>
        <colgroup>
            {colgroup_html}
        </colgroup>

        <thead>
            <tr>
                {header_html}
            </tr>
        </thead>

        <tbody>
            {body_html}
        </tbody>
    </table>
</div>
"""

    st.markdown(
        table_html,
        unsafe_allow_html=True,
    )


# ============================================================
# 3. LOAD DATA
# ============================================================

data_raw, parts_data, accessory_data = (
    load_all_data(
        data_files=DATA_FILES,
        workshop_name_map=WORKSHOP_NAME_MAP,
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

if not selection["show_dashboard"]:

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

month = selection[
    "month"
]

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
    selected_workshop=selected_workshop,

    year=year,
    month=month,

    targets=TARGETS,
)


# ============================================================
# 8. GET METRICS
# ============================================================

data = metrics[
    "data"
]

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
# 9. DASHBOARD HEADER
# ============================================================

render_dashboard_header(
    branch=selected_branch,
    workshop=selected_workshop,
    year=year,
    month=month,
)


# ============================================================
# 10. DATA PERIOD NOTICE
# ============================================================

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
# 12. WORKING DAYS
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

        actual_revenue=actual_revenue,
        target_revenue=target_revenue,

        working_day_info=working_day_info,

        calculate_target_plan_function=(
            calculate_target_plan
        ),
    )


# ============================================================
# 14. SUMMARY KPI DATA
# ============================================================

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
# 15. REVENUE BREAKDOWN DATA
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
# 15.1 SUMMARY + PIE LAYOUT
# ============================================================

left_revenue_column, right_revenue_column = (
    st.columns(
        [1.08, 0.92],
        gap="large",
    )
)


# ============================================================
# 15.2 LEFT COLUMN
# ============================================================

with left_revenue_column:

    # --------------------------------------------------------
    # TABLE 1
    # --------------------------------------------------------

    if target_available:

        render_compact_table(
            summary_kpi,
            column_widths=[
                30,
                25,
                24,
                21,
            ],
        )

    else:

        render_compact_table(
            summary_kpi,
            column_widths=[
                55,
                45,
            ],
        )


    # --------------------------------------------------------
    # GAP
    # --------------------------------------------------------

    st.markdown(
        """
<div class="summary-table-gap"></div>
""",
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # TABLE 2
    # --------------------------------------------------------

    render_compact_table(
        revenue_display,
        column_widths=[
            42,
            31,
            27,
        ],
    )


# ============================================================
# 15.3 RIGHT COLUMN
# ============================================================

with right_revenue_column:

    # --------------------------------------------------------
    # PIE CHART
    # --------------------------------------------------------

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

                texttemplate=(
                    "%{percent:.0%}"
                ),

                textfont=dict(
                    color="#FFFFFF",
                    size=14,
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


    # --------------------------------------------------------
    # CENTER TEXT
    # --------------------------------------------------------

    revenue_mix_figure.add_annotation(
        x=0.5,
        y=0.51,

        text=(
            f"<b>{fmt_m(actual_revenue)}</b>"
            "<br>"
            "<span style='font-size:12px;'>"
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


    # --------------------------------------------------------
    # FIGURE LAYOUT
    # --------------------------------------------------------

    revenue_mix_figure.update_layout(
        template="simple_white",

        height=300,

        margin=dict(
            l=5,
            r=5,
            t=0,
            b=0,
        ),

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        plot_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        showlegend=False,
    )


    # --------------------------------------------------------
    # CARD TOP / TITLE
    # --------------------------------------------------------

    st.markdown(
        """
<div style="
    width:100%;
    background:#FFFFFF;
    border:1px solid #E5E7EB;
    border-bottom:none;
    border-radius:18px 18px 0 0;
    box-sizing:border-box;
    padding:18px 20px 0 20px;
    margin:0;
">
    <div style="
        color:#1F2937;
        font-size:24px;
        font-weight:800;
        line-height:1.15;
        margin:0;
        padding:0;
    ">
        Cơ cấu tổng doanh thu
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # CARD BODY
    # --------------------------------------------------------

    revenue_mix_card = st.container(
        key="revenue_mix_donut_card"
    )


    with revenue_mix_card:

        st.plotly_chart(
            revenue_mix_figure,

            use_container_width=True,

            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


        legend_html = """
<div class="revenue-pie-legend">

    <div class="revenue-pie-legend-item">

        <span
            class="revenue-pie-dot"
            style="
                background:#386FAE;
            "
        ></span>

        <span>
            Công việc
        </span>

    </div>


    <div class="revenue-pie-legend-item">

        <span
            class="revenue-pie-dot"
            style="
                background:#F86D53;
            "
        ></span>

        <span>
            Phụ tùng
        </span>

    </div>


    <div class="revenue-pie-legend-item">

        <span
            class="revenue-pie-dot"
            style="
                background:#F9B43A;
            "
        ></span>

        <span>
            Phụ kiện
        </span>

    </div>

</div>
"""

        st.markdown(
            legend_html,
            unsafe_allow_html=True,
        )


# ============================================================
# 16. DAILY / MONTHLY CHARTS
# ============================================================

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

    workshop=chart_scope_name,

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
