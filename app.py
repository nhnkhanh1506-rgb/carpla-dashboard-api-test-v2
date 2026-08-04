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
# EXECUTIVE DASHBOARD - EMBEDDED IN APP.PY
# ============================================================

# ============================================================
# CẤU HÌNH TỌA ĐỘ MAP
# ============================================================
# Đây là tọa độ để hiển thị dashboard.
# Khi IT có tọa độ chính xác từng xưởng, chỉ cần sửa dictionary này.
# Dashboard không phụ thuộc vào API map bên ngoài.

WORKSHOP_COORDINATES = {
    "Phạm Văn Đồng": (21.0545, 105.7827),
    "Long Biên": (21.0458, 105.8893),
    "Giải Phóng": (20.9955, 105.8426),
    "Hà Đông": (20.9712, 105.7788),
    "Hưng Yên": (20.6464, 106.0511),
    "Hà Nam": (20.5835, 105.9230),
    "Hải Dương": (20.9373, 106.3146),
    "Ninh Bình": (20.2506, 105.9745),
}

BRANCH_COORDINATES = {
    "Hà Nội": (21.0285, 105.8542),
    "Tây Bắc Bộ": (21.8277, 103.1576),
    "Đông Bắc Bộ": (21.8537, 106.7615),
    "TP. HCM": (10.7769, 106.7009),
    "Cần Thơ": (10.0452, 105.7469),
    "Nghệ An": (18.6796, 105.6813),
    "Đà Nẵng": (16.0544, 108.2022),
}


EXCLUDED_STATUS = [
    "Báo giá",
    "Hủy",
    "Không thực hiện",
    "Không duyệt",
    "Nháp",
]


# ============================================================
# HÀM CƠ BẢN
# ============================================================

def safe_div(a, b):
    return a / b if b else 0


def _money_to_m(value):
    return value / 1_000_000


def _format_growth(value):
    if pd.isna(value):
        return "—"

    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1%}"


def _clean_scope_data(
    data_raw,
    selected_branch,
    selected_workshop,
    year,
):
    data = data_raw.copy()

    data = data[
        data["ngay_hoa_don"].notna()
    ].copy()

    data = data[
        data["ngay_hoa_don"].dt.year
        == int(year)
    ].copy()

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

    if "trang_thai" in data.columns:
        data = data[
            ~data["trang_thai"].isin(
                EXCLUDED_STATUS
            )
        ].copy()

    if "ro_key" in data.columns:
        data = data[
            data["ro_key"].notna()
        ].copy()

    return data


