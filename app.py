import textwrap

import pandas as pd
import plotly.graph_objects as go
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
# 2.1 LOCAL STYLE
# ============================================================

summary_css = """
<style>

/* ==========================================================
   COMPACT TABLES
   ========================================================== */

.compact-dashboard-table {
    width: 100%;
    background: #FFFFFF;

    border: 1px solid #E2E8F0;
    border-radius: 12px;

    overflow: hidden;

    box-sizing: border-box;

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
    background: #F8FAFC;
    color: #667085;

    font-size: 14px;
    font-weight: 500;
    line-height: 1.15;

    text-align: left;

    padding: 10px 10px;

    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
}

.compact-dashboard-table td {
    background: #FFFFFF;
    color: #1F2937;

    font-size: 14px;

    /* KHÔNG BOLD DATA */
    font-weight: 400;

    line-height: 1.15;

    text-align: left;

    padding: 10px 10px;

    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
}

.compact-dashboard-table th:last-child,
.compact-dashboard-table td:last-child {
    border-right: none;
}

.compact-dashboard-table tbody tr:last-child td {
    border-bottom: none;
}

/* chỉ TOTAL đậm nhẹ */
.compact-dashboard-table .total-row td {
    font-weight: 600;
}


/* ==========================================================
   GAP BETWEEN LEFT TABLES
   ========================================================== */

.summary-table-gap {
    height: 26px;
    width: 100%;
}


/* ==========================================================
   REVENUE MIX CARD
   ========================================================== */

.st-key-revenue_mix_card {
    width: 100%;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;
    border-radius: 18px;

    box-sizing: border-box;

    padding: 0 18px 18px 18px;

    overflow: hidden;
}


/* giảm khoảng trống Streamlit */
.st-key-revenue_mix_card
div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}


/* ==========================================================
   PIE TITLE
   giống style phần cơ cấu thương hiệu bên dưới
   ========================================================== */

.revenue-card-title {
    color: #1F2937;

    font-size: 20px;
    font-weight: 700;
    line-height: 1.2;

    margin: 0;

    padding: 16px 2px 2px 2px;
}


/* ==========================================================
   PIE CHART
   ========================================================== */

.st-key-revenue_mix_card
div[data-testid="stPlotlyChart"] {
    margin: 0 !important;
    padding: 0 !important;
}


/* ==========================================================
   PIE LEGEND
   ========================================================== */

.revenue-pie-legend {
    display: flex;

    justify-content: center;
    align-items: center;

    gap: 22px;

    width: 100%;

    flex-wrap: nowrap;

    margin-top: -6px;

    /* chừa khoảng dưới đẹp hơn */
    margin-bottom: 12px;

    font-size: 12.5px;
    font-weight: 600;

    color: #475467;
}

.revenue-pie-legend-item {
    display: flex;

    align-items: center;

    gap: 6px;

    white-space: nowrap;
}

.revenue-pie-dot {
    width: 9px;
    height: 9px;

    border-radius: 50%;

    display: inline-block;

    flex: 0 0 9px;
}


/* ==========================================================
   SUMMARY ROW ALIGNMENT
   ========================================================== */

div[data-testid="stHorizontalBlock"] {
    align-items: flex-start;
}

</style>
"""

st.markdown(
    textwrap.dedent(
        summary_css
    ).strip(),
    unsafe_allow_html=True,
)


# ============================================================
# 2.2 SAFE HTML HELPER
# ============================================================

def render_html(html):
    st.markdown(
        textwrap.dedent(
            html
        ).strip(),
        unsafe_allow_html=True,
    )


# ============================================================
# 2.3 COMPACT TABLE HELPER
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

    colgroup_html = "".join(
        f'<col style="width:{width}%;">'
        for width in column_widths
    )

    header_html = "".join(
        f"<th>{column}</th>"
        for column in columns
    )

    body_rows = []

    for _, row in dataframe.iterrows():

        first_value = (
            str(row.iloc[0])
            .strip()
            .upper()
        )

        row_class = (
            "total-row"
            if first_value
            == "TỔNG DOANH THU"
            else ""
        )

        cells = "".join(
            f"<td>{value}</td>"
            for value in row
        )

        body_rows.append(
            f'<tr class="{row_class}">'
            f'{cells}'
            '</tr>'
        )

    body_html = "".join(
        body_rows
    )

    table_html = (
        '<div class="compact-dashboard-table">'
        '<table>'
        f'<colgroup>{colgroup_html}</colgroup>'
        '<thead>'
        f'<tr>{header_html}</tr>'
        '</thead>'
        '<tbody>'
        f'{body_html}'
        '</tbody>'
        '</table>'
        '</div>'
    )

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
    (
        value / actual_revenue
        if actual_revenue
        else 0
    )
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
# 15.1 SUMMARY SECTION
# ============================================================

left_revenue_column, right_revenue_column = (
    st.columns(
        [1, 1],
        gap="medium",
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

    render_html(
        """
        <div class="summary-table-gap"></div>
        """
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

    revenue_mix_card = st.container(
        key="revenue_mix_card"
    )

    with revenue_mix_card:

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        render_html(
            """
            <div class="revenue-card-title">
                Cơ cấu tổng doanh thu
            </div>
            """
        )


        # ----------------------------------------------------
        # PIE CHART
        # ----------------------------------------------------

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

                    # donut nhỏ hơn
                    hole=0.62,

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
                        size=13,
                    ),

                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Giá trị: %{value:,.0f}<br>"
                        "Tỷ trọng: %{percent:.1%}"
                        "<extra></extra>"
                    ),

                    # QUAN TRỌNG:
                    # thu pie vào giữa card
                    domain=dict(
                        x=[0.16, 0.84],
                        y=[0.14, 0.94],
                    ),
                )
            ]
        )


        # ----------------------------------------------------
        # CENTER TEXT
        # ----------------------------------------------------

        revenue_mix_figure.add_annotation(
            x=0.5,
            y=0.54,

            text=(
                f"<b>{fmt_m(actual_revenue)}</b>"
                "<br>"
                "<span style='font-size:11px;'>"
                "Tổng doanh thu"
                "</span>"
            ),

            showarrow=False,

            font=dict(
                color="#1F2937",
                size=15,
            ),

            align="center",
        )


        # ----------------------------------------------------
        # PIE LAYOUT
        # ----------------------------------------------------

        revenue_mix_figure.update_layout(
            template="simple_white",

            # giảm từ 300 xuống
            height=250,

            margin=dict(
                l=0,
                r=0,
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


        st.plotly_chart(
            revenue_mix_figure,

            use_container_width=True,

            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        legend_html = (
            '<div class="revenue-pie-legend">'

            '<div class="revenue-pie-legend-item">'
            '<span class="revenue-pie-dot" '
            'style="background:#386FAE;"></span>'
            '<span>Công việc</span>'
            '</div>'

            '<div class="revenue-pie-legend-item">'
            '<span class="revenue-pie-dot" '
            'style="background:#F86D53;"></span>'
            '<span>Phụ tùng</span>'
            '</div>'

            '<div class="revenue-pie-legend-item">'
            '<span class="revenue-pie-dot" '
            'style="background:#F9B43A;"></span>'
            '<span>Phụ kiện</span>'
            '</div>'

            '</div>'
        )

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
