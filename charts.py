import calendar
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import (
    LUXURY_BRANDS,
    MASS_MARKET_BRANDS,
    PARTNER_BRANDS,
    TASCO_OFFICIAL_BRANDS,
)

from components import (
    fmt_m,
    render_mini_kpi,
)

from styles import (
    PRIMARY_BLUE,
    PRIMARY_BLUE_LIGHT,
    LINE_BLUE,
    LINE_BLUE_SOFT,
    PCT_TEXT_COLOR,
    BAR_LABEL_COLOR,
    CPUS_BAR_COLOR,
    CPUS_BAR_BORDER,
    REVENUE_BAR_COLOR,
    REVENUE_BAR_BORDER,
    CUMULATIVE_LINE_COLOR,
    CUMULATIVE_MARKER_COLOR,
    CUMULATIVE_MARKER_BORDER,
    DAILY_CHART_BG,
    DAILY_CHART_GRID,
    DAILY_CHART_TEXT,
    DAILY_CHART_TITLE,
    DAILY_CHART_AXIS,
    DARK_PANEL,
    DARK_GRID,
    WHITE,
    MUTED_BAR_COLORS,
    DONUT_MAIN,
    DONUT_SECOND,
)


# ============================================================
# HÀM CHIA AN TOÀN
# ============================================================

def safe_div(a, b):
    return a / b if b else 0


# ============================================================
# PHÂN NHÓM QUAN HỆ THƯƠNG HIỆU
# ============================================================

def normalize_brand_name(value):
    return (
        str(value)
        .strip()
        .upper()
        .replace("–", "-")
        .replace("—", "-")
    )


def classify_brand_relationship(brand_name):
    normalized_brand = normalize_brand_name(
        brand_name
    )

    official_brands = {
        normalize_brand_name(brand)
        for brand in TASCO_OFFICIAL_BRANDS
    }

    partner_brands = {
        normalize_brand_name(brand)
        for brand in PARTNER_BRANDS
    }

    if normalized_brand in official_brands:
        return "Xe chính hãng Tasco"

    if normalized_brand in partner_brands:
        return "Hãng đối tác"

    return "Khác"