def _prepare_orders(scope_data):
    # --------------------------------------------------------
    # LSC
    # --------------------------------------------------------
    lsc = scope_data[
        scope_data["loai_lenh"]
        == "LSC"
    ].copy()

    lsc[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        lsc[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    lsc = lsc[
        lsc["doanh_thu_truoc_thue"]
        > 0
    ].copy()

    lsc = (
        lsc.sort_values(
            "ngay_hoa_don"
        )
        .drop_duplicates(
            subset=["ro_key"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # LPK
    # --------------------------------------------------------
    accessory = scope_data[
        scope_data["loai_lenh"]
        == "LPK"
    ].copy()

    accessory[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        accessory[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    accessory = accessory[
        accessory[
            "doanh_thu_truoc_thue"
        ] > 0
    ].copy()

    if not accessory.empty:
        accessory = (
            accessory.sort_values(
                "ngay_hoa_don"
            )
            .drop_duplicates(
                subset=["ro_key"],
                keep="last",
            )
            .reset_index(drop=True)
        )

    return lsc, accessory


def _monthly_summary(
    lsc,
    accessory,
):
    months = list(
        range(1, 13)
    )

    lsc_month = (
        lsc.assign(
            month=lsc[
                "ngay_hoa_don"
            ].dt.month
        )
        .groupby("month")
        .agg(
            ro=(
                "ro_key",
                "nunique",
            ),
            service_revenue=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reindex(
            months,
            fill_value=0,
        )
        .reset_index()
    )

    if accessory.empty:
        accessory_month = pd.DataFrame(
            {
                "month": months,
                "accessory_revenue": 0,
            }
        )
    else:
        accessory_month = (
            accessory.assign(
                month=accessory[
                    "ngay_hoa_don"
                ].dt.month
            )
            .groupby("month")
            .agg(
                accessory_revenue=(
                    "doanh_thu_truoc_thue",
                    "sum",
                ),
            )
            .reindex(
                months,
                fill_value=0,
            )
            .reset_index()
        )

    monthly = lsc_month.merge(
        accessory_month,
        on="month",
        how="left",
    )

    monthly[
        "accessory_revenue"
    ] = monthly[
        "accessory_revenue"
    ].fillna(0)

    monthly[
        "revenue"
    ] = (
        monthly["service_revenue"]
        + monthly["accessory_revenue"]
    )

    monthly[
        "revenue_per_ro"
    ] = monthly.apply(
        lambda row:
        safe_div(
            row["revenue"],
            row["ro"],
        ),
        axis=1,
    )

    return monthly


def _latest_month_with_data(
    monthly,
):
    active = monthly[
        (
            monthly["ro"] > 0
        )
        | (
            monthly["revenue"] > 0
        )
    ]

    if active.empty:
        return None

    return int(
        active["month"].max()
    )


def _unit_summary(
    lsc,
    accessory,
    group_column,
):
    service = (
        lsc.groupby(
            group_column,
            dropna=False,
        )
        .agg(
            ro=(
                "ro_key",
                "nunique",
            ),
            service_revenue=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
    )

    if accessory.empty:
        accessory_group = pd.DataFrame(
            columns=[
                group_column,
                "accessory_revenue",
            ]
        )
    else:
        accessory_group = (
            accessory.groupby(
                group_column,
                dropna=False,
            )
            .agg(
                accessory_revenue=(
                    "doanh_thu_truoc_thue",
                    "sum",
                ),
            )
            .reset_index()
        )

    summary = service.merge(
        accessory_group,
        on=group_column,
        how="left",
    )

    summary[
        "accessory_revenue"
    ] = summary[
        "accessory_revenue"
    ].fillna(0)

    summary[
        "revenue"
    ] = (
        summary["service_revenue"]
        + summary["accessory_revenue"]
    )

    summary[
        "revenue_per_ro"
    ] = summary.apply(
        lambda row:
        safe_div(
            row["revenue"],
            row["ro"],
        ),
        axis=1,
    )

    return summary


def _growth_by_unit(
    lsc,
    accessory,
    group_column,
    latest_month,
):
    if (
        latest_month is None
        or latest_month <= 1
    ):
        return pd.DataFrame()

    def build_month(
        month_number,
    ):
        lsc_m = lsc[
            lsc[
                "ngay_hoa_don"
            ].dt.month
            == month_number
        ].copy()

        accessory_m = accessory[
            accessory[
                "ngay_hoa_don"
            ].dt.month
            == month_number
        ].copy()

        return _unit_summary(
            lsc=lsc_m,
            accessory=accessory_m,
            group_column=group_column,
        )[
            [
                group_column,
                "ro",
                "revenue",
            ]
        ]

    current = build_month(
        latest_month
    ).rename(
        columns={
            "ro": "ro_current",
            "revenue": "revenue_current",
        }
    )

    previous = build_month(
        latest_month - 1
    ).rename(
        columns={
            "ro": "ro_previous",
            "revenue": "revenue_previous",
        }
    )

    result = current.merge(
        previous,
        on=group_column,
        how="outer",
    ).fillna(0)

    result[
        "revenue_growth"
    ] = result.apply(
        lambda row:
        (
            row["revenue_current"]
            / row["revenue_previous"]
            - 1
        )
        if row["revenue_previous"] > 0
        else float("nan"),
        axis=1,
    )

    result[
        "ro_growth"
    ] = result.apply(
        lambda row:
        (
            row["ro_current"]
            / row["ro_previous"]
            - 1
        )
        if row["ro_previous"] > 0
        else float("nan"),
        axis=1,
    )

    return result


# ============================================================
# STYLE
# ============================================================

def _apply_executive_style():
    st.markdown(
        """
        <style>
        .exec-kpi-card {
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:18px;
            padding:18px 20px;
            min-height:126px;
            box-sizing:border-box;
        }

        .exec-kpi-label {
            color:#64748B;
            font-size:14px;
            font-weight:700;
            margin-bottom:12px;
        }

        .exec-kpi-value {
            color:#172033;
            font-size:31px;
            line-height:1;
            font-weight:900;
        }

        .exec-kpi-sub {
            margin-top:10px;
            color:#64748B;
            font-size:12.5px;
            font-weight:600;
        }

        .exec-section-title {
            color:#1F2937;
            font-size:27px;
            line-height:1.15;
            font-weight:900;
            margin:26px 0 12px 0;
        }

        .exec-card-title {
            color:#1F2937;
            font-size:18px;
            font-weight:800;
            margin:0 0 8px 0;
        }

        .exec-insight {
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:16px;
            padding:14px 16px;
            min-height:84px;
            box-sizing:border-box;
        }

        .exec-insight-label {
            color:#64748B;
            font-size:12px;
            font-weight:700;
            margin-bottom:6px;
        }

        .exec-insight-value {
            color:#1F2937;
            font-size:16px;
            font-weight:800;
            line-height:1.25;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card(
    label,
    value,
    subtext="",
):
    st.markdown(
        f"""
        <div class="exec-kpi-card">
            <div class="exec-kpi-label">{label}</div>
            <div class="exec-kpi-value">{value}</div>
            <div class="exec-kpi-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _insight_card(
    label,
    value,
):
    st.markdown(
        f"""
        <div class="exec-insight">
            <div class="exec-insight-label">{label}</div>
            <div class="exec-insight-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CHART HELPERS
# ============================================================

def _line_chart(
    monthly,
    value_column,
    title,
    y_title,
    suffix="",
):
    active_month = _latest_month_with_data(
        monthly
    )

    if active_month is None:
        chart_data = monthly.iloc[:7].copy()
    else:
        chart_data = monthly[
            monthly["month"]
            <= active_month
        ].copy()

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=chart_data["month"],
            y=chart_data[value_column],
            mode="lines+markers+text",
            line=dict(
                width=3,
                color="#3B6FB6",
            ),
            marker=dict(
                size=8,
                color="#3B6FB6",
                line=dict(
                    color="#FFFFFF",
                    width=2,
                ),
            ),
            text=[
                (
                    f"{value:,.0f}{suffix}"
                    if value_column == "ro"
                    else f"{_money_to_m(value):,.1f}M"
                )
                for value in chart_data[
                    value_column
                ]
            ],
            textposition="top center",
            textfont=dict(
                size=11,
                color="#667085",
            ),
            hovertemplate=(
                "Tháng %{x}<br>"
                + (
                    "Lượt xe: %{y:,.0f}"
                    if value_column == "ro"
                    else "Doanh thu: %{y:,.0f}"
                )
                + "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        template="simple_white",
        height=350,
        margin=dict(
            l=55,
            r=25,
            t=58,
            b=48,
        ),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02,
            y=0.96,
            xanchor="left",
            yanchor="top",
            font=dict(
                size=18,
                color="#1F2937",
            ),
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=chart_data["month"],
            ticktext=[
                f"T{month}"
                for month
                in chart_data["month"]
            ],
            title="",
            showgrid=False,
        ),
        yaxis=dict(
            title=y_title,
            gridcolor="#E5E7EB",
            zeroline=False,
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#667085",
        ),
        showlegend=False,
    )

    return figure


def _horizontal_bar(
    data,
    name_column,
    value_column,
    title,
    value_type,
    top_n=10,
    color="#F3D76B",
):
    chart = (
        data.sort_values(
            value_column,
            ascending=False,
        )
        .head(top_n)
        .sort_values(
            value_column,
            ascending=True,
        )
        .copy()
    )

    if value_type == "money":
        x_values = (
            chart[value_column]
            / 1_000_000
        )

        text_values = [
            f"{value:,.1f}M"
            for value in x_values
        ]

        x_title = "Doanh thu (M)"
    elif value_type == "money_per_ro":
        x_values = (
            chart[value_column]
            / 1_000_000
        )

        text_values = [
            f"{value:,.1f}M"
            for value in x_values
        ]

        x_title = "Doanh thu / RO (M)"
    else:
        x_values = chart[
            value_column
        ]

        text_values = [
            f"{int(value):,}"
            for value in x_values
        ]

        x_title = "Lượt xe / RO"

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=x_values,
            y=chart[name_column],
            orientation="h",
            marker=dict(
                color=color,
            ),
            text=text_values,
            textposition="outside",
            textfont=dict(
                size=12,
                color="#667085",
            ),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x}<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        template="simple_white",
        height=max(
            340,
            54 * len(chart),
        ),
        margin=dict(
            l=165,
            r=70,
            t=58,
            b=45,
        ),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02,
            y=0.96,
            xanchor="left",
            yanchor="top",
            font=dict(
                size=18,
                color="#1F2937",
            ),
        ),
        xaxis=dict(
            title=x_title,
            gridcolor="#E5E7EB",
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            automargin=True,
            tickfont=dict(
                size=11.5,
            ),
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#667085",
        ),
        showlegend=False,
    )

    return figure


def _map_chart(
    unit_summary,
    name_column,
    coordinate_dict,
    title,
):
    map_data = unit_summary.copy()

    map_data["lat"] = map_data[
        name_column
    ].map(
        lambda value:
        coordinate_dict.get(
            value,
            (None, None),
        )[0]
    )

    map_data["lon"] = map_data[
        name_column
    ].map(
        lambda value:
        coordinate_dict.get(
            value,
            (None, None),
        )[1]
    )

    map_data = map_data[
        map_data["lat"].notna()
        & map_data["lon"].notna()
    ].copy()

    if map_data.empty:
        return None

    revenue_values = (
        map_data["revenue"]
        .clip(lower=0)
    )

    max_revenue = max(
        revenue_values.max(),
        1,
    )

    sizes = (
        18
        + 30
        * (
            revenue_values
            / max_revenue
        ) ** 0.5
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scattermapbox(
            lat=map_data["lat"],
            lon=map_data["lon"],
            mode="markers",
            text=map_data[
                name_column
            ],
            customdata=list(
                zip(
                    map_data["ro"],
                    map_data["revenue"],
                    map_data["revenue_per_ro"],
                )
            ),
            marker=dict(
                size=sizes,
                color=map_data["revenue"],
                colorscale=[
                    [0.0, "#FEE2E2"],
                    [0.35, "#FCA5A5"],
                    [0.70, "#EF4444"],
                    [1.0, "#991B1B"],
                ],
                cmin=0,
                cmax=max_revenue,
                opacity=0.88,
                showscale=True,
                colorbar=dict(
                    title="Doanh thu",
                    thickness=12,
                    len=0.60,
                ),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Lượt xe: %{customdata[0]:,.0f}<br>"
                "Doanh thu: %{customdata[1]:,.0f}<br>"
                "DT/RO: %{customdata[2]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    center_lat = (
        map_data["lat"].mean()
    )

    center_lon = (
        map_data["lon"].mean()
    )

    if len(map_data) == 1:
        zoom = 10
    elif (
        map_data["lat"].max()
        - map_data["lat"].min()
        < 0.5
    ):
        zoom = 7.3
    else:
        zoom = 4.5

    figure.update_layout(
        height=455,
        margin=dict(
            l=0,
            r=0,
            t=58,
            b=0,
        ),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02,
            y=0.97,
            xanchor="left",
            yanchor="top",
            font=dict(
                size=18,
                color="#1F2937",
            ),
        ),
        mapbox=dict(
            style="open-street-map",
            center=dict(
                lat=center_lat,
                lon=center_lon,
            ),
            zoom=zoom,
        ),
        paper_bgcolor="#FFFFFF",
        font=dict(
            color="#667085",
        ),
    )

    return figure


# ============================================================
# MAIN EXECUTIVE DASHBOARD
# ============================================================

def render_executive_dashboard(
    data_raw,
    selected_branch,
    selected_workshop,
    year,
):
    _apply_executive_style()

    scope_data = _clean_scope_data(
        data_raw=data_raw,
        selected_branch=selected_branch,
        selected_workshop=selected_workshop,
        year=year,
    )

    lsc, accessory = _prepare_orders(
        scope_data
    )

    if lsc.empty:
        st.warning(
            "Không có dữ liệu LSC trong phạm vi đã chọn."
        )
        return

    monthly = _monthly_summary(
        lsc=lsc,
        accessory=accessory,
    )

    latest_month = _latest_month_with_data(
        monthly
    )

    total_ro = lsc[
        "ro_key"
    ].nunique()

    total_revenue = (
        lsc[
            "doanh_thu_truoc_thue"
        ].sum()
        + accessory[
            "doanh_thu_truoc_thue"
        ].sum()
    )

    revenue_per_ro = safe_div(
        total_revenue,
        total_ro,
    )

    active_workshops = (
        lsc["xuong"]
        .dropna()
        .nunique()
    )

    current_row = None
    previous_row = None

    if latest_month is not None:
        current_row = monthly[
            monthly["month"]
            == latest_month
        ].iloc[0]

        if latest_month > 1:
            previous_row = monthly[
                monthly["month"]
                == latest_month - 1
            ].iloc[0]

    ro_mom = float("nan")
    revenue_mom = float("nan")

    if (
        current_row is not None
        and previous_row is not None
    ):
        ro_mom = (
            current_row["ro"]
            / previous_row["ro"]
            - 1
            if previous_row["ro"] > 0
            else float("nan")
        )

        revenue_mom = (
            current_row["revenue"]
            / previous_row["revenue"]
            - 1
            if previous_row["revenue"] > 0
            else float("nan")
        )

    # ========================================================
    # HEADER
    # ========================================================

    if selected_branch == "All":
        scope_name = "Toàn HO"
    elif selected_workshop == "All":
        scope_name = (
            f"Chi nhánh {selected_branch}"
        )
    else:
        scope_name = (
            f"Xưởng {selected_workshop}"
        )

    active_period = (
        f"T1–T{latest_month}/{year}"
        if latest_month
        else str(year)
    )

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#FFF3B6 0%,#FFE27A 55%,#FFF7D6 100%);
            border:1px solid rgba(245,198,66,0.35);
            border-radius:22px;
            padding:24px 28px;
            margin-bottom:20px;
        ">
            <div style="
                color:#18316A;
                font-size:34px;
                font-weight:900;
                line-height:1.1;
            ">
                Executive Dashboard – {scope_name}
            </div>
            <div style="
                color:#526581;
                font-size:14px;
                font-weight:600;
                margin-top:8px;
            ">
                Tổng hợp YTD {active_period} · Xu hướng · Xếp hạng · Cơ cấu khách hàng · Mạng lưới
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # KPI
    # ========================================================

    k1, k2, k3, k4, k5 = (
        st.columns(5)
    )

    with k1:
        _kpi_card(
            "Lượt xe / RO YTD",
            f"{total_ro:,.0f}",
            (
                f"MoM {_format_growth(ro_mom)}"
                if latest_month
                else ""
            ),
        )

    with k2:
        _kpi_card(
            "Doanh thu YTD",
            fmt_m(total_revenue),
            (
                f"MoM {_format_growth(revenue_mom)}"
                if latest_month
                else ""
            ),
        )

    with k3:
        _kpi_card(
            "Doanh thu / RO",
            fmt_m(revenue_per_ro),
            "Giá trị bình quân / lượt xe",
        )

    with k4:
        _kpi_card(
            "Xưởng hoạt động",
            f"{active_workshops:,.0f}",
            "Có phát sinh LSC trong kỳ",
        )

    with k5:
        latest_month_text = (
            f"T{latest_month}"
            if latest_month
            else "—"
        )

        _kpi_card(
            "Dữ liệu mới nhất",
            latest_month_text,
            f"Năm {year}",
        )

    # ========================================================
    # TREND
    # ========================================================

    st.markdown(
        '<div class="exec-section-title">1. Xu hướng hoạt động</div>',
        unsafe_allow_html=True,
    )

    trend_left, trend_right = (
        st.columns(2)
    )

    with trend_left:
        ro_line = _line_chart(
            monthly=monthly,
            value_column="ro",
            title="Lượt xe theo tháng",
            y_title="Lượt xe / RO",
        )

        st.plotly_chart(
            ro_line,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with trend_right:
        revenue_line = _line_chart(
            monthly=monthly,
            value_column="revenue",
            title="Doanh thu theo tháng",
            y_title="Doanh thu",
        )

        st.plotly_chart(
            revenue_line,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    # ========================================================
    # MAP + RANKING UNITS
    # ========================================================

    st.markdown(
        '<div class="exec-section-title">2. Mạng lưới & hiệu quả đơn vị</div>',
        unsafe_allow_html=True,
    )

    if selected_branch == "All":
        group_column = "chi_nhanh"
        coordinate_dict = (
            BRANCH_COORDINATES
        )
        map_title = (
            "Bản đồ doanh thu theo chi nhánh"
        )
        unit_label = "Chi nhánh"
    elif selected_workshop == "All":
        group_column = "xuong"
        coordinate_dict = (
            WORKSHOP_COORDINATES
        )
        map_title = (
            f"Bản đồ xưởng – {selected_branch}"
        )
        unit_label = "Xưởng"
    else:
        group_column = "xuong"
        coordinate_dict = (
            WORKSHOP_COORDINATES
        )
        map_title = (
            f"Vị trí xưởng {selected_workshop}"
        )
        unit_label = "Xưởng"

    unit_summary = _unit_summary(
        lsc=lsc,
        accessory=accessory,
        group_column=group_column,
    )

    map_figure = _map_chart(
        unit_summary=unit_summary,
        name_column=group_column,
        coordinate_dict=coordinate_dict,
        title=map_title,
    )

    if (
        selected_branch == "All"
        or selected_workshop == "All"
    ):
        map_col, rank_col = st.columns(
            [1.05, 0.95]
        )

        with map_col:
            if map_figure is not None:
                st.plotly_chart(
                    map_figure,
                    use_container_width=True,
                    config={
                        "displayModeBar": False,
                    },
                )
            else:
                st.info(
                    "Chưa cấu hình tọa độ cho phạm vi map này."
                )

        with rank_col:
            ranking_metric = _horizontal_bar(
                data=unit_summary,
                name_column=group_column,
                value_column="revenue",
                title=(
                    f"{unit_label} theo doanh thu YTD"
                ),
                value_type="money",
                top_n=10,
                color="#E86B62",
            )

            st.plotly_chart(
                ranking_metric,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

        unit_left, unit_mid, unit_right = (
            st.columns(3)
        )

        with unit_left:
            ro_rank = _horizontal_bar(
                data=unit_summary,
                name_column=group_column,
                value_column="ro",
                title=(
                    f"{unit_label} theo lượt xe"
                ),
                value_type="count",
                top_n=10,
                color="#A9C4E6",
            )

            st.plotly_chart(
                ro_rank,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

        with unit_mid:
            revenue_rank = _horizontal_bar(
                data=unit_summary,
                name_column=group_column,
                value_column="revenue",
                title=(
                    f"{unit_label} theo doanh thu"
                ),
                value_type="money",
                top_n=10,
                color="#F0C957",
            )

            st.plotly_chart(
                revenue_rank,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

        with unit_right:
            cpu_rank = _horizontal_bar(
                data=unit_summary,
                name_column=group_column,
                value_column="revenue_per_ro",
                title=(
                    f"{unit_label} theo doanh thu / RO"
                ),
                value_type="money_per_ro",
                top_n=10,
                color="#B7D9C7",
            )

            st.plotly_chart(
                cpu_rank,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

    else:
        if map_figure is not None:
            st.plotly_chart(
                map_figure,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

    # ========================================================
    # BRAND YTD
    # ========================================================

    st.markdown(
        '<div class="exec-section-title">3. Top hãng xe YTD</div>',
        unsafe_allow_html=True,
    )

    brand_data = lsc.copy()

    brand_data[
        "hang_xe"
    ] = (
        brand_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.strip()
        .replace(
            "",
            "KHÔNG XÁC ĐỊNH",
        )
    )

    brand_summary = (
        brand_data.groupby(
            "hang_xe",
            dropna=False,
        )
        .agg(
            ro=(
                "ro_key",
                "nunique",
            ),
            revenue=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
    )

    brand_left, brand_right = (
        st.columns(2)
    )

    with brand_left:
        brand_ro = _horizontal_bar(
            data=brand_summary,
            name_column="hang_xe",
            value_column="ro",
            title="Top hãng xe theo lượt xe",
            value_type="count",
            top_n=10,
            color="#E9D268",
        )

        st.plotly_chart(
            brand_ro,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with brand_right:
        brand_revenue = _horizontal_bar(
            data=brand_summary,
            name_column="hang_xe",
            value_column="revenue",
            title="Top hãng xe theo doanh thu",
            value_type="money",
            top_n=10,
            color="#D9B84F",
        )

        st.plotly_chart(
            brand_revenue,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    # ========================================================
    # SOURCE YTD
    # ========================================================

    st.markdown(
        '<div class="exec-section-title">4. Top nguồn khách YTD</div>',
        unsafe_allow_html=True,
    )

    source_data = lsc.copy()

    if "nguon_khach" not in source_data.columns:
        source_data[
            "nguon_khach"
        ] = "KHÔNG XÁC ĐỊNH"

    source_data[
        "nguon_khach"
    ] = (
        source_data[
            "nguon_khach"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.strip()
        .replace(
            "",
            "KHÔNG XÁC ĐỊNH",
        )
    )

    source_summary = (
        source_data.groupby(
            "nguon_khach",
            dropna=False,
        )
        .agg(
            ro=(
                "ro_key",
                "nunique",
            ),
            revenue=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
    )

    source_left, source_right = (
        st.columns(2)
    )

    with source_left:
        source_ro = _horizontal_bar(
            data=source_summary,
            name_column="nguon_khach",
            value_column="ro",
            title="Top nguồn khách theo lượt xe",
            value_type="count",
            top_n=10,
            color="#F1D56D",
        )

        st.plotly_chart(
            source_ro,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with source_right:
        source_revenue = _horizontal_bar(
            data=source_summary,
            name_column="nguon_khach",
            value_column="revenue",
            title="Top nguồn khách theo doanh thu",
            value_type="money",
            top_n=10,
            color="#E7BF51",
        )

        st.plotly_chart(
            source_revenue,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    # ========================================================
    # MANAGEMENT ATTENTION
    # ========================================================

    if (
        selected_branch == "All"
        or selected_workshop == "All"
    ):
        growth = _growth_by_unit(
            lsc=lsc,
            accessory=accessory,
            group_column=group_column,
            latest_month=latest_month,
        )

        if not growth.empty:
            st.markdown(
                '<div class="exec-section-title">5. Điểm cần chú ý</div>',
                unsafe_allow_html=True,
            )

            valid_revenue_growth = growth[
                growth[
                    "revenue_growth"
                ].notna()
            ].copy()

            if not valid_revenue_growth.empty:
                best_row = (
                    valid_revenue_growth
                    .sort_values(
                        "revenue_growth",
                        ascending=False,
                    )
                    .iloc[0]
                )

                worst_row = (
                    valid_revenue_growth
                    .sort_values(
                        "revenue_growth",
                        ascending=True,
                    )
                    .iloc[0]
                )
            else:
                best_row = None
                worst_row = None

            low_cpu = (
                unit_summary[
                    unit_summary["ro"] > 0
                ]
                .sort_values(
                    "revenue_per_ro",
                    ascending=True,
                )
            )

            low_cpu_row = (
                low_cpu.iloc[0]
                if not low_cpu.empty
                else None
            )

            i1, i2, i3 = st.columns(3)

            with i1:
                if best_row is not None:
                    _insight_card(
                        "Tăng trưởng doanh thu tốt nhất",
                        (
                            f"{best_row[group_column]} · "
                            f"{_format_growth(best_row['revenue_growth'])}"
                        ),
                    )

            with i2:
                if worst_row is not None:
                    _insight_card(
                        "Cần chú ý – doanh thu giảm mạnh",
                        (
                            f"{worst_row[group_column]} · "
                            f"{_format_growth(worst_row['revenue_growth'])}"
                        ),
                    )

            with i3:
                if low_cpu_row is not None:
                    _insight_card(
                        "Doanh thu / RO thấp nhất",
                        (
                            f"{low_cpu_row[group_column]} · "
                            f"{fmt_m(low_cpu_row['revenue_per_ro'])}"
                        ),
                    )

    st.caption(
        "Dashboard Executive sử dụng dữ liệu theo cột Ngày DT. "
        "Không sử dụng Ngày lập lệnh hoặc Ngày quyết toán."
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
# 6.1 EXECUTIVE DASHBOARD CHO CÁC CASE THÁNG = ALL
# ============================================================
# Theo flow 6 trường hợp:
# 2. 1 xưởng + Tháng All
# 4. Xưởng All + Tháng All
# 6. Chi nhánh All + Tháng All
#
# Ba case này dùng Dashboard Executive riêng.
# Các case theo 1 tháng vẫn giữ nguyên dashboard vận hành hiện tại.

if month == "All":
    render_executive_dashboard(
        data_raw=data_raw,
        selected_branch=selected_branch,
        selected_workshop=selected_workshop,
        year=year,
    )

    st.stop()


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