def build_brand_relationship_summary(data):
    relationship_data = data.copy()

    relationship_data[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        relationship_data[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    relationship_data[
        "hang_xe"
    ] = (
        relationship_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.strip()
    )

    relationship_data[
        "nhom_quan_he"
    ] = relationship_data[
        "hang_xe"
    ].apply(
        classify_brand_relationship
    )

    summary = (
        relationship_data
        .groupby(
            "nhom_quan_he",
            dropna=False,
        )
        .agg(
            so_ro=(
                "ro",
                "nunique",
            ),
            doanh_thu=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
    )

    group_order = [
        "Xe chính hãng Tasco",
        "Hãng đối tác",
        "Khác",
    ]

    summary = (
        summary
        .set_index("nhom_quan_he")
        .reindex(
            group_order,
            fill_value=0,
        )
        .reset_index()
    )

    total_ro = summary[
        "so_ro"
    ].sum()

    total_revenue = summary[
        "doanh_thu"
    ].sum()

    summary[
        "ty_trong_ro"
    ] = summary[
        "so_ro"
    ].apply(
        lambda value:
        safe_div(
            value,
            total_ro,
        )
    )

    summary[
        "ty_trong_doanh_thu"
    ] = summary[
        "doanh_thu"
    ].apply(
        lambda value:
        safe_div(
            value,
            total_revenue,
        )
    )

    return summary


def build_brand_relationship_bubble_chart(
    relationship_summary,
):
    bubble_data = (
        relationship_summary
        .sort_values(
            "doanh_thu",
            ascending=False,
        )
        .reset_index(drop=True)
        .copy()
    )

    positions = [
        (1.45, 1.55),
        (3.00, 2.05),
        (2.92, 0.92),
    ]

    bubble_colors = {
        "Xe chính hãng Tasco": {
            "fill": "#EEE9FF",
            "text": "#6D4BEA",
        },
        "Hãng đối tác": {
            "fill": "#DFF5EA",
            "text": "#2FB878",
        },
        "Khác": {
            "fill": "#FDE7EB",
            "text": "#EC5269",
        },
    }

    max_share = max(
        bubble_data[
            "ty_trong_doanh_thu"
        ].max(),
        0.01,
    )

    bubble_data[
        "bubble_size"
    ] = bubble_data[
        "ty_trong_doanh_thu"
    ].apply(
        lambda share:
        78
        + 110
        * (
            share
            / max_share
        ) ** 0.5
    )

    figure = go.Figure()

    for index, row in (
        bubble_data.iterrows()
    ):
        group_name = row[
            "nhom_quan_he"
        ]

        style = bubble_colors[
            group_name
        ]

        x_position, y_position = (
            positions[index]
        )

        figure.add_trace(
            go.Scatter(
                x=[x_position],
                y=[y_position],
                mode="markers+text",

                marker=dict(
                    size=float(
                        row["bubble_size"]
                    ),
                    color=style["fill"],
                    line=dict(
                        color="rgba(255,255,255,0.90)",
                        width=2,
                    ),
                ),

                text=[
                    (
                        "<b>"
                        f"{row['ty_trong_doanh_thu']:.0%}"
                        "</b>"
                    )
                ],

                textposition="middle center",

                textfont=dict(
                    color=style["text"],
                    size=20,
                ),

                hovertemplate=(
                    f"<b>{group_name}</b><br>"
                    "Số RO: "
                    f"{int(row['so_ro'])}<br>"
                    "Doanh thu: "
                    f"{fmt_m(row['doanh_thu'])}<br>"
                    "Tỷ trọng RO: "
                    f"{row['ty_trong_ro']:.1%}<br>"
                    "Tỷ trọng doanh thu: "
                    f"{row['ty_trong_doanh_thu']:.1%}"
                    "<extra></extra>"
                ),

                showlegend=False,
            )
        )

    figure.update_layout(
        template="simple_white",
        height=275,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0,
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        xaxis=dict(
            visible=False,
            range=[0, 4.0],
            fixedrange=True,
        ),

        yaxis=dict(
            visible=False,
            range=[0, 2.8],
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1,
        ),

        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#E5E7EB",
            font=dict(
                color="#1F2937",
            ),
        ),
    )

    return figure



def build_brand_relationship_brand_map(
    data,
):
    relationship_data = data.copy()

    relationship_data[
        "hang_xe"
    ] = (
        relationship_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .map(
            normalize_brand_name
        )
    )

    relationship_data[
        "nhom_quan_he"
    ] = relationship_data[
        "hang_xe"
    ].apply(
        classify_brand_relationship
    )

    group_order = [
        "Xe chính hãng Tasco",
        "Hãng đối tác",
        "Khác",
    ]

    records = []

    for group_name in group_order:
        brands = sorted(
            relationship_data.loc[
                relationship_data[
                    "nhom_quan_he"
                ]
                == group_name,
                "hang_xe",
            ].dropna().unique().tolist()
        )

        records.append(
            {
                "group_name": group_name,
                "brands": brands,
            }
        )

    return records


def render_brand_relationship_legend():
    legend_items = [
        (
            "Xe chính hãng Tasco",
            "#6D4BEA",
        ),
        (
            "Hãng đối tác",
            "#2FB878",
        ),
        (
            "Khác",
            "#EC5269",
        ),
    ]

    legend_columns = st.columns(
        [1.25, 1, 0.65]
    )

    for column, (
        label,
        color,
    ) in zip(
        legend_columns,
        legend_items,
    ):
        with column:
            st.markdown(
                (
                    '<div class="brand-relationship-legend-item">'
                    f'<span class="brand-relationship-dot" '
                    f'style="background:{color};"></span>'
                    f'<span>{label}</span>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )


def render_brand_relationship_group_cards(
    relationship_groups,
):
    for item in relationship_groups:
        group_name = item[
            "group_name"
        ]

        brands = item[
            "brands"
        ]

        color_map = {
            "Xe chính hãng Tasco": "#6D4BEA",
            "Hãng đối tác": "#2FB878",
            "Khác": "#EC5269",
        }

        brand_text = (
            ", ".join(brands)
            if brands
            else "-"
        )

        st.markdown(
            f"""
            <div style="
                background:#F9FAFB;
                border:1px solid #EEF2F7;
                border-radius:18px;
                padding:14px 16px;
                margin-bottom:12px;
            ">
                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    margin-bottom:8px;
                ">
                    <span style="
                        display:inline-block;
                        width:10px;
                        height:10px;
                        border-radius:50%;
                        background:{color_map[group_name]};
                    "></span>
                    <span style="
                        font-size:16px;
                        font-weight:800;
                        color:#1F2937;
                    ">{group_name}</span>
                </div>
                <div style="
                    font-size:14px;
                    line-height:1.65;
                    color:#475467;
                    font-weight:500;
                ">{brand_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )



def render_brand_relationship_section(
    data,
):
    relationship_summary = (
        build_brand_relationship_summary(
            data
        )
    )

    official_brands = [
        normalize_brand_name(
            brand
        )
        for brand in TASCO_OFFICIAL_BRANDS
    ]

    partner_brands = [
        normalize_brand_name(
            brand
        )
        for brand in PARTNER_BRANDS
    ]

    relationship_data = data.copy()

    relationship_data[
        "hang_xe"
    ] = (
        relationship_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .map(
            normalize_brand_name
        )
    )

    other_brands = sorted(
        relationship_data.loc[
            relationship_data[
                "hang_xe"
            ].apply(
                classify_brand_relationship
            )
            == "Khác",
            "hang_xe",
        ]
        .dropna()
        .unique()
        .tolist()
    )

    grouped_brands = [
        (
            "Xe chính hãng Tasco",
            official_brands,
        ),
        (
            "Hãng đối tác",
            partner_brands,
        ),
        (
            "Khác",
            other_brands,
        ),
    ]

    left_column, right_column = (
        st.columns(
            [0.86, 1.14]
        )
    )

    with left_column:
        bubble_card = st.container(
            key="brand_relationship_bubble_card"
        )

        with bubble_card:
            st.markdown(
                '<div class="brand-relationship-card-title">'
                'Cơ cấu theo quan hệ thương hiệu'
                '</div>',
                unsafe_allow_html=True,
            )

            bubble_figure = (
                build_brand_relationship_bubble_chart(
                    relationship_summary
                )
            )

            st.plotly_chart(
                bubble_figure,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

            render_brand_relationship_legend()

    with right_column:
        group_card = st.container(
            key="brand_relationship_group_card"
        )

        with group_card:
            st.markdown(
                '<div class="brand-relationship-card-title">'
                'Chi tiết hãng xe theo nhóm'
                '</div>',
                unsafe_allow_html=True,
            )

            table_html = """
            <div class="brand-group-table-wrap">
                <table class="brand-group-table">
                    <thead>
                        <tr>
                            <th>Nhóm thương hiệu</th>
                            <th>Hãng xe</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for (
                group_name,
                brands,
            ) in grouped_brands:
                display_brands = (
                    brands
                    if brands
                    else ["-"]
                )

                row_count = len(
                    display_brands
                )

                for index, brand_name in enumerate(
                    display_brands
                ):
                    table_html += "<tr>"

                    if index == 0:
                        group_class_map = {
                            "Xe chính hãng Tasco": (
                                "brand-group-official"
                            ),
                            "Hãng đối tác": (
                                "brand-group-partner"
                            ),
                            "Khác": (
                                "brand-group-other"
                            ),
                        }

                        group_class = (
                            group_class_map[
                                group_name
                            ]
                        )

                        table_html += (
                            '<td class="brand-group-merged '
                            f'{group_class}" '
                            f'rowspan="{row_count}">'
                            f'{html.escape(group_name)}'
                            "</td>"
                        )

                    table_html += (
                        "<td>"
                        f"{html.escape(brand_name)}"
                        "</td>"
                    )

                    table_html += "</tr>"

            table_html += """
                    </tbody>
                </table>
            </div>
            """

            st.markdown(
                table_html,
                unsafe_allow_html=True,
            )


# ============================================================
# PHÂN KHÚC XE
# ============================================================

def classify_vehicle_segment(brand_name):
    normalized_brand = normalize_brand_name(
        brand_name
    )

    luxury_brands = {
        normalize_brand_name(brand)
        for brand in LUXURY_BRANDS
    }

    mass_market_brands = {
        normalize_brand_name(brand)
        for brand in MASS_MARKET_BRANDS
    }

    if normalized_brand in luxury_brands:
        return "Xe sang"

    if normalized_brand in mass_market_brands:
        return "Xe phổ thông"

    return "Khác"


def build_vehicle_segment_summary(data):
    segment_data = data.copy()

    segment_data[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        segment_data[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    segment_data[
        "hang_xe"
    ] = (
        segment_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .map(
            normalize_brand_name
        )
    )

    segment_data[
        "phan_khuc"
    ] = segment_data[
        "hang_xe"
    ].apply(
        classify_vehicle_segment
    )

    summary = (
        segment_data
        .groupby(
            "phan_khuc",
            dropna=False,
        )
        .agg(
            so_ro=(
                "ro",
                "nunique",
            ),
            doanh_thu=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
    )

    group_order = [
        "Xe sang",
        "Xe phổ thông",
        "Khác",
    ]

    summary = (
        summary
        .set_index("phan_khuc")
        .reindex(
            group_order,
            fill_value=0,
        )
        .reset_index()
    )

    total_ro = summary[
        "so_ro"
    ].sum()

    total_revenue = summary[
        "doanh_thu"
    ].sum()

    summary[
        "ty_trong_ro"
    ] = summary[
        "so_ro"
    ].apply(
        lambda value:
        safe_div(
            value,
            total_ro,
        )
    )

    summary[
        "ty_trong_doanh_thu"
    ] = summary[
        "doanh_thu"
    ].apply(
        lambda value:
        safe_div(
            value,
            total_revenue,
        )
    )

    return summary


def build_vehicle_segment_bubble_chart(
    segment_summary,
):
    bubble_data = (
        segment_summary
        .sort_values(
            "doanh_thu",
            ascending=False,
        )
        .reset_index(drop=True)
        .copy()
    )

    positions = [
        (1.45, 1.50),
        (2.72, 1.95),
        (2.66, 0.92),
    ]

    bubble_colors = {
        "Xe sang": {
            "fill": "#FE9E2C",
            "text": "#A84E00",
        },
        "Xe phổ thông": {
            "fill": "#9DDBF5",
            "text": "#1E5E7A",
        },
        "Khác": {
            "fill": "#FDE7EB",
            "text": "#EC5269",
        },
    }

    max_share = max(
        bubble_data[
            "ty_trong_doanh_thu"
        ].max(),
        0.01,
    )

    bubble_data[
        "bubble_size"
    ] = bubble_data[
        "ty_trong_doanh_thu"
    ].apply(
        lambda share:
        78
        + 110
        * (
            share
            / max_share
        ) ** 0.5
    )

    figure = go.Figure()

    for index, row in (
        bubble_data.iterrows()
    ):
        group_name = row[
            "phan_khuc"
        ]

        style = bubble_colors[
            group_name
        ]

        x_position, y_position = (
            positions[index]
        )

        figure.add_trace(
            go.Scatter(
                x=[x_position],
                y=[y_position],
                mode="markers+text",
                marker=dict(
                    size=float(
                        row["bubble_size"]
                    ),
                    color=style["fill"],
                    line=dict(
                        color="rgba(255,255,255,0.90)",
                        width=2,
                    ),
                ),
                text=[
                    (
                        "<b>"
                        f"{row['ty_trong_doanh_thu']:.0%}"
                        "</b>"
                    )
                ],
                textposition="middle center",
                textfont=dict(
                    color=style["text"],
                    size=20,
                ),
                hovertemplate=(
                    f"<b>{group_name}</b><br>"
                    "Số RO: "
                    f"{int(row['so_ro'])}<br>"
                    "Doanh thu: "
                    f"{fmt_m(row['doanh_thu'])}<br>"
                    "Tỷ trọng RO: "
                    f"{row['ty_trong_ro']:.1%}<br>"
                    "Tỷ trọng doanh thu: "
                    f"{row['ty_trong_doanh_thu']:.1%}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

    figure.update_layout(
        template="simple_white",
        height=275,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            visible=False,
            range=[0, 4.0],
            fixedrange=True,
        ),
        yaxis=dict(
            visible=False,
            range=[0, 2.8],
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1,
        ),
    )

    return figure


def render_vehicle_segment_legend():
    legend_items = [
        (
            "Xe phổ thông",
            "#1E5E7A",
        ),
        (
            "Xe sang",
            "#A84E00",
        ),
        (
            "Khác",
            "#EC5269",
        ),
    ]

    legend_columns = st.columns(
        [0.85, 1.1, 0.65]
    )

    for column, (
        label,
        color,
    ) in zip(
        legend_columns,
        legend_items,
    ):
        with column:
            st.markdown(
                (
                    '<div class="vehicle-segment-legend-item">'
                    f'<span class="vehicle-segment-dot" '
                    f'style="background:{color};"></span>'
                    f'<span>{label}</span>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )


def render_vehicle_segment_section(data):
    segment_summary = (
        build_vehicle_segment_summary(
            data
        )
    )

    segment_data = data.copy()

    segment_data[
        "hang_xe"
    ] = (
        segment_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .map(
            normalize_brand_name
        )
    )

    other_brands = sorted(
        segment_data.loc[
            segment_data[
                "hang_xe"
            ].apply(
                classify_vehicle_segment
            )
            == "Khác",
            "hang_xe",
        ]
        .dropna()
        .unique()
        .tolist()
    )

    grouped_brands = [
        (
            "Xe phổ thông",
            [
                normalize_brand_name(
                    brand
                )
                for brand in MASS_MARKET_BRANDS
            ],
            "vehicle-segment-mass",
        ),
        (
            "Xe sang",
            [
                normalize_brand_name(
                    brand
                )
                for brand in LUXURY_BRANDS
            ],
            "vehicle-segment-luxury",
        ),
        (
            "Khác",
            other_brands,
            "vehicle-segment-other",
        ),
    ]

    st.markdown(
        "<div style='height: 8px;'></div>",
        unsafe_allow_html=True,
    )

    left_column, right_column = (
        st.columns(
            [0.86, 1.14]
        )
    )

    with left_column:
        bubble_card = st.container(
            key="vehicle_segment_bubble_card"
        )

        with bubble_card:
            st.markdown(
                '<div class="vehicle-segment-card-title">'
                'Cơ cấu theo phân khúc xe'
                '</div>',
                unsafe_allow_html=True,
            )

            bubble_figure = (
                build_vehicle_segment_bubble_chart(
                    segment_summary
                )
            )

            st.plotly_chart(
                bubble_figure,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

            render_vehicle_segment_legend()

    with right_column:
        group_card = st.container(
            key="vehicle_segment_group_card"
        )

        with group_card:
            st.markdown(
                '<div class="vehicle-segment-card-title">'
                'Chi tiết hãng xe theo phân khúc'
                '</div>',
                unsafe_allow_html=True,
            )

            table_html = """
            <div class="vehicle-segment-table-wrap">
                <table class="vehicle-segment-table">
                    <thead>
                        <tr>
                            <th>Phân khúc</th>
                            <th>Hãng xe</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for (
                group_name,
                brands,
                group_class,
            ) in grouped_brands:
                display_brands = (
                    brands
                    if brands
                    else ["-"]
                )

                row_count = len(
                    display_brands
                )

                for index, brand_name in enumerate(
                    display_brands
                ):
                    table_html += "<tr>"

                    if index == 0:
                        table_html += (
                            '<td class="vehicle-segment-merged '
                            f'{group_class}" '
                            f'rowspan="{row_count}">'
                            f'{html.escape(group_name)}'
                            "</td>"
                        )

                    table_html += (
                        "<td>"
                        f"{html.escape(brand_name)}"
                        "</td>"
                    )

                    table_html += "</tr>"

            table_html += """
                    </tbody>
                </table>
            </div>
            """

            st.markdown(
                table_html,
                unsafe_allow_html=True,
            )



# ============================================================
# ĐỊNH DẠNG BẢNG
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
                "text-align": "left",
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
                        (
                            "text-align",
                            "left",
                        ),
                    ],
                },
            ],
            overwrite=False,
        )
        .hide(axis="index")
    )


# ============================================================
# CHUẨN BỊ DỮ LIỆU THEO NGÀY
# ============================================================

def prepare_daily_data(
    data,
    year,
    month,
    target_ro,
    target_revenue,
    working_days,
):
    daily_source = data.dropna(
        subset=["ngay_hoa_don"]
    ).copy()

    daily_source[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        daily_source[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    # ========================================================
    # THÁNG = ALL
    # Giữ nguyên hình dáng/màu chart.
    # Chỉ đổi đơn vị trục X từ ngày sang tháng.
    # ========================================================

    if month == "All":
        days = list(
            range(
                1,
                13,
            )
        )

        daily = (
            daily_source
            .assign(
                day=lambda dataframe:
                dataframe[
                    "ngay_hoa_don"
                ].dt.month
            )
            .groupby("day")
            .agg(
                ro=(
                    "ro",
                    "nunique",
                ),
                revenue=(
                    "doanh_thu_truoc_thue",
                    "sum",
                ),
            )
            .reindex(
                days,
                fill_value=0,
            )
            .reset_index()
        )

        daily[
            "revenue_m"
        ] = (
            daily["revenue"]
            / 1_000_000
        )

        daily["cum_ro"] = (
            daily["ro"].cumsum()
        )

        daily[
            "cum_revenue"
        ] = (
            daily[
                "revenue"
            ].cumsum()
        )

        target_ro_day = safe_div(
            target_ro,
            12,
        )

        target_revenue_day = (
            safe_div(
                target_revenue,
                12,
            )
        )

        daily[
            "target_cum_ro"
        ] = (
            daily["day"]
            * target_ro_day
        )

        daily[
            "target_cum_revenue"
        ] = (
            daily["day"]
            * target_revenue_day
        )

    else:
        days_in_month = calendar.monthrange(
            year,
            int(month),
        )[1]

        days = list(
            range(
                1,
                days_in_month + 1,
            )
        )

        daily = (
            daily_source
            .assign(
                day=lambda dataframe:
                dataframe[
                    "ngay_hoa_don"
                ].dt.day
            )
            .groupby("day")
            .agg(
                ro=(
                    "ro",
                    "nunique",
                ),
                revenue=(
                    "doanh_thu_truoc_thue",
                    "sum",
                ),
            )
            .reindex(
                days,
                fill_value=0,
            )
            .reset_index()
        )

        daily[
            "revenue_m"
        ] = (
            daily["revenue"]
            / 1_000_000
        )

        daily["cum_ro"] = (
            daily["ro"].cumsum()
        )

        daily[
            "cum_revenue"
        ] = (
            daily[
                "revenue"
            ].cumsum()
        )

        target_ro_day = safe_div(
            target_ro,
            working_days,
        )

        target_revenue_day = (
            safe_div(
                target_revenue,
                working_days,
            )
        )

        daily[
            "target_cum_ro"
        ] = [
            target_ro_day
            * min(
                day,
                working_days,
            )
            for day in daily[
                "day"
            ]
        ]

        daily[
            "target_cum_revenue"
        ] = [
            target_revenue_day
            * min(
                day,
                working_days,
            )
            for day in daily[
                "day"
            ]
        ]

    daily["cum_ro_pct"] = (
        daily["cum_ro"]
        / daily[
            "target_cum_ro"
        ]
        * 100
    )

    daily[
        "cum_revenue_pct"
    ] = (
        daily[
            "cum_revenue"
        ]
        / daily[
            "target_cum_revenue"
        ]
        * 100
    )

    daily["cum_ro_pct"] = (
        daily["cum_ro_pct"]
        .replace(
            [
                float("inf"),
                -float("inf"),
            ],
            0,
        )
        .fillna(0)
    )

    daily[
        "cum_revenue_pct"
    ] = (
        daily[
            "cum_revenue_pct"
        ]
        .replace(
            [
                float("inf"),
                -float("inf"),
            ],
            0,
        )
        .fillna(0)
    )

    return (
        daily,
        days,
        target_ro_day,
        target_revenue_day,
    )


# ============================================================
# BIỂU ĐỒ LƯỢT XE THEO NGÀY
# ============================================================

def build_ro_daily_chart(
    daily,
    days,
    workshop,
    has_target=True,
):
    figure = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    figure.add_trace(
        go.Bar(
            x=daily["day"],
            y=daily["ro"],

            marker=dict(
                color=CPUS_BAR_COLOR,
                line=dict(
                    color=CPUS_BAR_BORDER,
                    width=1,
                ),
            ),

            name="RO/ngày",

            text=[
                f"{int(value)}"
                if value > 0
                else ""
                for value in daily["ro"]
            ],

            textposition="outside",

            textfont=dict(
                color=BAR_LABEL_COLOR,
                size=14,
            ),

            cliponaxis=False,
        ),
        secondary_y=False,
    )

    if has_target:
        figure.add_trace(
            go.Scatter(
                x=daily["day"],
                y=daily["cum_ro_pct"],

                mode="lines+markers+text",

                line=dict(
                    color=CUMULATIVE_LINE_COLOR,
                    width=3,
                    dash="dot",
                ),

                marker=dict(
                    size=7,
                    color=CUMULATIVE_MARKER_COLOR,
                    line=dict(
                        color=CUMULATIVE_MARKER_BORDER,
                        width=1,
                    ),
                ),

                text=[
                    f"{value:.0f}%"
                    if value > 0
                    else ""
                    for value in daily[
                        "cum_ro_pct"
                    ]
                ],

                textposition="bottom center",

                textfont=dict(
                    size=10,
                    color=DAILY_CHART_TEXT,
                ),

                name="% đạt lũy kế",
            ),
            secondary_y=True,
        )

    figure.update_layout(
        template="simple_white",
        height=370,
        paper_bgcolor=DAILY_CHART_BG,
        plot_bgcolor=DAILY_CHART_BG,
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#E9ECF3",
            font=dict(
                color="#1E2F6E",
            ),
        ),

        font=dict(
            color=DAILY_CHART_TEXT,
        ),

        margin=dict(
            l=30,
            r=30,
            t=65,
            b=40,
        ),

        showlegend=False,
        bargap=0.18,

        title=dict(
            text=(
                f"CPUS DAILY - "
                f"{workshop.upper()}"
            ),
            x=0.5,
            font=dict(
                size=19,
                color=DAILY_CHART_TITLE,
            ),
        ),
    )

    figure.update_xaxes(
        tickmode="array",
        tickvals=days,
        showgrid=False,
        color=DAILY_CHART_AXIS,
        linecolor="#DAD1D2",
        zeroline=False,
    )

    figure.update_yaxes(
        showgrid=True,
        gridcolor=DAILY_CHART_GRID,
        color=DAILY_CHART_AXIS,
        zeroline=False,
        secondary_y=False,
    )

    figure.update_yaxes(
        range=[0, 300],
        ticksuffix="%",
        showgrid=False,
        color=DAILY_CHART_AXIS,
        zeroline=False,
        secondary_y=True,
    )

    return figure


# ============================================================
# BIỂU ĐỒ DOANH THU THEO NGÀY
# ============================================================

def build_revenue_daily_chart(
    daily,
    days,
    workshop,
    has_target=True,
):
    figure = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    figure.add_trace(
        go.Bar(
            x=daily["day"],
            y=daily["revenue_m"],

            marker=dict(
                color=REVENUE_BAR_COLOR,
                line=dict(
                    color=REVENUE_BAR_BORDER,
                    width=1,
                ),
            ),

            name="Doanh thu/ngày",

            text=[
                f"{value:.1f}M"
                if value > 0
                else ""
                for value in daily[
                    "revenue_m"
                ]
            ],

            textposition="outside",

            textfont=dict(
                color=BAR_LABEL_COLOR,
                size=14,
            ),

            cliponaxis=False,
        ),
        secondary_y=False,
    )

    if has_target:
        figure.add_trace(
            go.Scatter(
                x=daily["day"],
                y=daily[
                    "cum_revenue_pct"
                ],

                mode="lines+markers+text",

                line=dict(
                    color=CUMULATIVE_LINE_COLOR,
                    width=3,
                    dash="dot",
                ),

                marker=dict(
                    size=7,
                    color=CUMULATIVE_MARKER_COLOR,
                    line=dict(
                        color=CUMULATIVE_MARKER_BORDER,
                        width=1,
                    ),
                ),

                text=[
                    f"{value:.0f}%"
                    if value > 0
                    else ""
                    for value in daily[
                        "cum_revenue_pct"
                    ]
                ],

                textposition="bottom center",

                textfont=dict(
                    size=10,
                    color=DAILY_CHART_TEXT,
                ),

                name="% đạt lũy kế",
            ),
            secondary_y=True,
        )

    figure.update_layout(
        template="simple_white",
        height=370,
        paper_bgcolor=DAILY_CHART_BG,
        plot_bgcolor=DAILY_CHART_BG,
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#E9ECF3",
            font=dict(
                color="#1E2F6E",
            ),
        ),

        font=dict(
            color=DAILY_CHART_TEXT,
        ),

        margin=dict(
            l=30,
            r=30,
            t=65,
            b=40,
        ),

        showlegend=False,
        bargap=0.18,

        title=dict(
            text=(
                f"DOANH THU DAILY - "
                f"{workshop.upper()}"
            ),
            x=0.5,
            font=dict(
                size=19,
                color=DAILY_CHART_TITLE,
            ),
        ),
    )

    figure.update_xaxes(
        tickmode="array",
        tickvals=days,
        showgrid=False,
        color=DAILY_CHART_AXIS,
        linecolor="#DAD1D2",
        zeroline=False,
    )

    figure.update_yaxes(
        showgrid=True,
        gridcolor=DAILY_CHART_GRID,
        color=DAILY_CHART_AXIS,
        zeroline=False,
        secondary_y=False,
    )

    figure.update_yaxes(
        range=[0, 300],
        ticksuffix="%",
        showgrid=False,
        color=DAILY_CHART_AXIS,
        zeroline=False,
        secondary_y=True,
    )

    return figure


# ============================================================
# HIỂN THỊ BIỂU ĐỒ THEO NGÀY
# ============================================================

def render_daily_charts(
    data,
    year,
    month,
    workshop,
    target_ro,
    target_revenue,
    working_days,
    target_available=True,
):
    is_year_view = (
        month == "All"
    )

    if is_year_view:
        st.markdown(
            "## 2. Lượt xe & Doanh thu theo tháng"
        )
    else:
        st.markdown(
            "## 2. Lượt xe & Doanh thu theo ngày"
        )

    (
        daily,
        days,
        target_ro_day,
        target_revenue_day,
    ) = prepare_daily_data(
        data=data,
        year=year,
        month=month,
        target_ro=target_ro,
        target_revenue=target_revenue,
        working_days=working_days,
    )

    total_ro = daily[
        "ro"
    ].sum()

    total_revenue = daily[
        "revenue"
    ].sum()

    if is_year_view:
        period_count = 12

        actual_ro_average = safe_div(
            total_ro,
            period_count,
        )

        actual_revenue_average = safe_div(
            total_revenue,
            period_count,
        )
    else:
        actual_ro_average = safe_div(
            total_ro,
            working_days,
        )

        actual_revenue_average = safe_div(
            total_revenue,
            working_days,
        )

    revenue_per_cpus = safe_div(
        total_revenue,
        total_ro,
    )

    # HÀNG 1: CPUS
    ro_chart_column, ro_kpi_column = (
        st.columns(
            [4.6, 1.25]
        )
    )

    with ro_chart_column:
        ro_figure = build_ro_daily_chart(
            daily=daily,
            days=days,
            workshop=workshop,
            has_target=target_available,
        )

        ro_chart_card = st.container(
            key="ro_daily_chart_card"
        )

        with ro_chart_card:
            st.plotly_chart(
                ro_figure,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": False,
                },
            )

    with ro_kpi_column:
        if is_year_view:
            render_mini_kpi(
                "CPUS TB/THÁNG",
                f"{actual_ro_average:.0f}",
            )

            if target_available:
                render_mini_kpi(
                    "CPUS/THÁNG TARGET",
                    f"{target_ro_day:.0f}",
                )
        else:
            render_mini_kpi(
                "CPUS TB/NGÀY",
                f"{actual_ro_average:.0f}",
            )

            if target_available:
                render_mini_kpi(
                    "CPUS/NGÀY TARGET",
                    f"{target_ro_day:.0f}",
                )

    # HÀNG 2: DOANH THU
    revenue_chart_column, revenue_kpi_column = (
        st.columns(
            [4.6, 1.25]
        )
    )

    with revenue_chart_column:
        revenue_figure = (
            build_revenue_daily_chart(
                daily=daily,
                days=days,
                workshop=workshop,
                has_target=target_available,
            )
        )

        revenue_chart_card = st.container(
            key="revenue_daily_chart_card"
        )

        with revenue_chart_card:
            st.plotly_chart(
                revenue_figure,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": False,
                },
            )

    with revenue_kpi_column:
        render_mini_kpi(
            "DT TB/CPUS",
            fmt_m(
                revenue_per_cpus
            ),
        )

        if is_year_view:
            render_mini_kpi(
                "DT TB/THÁNG",
                fmt_m(
                    actual_revenue_average
                ),
            )

            if target_available:
                render_mini_kpi(
                    "DT TB/THÁNG TARGET",
                    fmt_m(
                        target_revenue_day
                    ),
                )
        else:
            render_mini_kpi(
                "DT TB/NGÀY",
                fmt_m(
                    actual_revenue_average
                ),
            )

            if target_available:
                render_mini_kpi(
                    "DT TB/NGÀY TARGET",
                    fmt_m(
                        target_revenue_day
                    ),
                )


# ============================================================
# HÃNG XE
# ============================================================

def render_brand_section(data):
    st.markdown(
        "## 3. Hãng xe"
    )

    required_columns = [
        "ro",
        "hang_xe",
        "doanh_thu_truoc_thue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            "Dữ liệu phần Hãng xe thiếu các cột: "
            + ", ".join(missing_columns)
        )
        st.stop()

    brand_data = data.copy()

    brand_data[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        brand_data[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    brand_data[
        "hang_xe"
    ] = (
        brand_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.strip()
    )

    # Danh sách lệnh và hãng lấy từ file Lệnh sửa chữa.
    # Doanh thu theo hãng dùng Tổng trước thuế.
    brand_summary = (
        brand_data
        .groupby(
            "hang_xe"
        )
        .agg(
            so_ro=(
                "ro",
                "nunique",
            ),
            doanh_thu=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
        .sort_values(
            "doanh_thu",
            ascending=False,
        )
    )

    total_ro_brand = (
        brand_summary[
            "so_ro"
        ].sum()
    )

    total_revenue_brand = (
        brand_summary[
            "doanh_thu"
        ].sum()
    )

    brand_summary[
        "ty_trong_ro"
    ] = (
        brand_summary["so_ro"]
        / total_ro_brand
        if total_ro_brand
        else 0
    )

    brand_summary[
        "ty_trong_doanh_thu"
    ] = (
        brand_summary["doanh_thu"]
        / total_revenue_brand
        if total_revenue_brand
        else 0
    )

    brand_display = (
        brand_summary.copy()
    )

    brand_display[
        "doanh_thu"
    ] = (
        brand_display[
            "doanh_thu"
        ].map(fmt_m)
    )

    brand_display[
        "ty_trong_ro"
    ] = (
        brand_display[
            "ty_trong_ro"
        ]
        .map(
            lambda value:
            f"{value:.0%}"
        )
    )

    brand_display[
        "ty_trong_doanh_thu"
    ] = (
        brand_display[
            "ty_trong_doanh_thu"
        ]
        .map(
            lambda value:
            f"{value:.0%}"
        )
    )

    brand_display = (
        brand_display.rename(
            columns={
                "hang_xe": "Hãng xe",
                "so_ro": "Số RO",
                "doanh_thu": (
                    "Doanh thu trước thuế"
                ),
                "ty_trong_ro": (
                    "Tỷ trọng RO"
                ),
                "ty_trong_doanh_thu": (
                    "Tỷ trọng doanh thu"
                ),
            }
        )
    )

    # Chuyển Số RO sang chuỗi để Streamlit căn trái.
    brand_display["Số RO"] = (
        brand_display["Số RO"]
        .astype(int)
        .astype(str)
    )

    total_row = pd.DataFrame(
        {
            "Hãng xe": [
                "TỔNG"
            ],
            "Số RO": [
                str(
                    int(
                        total_ro_brand
                    )
                )
            ],
            "Doanh thu trước thuế": [
                fmt_m(
                    total_revenue_brand
                )
            ],
            "Tỷ trọng RO": [
                "100%"
            ],
            "Tỷ trọng doanh thu": [
                "100%"
            ],
        }
    )

    brand_display = pd.concat(
        [
            brand_display,
            total_row,
        ],
        ignore_index=True,
    )

    left_column, right_column = (
        st.columns(
            [1.35, 1]
        )
    )

    # ========================================================
    # BẢNG CHI TIẾT
    # ========================================================

    with left_column:
        st.markdown(
            '<div class="section-label">'
            'Bảng chi tiết theo hãng xe'
            '</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            style_white_table(
                brand_display
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # BIỂU ĐỒ TOP HÃNG XE
    # ========================================================

    with right_column:
        st.markdown(
            '<div class="section-label">'
            'Top hãng xe theo doanh thu'
            '</div>',
            unsafe_allow_html=True,
        )

        brand_chart = (
            brand_summary
            .head(10)
            .sort_values(
                "doanh_thu",
                ascending=True,
            )
            .copy()
        )

        brand_chart[
            "doanh_thu_m"
        ] = (
            brand_chart[
                "doanh_thu"
            ]
            / 1_000_000
        )

        # Gradient vàng Carpla từ trên xuống dưới:
        # hãng đứng đầu đậm nhất, các hãng phía dưới nhạt dần.
        carpla_yellow_gradient = [
            "#F1CD54",
            "#F3D467",
            "#F5DA7A",
            "#F7E08D",
            "#F8E6A0",
            "#F9EAB0",
            "#FBEFC0",
            "#FCF3CF",
            "#FDF7DE",
            "#FFFBEE",
        ]

        # brand_chart đang sort tăng dần để hãng doanh thu
        # cao nhất hiển thị ở trên cùng trong horizontal bar.
        color_list = list(
            reversed(
                carpla_yellow_gradient[
                    :len(brand_chart)
                ]
            )
        )

        figure = go.Figure()

        figure.add_trace(
            go.Bar(
                x=brand_chart[
                    "doanh_thu_m"
                ],
                y=brand_chart[
                    "hang_xe"
                ],

                orientation="h",

                marker=dict(
                    color=color_list,
                    line=dict(
                        color="#E5ECF6",
                        width=0.5,
                    ),
                ),

                text=[
                    f"{value:.1f}M"
                    for value
                    in brand_chart[
                        "doanh_thu_m"
                    ]
                ],

                textposition="outside",

                textfont=dict(
                    color="#667085",
                    size=12,
                ),

                cliponaxis=False,

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Doanh thu trước thuế: "
                    "%{x:.1f}M"
                    "<extra></extra>"
                ),
            )
        )

        figure.update_layout(
            template="simple_white",

            # Chỉ giảm chiều cao để cân với bảng.
            height=403,

            margin=dict(
                l=24,
                r=62,
                t=18,
                b=42,
            ),

            xaxis_title=(
                "Doanh thu trước thuế (M)"
            ),

            yaxis_title="",

            paper_bgcolor="white",
            plot_bgcolor="white",

            font=dict(
                color="#475467",
            ),

            showlegend=False,
        )

        figure.update_xaxes(
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False,

            title_font=dict(
                color="#667085",
            ),

            tickfont=dict(
                color="#667085",
            ),
        )

        figure.update_yaxes(
            showgrid=False,

            tickfont=dict(
                color="#667085",
            ),
        )

        # Container chỉ dùng để bo góc ô graph này.
        chart_card = st.container(
            key="brand_revenue_chart_card"
        )

        with chart_card:
            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    st.markdown(
        "<div style='height: 2px;'></div>",
        unsafe_allow_html=True,
    )

    render_brand_relationship_section(
        brand_data
    )

    render_vehicle_segment_section(
        brand_data
    )


# ============================================================
# CƠ CẤU NGUỒN THANH TOÁN
# ============================================================

def render_payment_section(data):
    st.markdown(
        "## 4. Cơ cấu nguồn thanh toán"
    )

    required_columns = [
        "khach_hang_chi_tra",
        "bao_hiem_chi_tra",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            "Thiếu cột nguồn thanh toán: "
            + ", ".join(missing_columns)
        )
        return 0

    payment_css = """
    <style>
    .payment-chart-title {
        color: #1F2937;
        font-size: 20px;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
        padding: 16px 2px 6px 2px;
    }

    .payment-legend {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 24px;
        width: 100%;
        flex-wrap: nowrap;
        margin-top: -6px;
        margin-bottom: 10px;
        font-size: 12.5px;
        font-weight: 600;
        color: #475467;
    }

    .payment-legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }

    .payment-legend-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        display: inline-block;
        flex: 0 0 9px;
    }

    .st-key-payment_donut_card {
        width: 100%;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        box-sizing: border-box;
        padding: 0 18px 16px 18px;
        overflow: hidden;
    }

    .st-key-payment_donut_card div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    .st-key-payment_donut_card div[data-testid="stPlotlyChart"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """

    st.markdown(
        payment_css,
        unsafe_allow_html=True,
    )

    customer_value = pd.to_numeric(
        data["khach_hang_chi_tra"],
        errors="coerce",
    ).fillna(0).sum()

    insurance_value = pd.to_numeric(
        data["bao_hiem_chi_tra"],
        errors="coerce",
    ).fillna(0).sum()

    total_payment = (
        customer_value
        + insurance_value
    )

    payment_structure = pd.DataFrame(
        {
            "Nguồn thanh toán": [
                "Bảo hiểm chi trả",
                "Khách hàng chi trả",
            ],
            "Giá trị": [
                insurance_value,
                customer_value,
            ],
        }
    )

    payment_structure[
        "Tỷ trọng"
    ] = payment_structure[
        "Giá trị"
    ].apply(
        lambda value:
        safe_div(
            value,
            total_payment,
        )
    )

    payment_display = (
        payment_structure.copy()
    )

    payment_display[
        "Giá trị"
    ] = payment_display[
        "Giá trị"
    ].map(
        fmt_m
    )

    payment_display[
        "Tỷ trọng"
    ] = payment_display[
        "Tỷ trọng"
    ].map(
        lambda value:
        f"{value:.2%}"
    )

    total_row = pd.DataFrame(
        {
            "Nguồn thanh toán": [
                "TỔNG"
            ],
            "Giá trị": [
                fmt_m(
                    total_payment
                )
            ],
            "Tỷ trọng": [
                "100.00%"
            ],
        }
    )

    payment_display = pd.concat(
        [
            payment_display,
            total_row,
        ],
        ignore_index=True,
    )

    left_column, right_column = (
        st.columns(
            [1, 1]
        )
    )

    with left_column:
        st.dataframe(
            style_white_table(
                payment_display
            ),
            use_container_width=True,
            hide_index=True,
        )

    with right_column:
        payment_chart_card = st.container(
            key="payment_donut_card"
        )

        with payment_chart_card:
            st.markdown(
                '<div class="payment-chart-title">'
                'Tỷ trọng nguồn thanh toán'
                '</div>',
                unsafe_allow_html=True,
            )

            figure = go.Figure(
                data=[
                    go.Pie(
                        labels=[
                            "Khách hàng chi trả",
                            "Bảo hiểm chi trả",
                        ],
                        values=[
                            customer_value,
                            insurance_value,
                        ],
                        hole=0.60,
                        marker=dict(
                            colors=[
                                DONUT_MAIN,
                                DONUT_SECOND,
                            ]
                        ),
                        textinfo="percent",
                        texttemplate=(
                            "%{percent:.0%}"
                        ),
                        textfont=dict(
                            size=14,
                            color="white",
                        ),
                        domain=dict(
                            x=[0.22, 0.68],
                            y=[0.20, 0.88],
                        ),
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Giá trị: %{value:,.0f}<br>"
                            "Tỷ trọng: %{percent:.2%}"
                            "<extra></extra>"
                        ),
                    )
                ]
            )

            figure.update_layout(
                template="simple_white",
                height=300,
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0,
                ),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#475467",
                ),
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

            payment_legend_html = (
                '<div class="payment-legend">'
                '<div class="payment-legend-item">'
                f'<span class="payment-legend-dot" style="background:{DONUT_MAIN};"></span>'
                '<span>Khách hàng chi trả</span>'
                '</div>'
                '<div class="payment-legend-item">'
                f'<span class="payment-legend-dot" style="background:{DONUT_SECOND};"></span>'
                '<span>Bảo hiểm chi trả</span>'
                '</div>'
                '</div>'
            )

            st.markdown(
                payment_legend_html,
                unsafe_allow_html=True,
            )

    return total_payment
