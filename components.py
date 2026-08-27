# FIX_VERSION: HANOI_2026_ONLY + HOMEPAGE_RED_GRADIENT_BUTTON
import math
from pathlib import Path
import base64

import streamlit as st

from custom_slider import carpla_slider


# ============================================================
# HÀM FORMAT
# ============================================================

def fmt_m(value):
    return f"{value / 1_000_000:,.1f}M"


def fmt_m0(value):
    return f"{value / 1_000_000:,.1f}M"


# ============================================================
# KPI CARD
# ============================================================

def render_kpi_card(
    title,
    value,
    badge=None,
):
    badge_html = (
        f'<div class="card-badge">{badge}</div>'
        if badge
        else ""
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROGRESS CARD
# ============================================================

def render_progress_card(
    title,
    actual_text,
    target_text,
    rate,
):
    percentage = rate * 100
    percentage_display = max(
        0,
        min(percentage, 100),
    )

    html = f"""
<div class="section-card">
    <div class="progress-title">{title}</div>
    <div class="progress-sub">Thực hiện: {actual_text} / {target_text}</div>
    <div class="progress-track">
        <div class="progress-fill" style="width:{percentage_display}%;"></div>
        <div class="progress-dot" style="left:{percentage_display}%;"></div>
        <div class="progress-label" style="left:{percentage_display}%;">{percentage:.0f}%</div>
    </div>
    <div class="progress-scale">
        <span>0%</span>
        <span>100%</span>
    </div>
</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True,
    )

# ============================================================
# MINI KPI
# ============================================================

def render_mini_kpi(
    title,
    value,
    badge=None,
):
    badge_html = (
        f'<div class="mini-kpi-badge">{badge}</div>'
        if badge
        else ""
    )

    st.markdown(
        f"""
        <div class="mini-kpi">
            <div class="mini-kpi-title">{title}</div>
            <div class="mini-kpi-value">{value}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR FILTER
# ============================================================

def render_sidebar(branch_workshop_codes):
    if "show_dashboard" not in st.session_state:
        st.session_state.show_dashboard = False

    if "selected_branch" not in st.session_state:
        st.session_state.selected_branch = None

    if "selected_workshop" not in st.session_state:
        st.session_state.selected_workshop = None

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = None

    if "selected_month" not in st.session_state:
        st.session_state.selected_month = None

    st.sidebar.markdown("## Bộ lọc")

    # =========================================================
    # 1. CHI NHÁNH
    # =========================================================

    branch_options = [
        "All"
    ] + list(
        branch_workshop_codes.keys()
    )

    selected_branch_input = (
        st.sidebar.selectbox(
            "Chi nhánh",
            options=branch_options,
            index=None,
            placeholder=" ",
            key="sidebar_branch",
        )
    )

    # =========================================================
    # 2. XƯỞNG
    # =========================================================

    if selected_branch_input is None:
        workshop_options = []

    elif selected_branch_input == "All":
        workshop_options = [
            "All"
        ]

    else:
        workshop_options = [
            "All"
        ] + sorted(
            branch_workshop_codes.get(
                selected_branch_input,
                {},
            ).keys()
        )

    selected_workshop_input = (
        st.sidebar.selectbox(
            "Xưởng",
            options=workshop_options,
            index=None,
            placeholder=" ",
            key="sidebar_workshop",
        )
    )

    # =========================================================
    # 3. NĂM
    # =========================================================

    if (
        selected_branch_input is not None
        and selected_workshop_input is not None
    ):
        year_options = [
            2026
        ]
    else:
        year_options = []

    selected_year_input = (
        st.sidebar.selectbox(
            "Năm",
            options=year_options,
            index=None,
            placeholder=" ",
            key="sidebar_year",
        )
    )

    # =========================================================
    # 4. THÁNG
    # =========================================================

    if selected_year_input is not None:
        from datetime import date

        today = date.today()

        if int(selected_year_input) == today.year:
            max_month = today.month
        elif int(selected_year_input) < today.year:
            max_month = 12
        else:
            max_month = 0

        month_options = (
            ["All"]
            + list(
                range(
                    1,
                    max_month + 1,
                )
            )
        )
    else:
        month_options = []

    selected_month_input = (
        st.sidebar.selectbox(
            "Tháng",
            options=month_options,
            index=None,
            placeholder=" ",
            format_func=(
                lambda value:
                "All"
                if value == "All"
                else str(
                    int(value)
                )
            ),
            key="sidebar_month",
        )
    )

    # =========================================================
    # 5. NÚT XEM DASHBOARD
    # =========================================================

    all_selected = all([
        selected_branch_input is not None,
        selected_workshop_input is not None,
        selected_year_input is not None,
        selected_month_input is not None,
    ])

    if st.sidebar.button(
        "XEM DASHBOARD",
        type="primary",
        use_container_width=True,
        disabled=not all_selected,
    ):
        st.session_state.selected_branch = (
            selected_branch_input
        )

        st.session_state.selected_workshop = (
            selected_workshop_input
        )

        st.session_state.selected_year = int(
            selected_year_input
        )

        if (
            selected_month_input
            == "All"
        ):
            st.session_state.selected_month = (
                "All"
            )
        else:
            st.session_state.selected_month = int(
                selected_month_input
            )

        st.session_state.show_dashboard = True
        st.rerun()

    # =========================================================
    # 6. NÚT TRANG CHỦ
    # =========================================================

    if st.session_state.show_dashboard:
        if st.sidebar.button(
            "← TRANG CHỦ",
            use_container_width=True,
        ):
            st.session_state.show_dashboard = False

            st.session_state.selected_branch = None
            st.session_state.selected_workshop = None
            st.session_state.selected_year = None
            st.session_state.selected_month = None

            for key in [
                "sidebar_branch",
                "sidebar_workshop",
                "sidebar_year",
                "sidebar_month",
            ]:
                if key in st.session_state:
                    del st.session_state[
                        key
                    ]

            st.rerun()

    return {
        "show_dashboard": (
            st.session_state.show_dashboard
        ),
        "branch": (
            st.session_state.get(
                "selected_branch"
            )
        ),
        "workshop": (
            st.session_state.get(
                "selected_workshop"
            )
        ),
        "year": (
            st.session_state.get(
                "selected_year"
            )
        ),
        "month": (
            st.session_state.get(
                "selected_month"
            )
        ),
    }


# ============================================================
# TASCO AUTO WORDMARK - HOMEPAGE
# ============================================================

def _build_tasco_wordmark_html():
    """
    Dùng file PNG đã xử lý sẵn:
    tasco_auto_logo_navy.png

    - nền trong suốt
    - chữ navy #1E2F6E
    - đặt nhỏ ở góc trên trái của homepage-card
    """

    tasco_logo_path = (
        Path(__file__).resolve().parent
        / "tasco_auto_logo_navy.png"
    )

    if not tasco_logo_path.exists():
        return (
            '<div style="'
            'position:absolute;'
            'top:24px;'
            'left:30px;'
            'z-index:5;'
            'color:#1E2F6E;'
            'font-size:15px;'
            'line-height:0.95;'
            'font-weight:900;'
            'letter-spacing:0.4px;'
            'text-align:left;'
            '">'
            'TASCO<br>AUTO'
            '</div>'
        )

    tasco_base64 = base64.b64encode(
        tasco_logo_path.read_bytes()
    ).decode("utf-8")

    return (
        '<img '
        f'src="data:image/png;base64,{tasco_base64}" '
        'alt="TASCO AUTO" '
        'style="'
        'position:absolute;'
        'top:22px;'
        'left:28px;'
        'width:118px;'
        'height:auto;'
        'z-index:5;'
        'display:block;'
        'object-fit:contain;'
        '">'
    )


# ============================================================
# HOMEPAGE
# ============================================================

def render_homepage(logo_path: Path):
    st.markdown(
        "<div style='height:18px;'></div>",
        unsafe_allow_html=True,
    )

    if logo_path.exists():
        logo_base64 = base64.b64encode(
            logo_path.read_bytes()
        ).decode("utf-8")

        logo_html = (
            f'<img src="data:image/png;base64,{logo_base64}" '
            'style="width:360px;max-width:72%;height:auto;'
            'display:block;margin:0 auto;">'
        )
    else:
        logo_html = (
            '<div style="font-size:42px;font-weight:900;'
            'color:#172554;">CARPLA SERVICES</div>'
        )

    tasco_wordmark_html = (
        _build_tasco_wordmark_html()
    )

    html = (
        '<div class="homepage-stage">'
            '<div class="homepage-card">'

                # TASCO AUTO nhỏ ở góc trên trái của inner card
                f'{tasco_wordmark_html}'

                # CARPLA SERVICES giữ nguyên ở giữa
                f'{logo_html}'

                '<div class="homepage-title">'
                    'DASHBOARD QUẢN TRỊ DMS'
                '</div>'

                '<div class="homepage-subtitle">'
                    'Nền tảng dashboard tập trung giúp theo dõi, '
                    'phân tích và đánh giá hiệu quả hoạt động của '
                    'các xưởng trong toàn hệ thống Carpla Services.'
                '</div>'

                '<div class="homepage-feature-grid">'
                    '<div class="homepage-feature-item">'
                        '🚗 <span>Lượt xe</span>'
                    '</div>'
                    '<div class="homepage-feature-item">'
                        '📊 <span>Doanh thu</span>'
                    '</div>'
                    '<div class="homepage-feature-item">'
                        '📦 <span>Cơ cấu xe</span>'
                    '</div>'
                    '<div class="homepage-feature-item">'
                        '💳 <span>Thanh toán</span>'
                    '</div>'
                    '<div class="homepage-feature-item">'
                        '📈 <span>KPI vận hành</span>'
                    '</div>'
                '</div>'

                '<div class="homepage-guide">'
                    '<span style="'
                        'display:inline-flex;'
                        'align-items:center;'
                        'justify-content:center;'
                        'padding:13px 24px;'
                        'border-radius:14px;'
                        'background:linear-gradient('
                            '135deg,'
                            '#FF6969 0%,'
                            '#FF4F4F 52%,'
                            '#E93E3E 100%'
                        ');'
                        'color:#FFFFFF;'
                        'font-size:15px;'
                        'line-height:1.35;'
                        'font-weight:800;'
                        'letter-spacing:0.15px;'
                        'border:1px solid rgba(255,255,255,0.30);'
                        'box-shadow:'
                            '0 10px 22px rgba(233,62,62,0.28),'
                            '0 0 18px rgba(255,90,90,0.12),'
                            'inset 0 1px 0 rgba(255,255,255,0.32);'
                        'text-shadow:0 1px 2px rgba(122,26,26,0.18);'
                        'white-space:normal;'
                        'text-align:center;'
                        'max-width:760px;'
                    '">'
                        'Vui lòng chọn Chế độ xem tại bộ lọc bên trái để bắt đầu.'
                    '</span>'
                '</div>'

            '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO DASHBOARD
# ============================================================

def render_dashboard_header(
    branch,
    workshop,
    year,
    month,
):
    # Tên phạm vi
    if branch == "All":
        title_scope = "Toàn HO"
        subtitle_scope = "Toàn hệ thống"
    elif workshop == "All":
        title_scope = (
            f"Chi nhánh {branch}"
        )
        subtitle_scope = (
            f"Chi nhánh {branch}"
        )
    else:
        title_scope = (
            f"Xưởng {workshop}"
        )
        subtitle_scope = (
            f"Chi nhánh {branch}"
        )

    # Tên kỳ
    if month == "All":
        period_text = (
            f"năm {year}"
        )
    else:
        period_text = (
            f"tháng {month}/{year}"
        )

    html = f"""
<div class="hero-box">
    <div class="hero-title">Dashboard DMS - {title_scope}</div>
    <div class="hero-subtitle">{subtitle_scope} | Theo dõi hiệu quả hoạt động {period_text}: lượt xe, doanh thu, cơ cấu hãng xe và nguồn thanh toán</div>
</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# TOP KPI SECTION
# ============================================================

def render_top_kpis(metrics):
    actual_ro = metrics["actual_ro"]
    actual_revenue = metrics["actual_revenue"]
    total_after_tax = metrics["total_after_tax"]
    revenue_per_ro = metrics["revenue_per_ro"]

    target_available = metrics.get(
        "target_available",
        False,
    )

    target_ro = metrics["target_ro"]
    target_revenue = metrics["target_revenue"]

    ro_rate = metrics["ro_rate"]
    revenue_rate = metrics["revenue_rate"]

    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        if target_available:
            render_kpi_card(
                "Lượt xe / RO",
                f"{actual_ro:,.0f}",
                (
                    f"Target: {target_ro:,.0f} | "
                    f"Đạt: {ro_rate:.0%}"
                ),
            )
        else:
            render_kpi_card(
                "Lượt xe / RO",
                f"{actual_ro:,.0f}",
            )

    with column_2:
        if target_available:
            render_kpi_card(
                "Tổng doanh thu",
                fmt_m(actual_revenue),
                (
                    f"Target: "
                    f"{target_revenue / 1_000_000:,.0f}M | "
                    f"Đạt: {revenue_rate:.0%}"
                ),
            )
        else:
            render_kpi_card(
                "Tổng doanh thu",
                fmt_m(actual_revenue),
            )

    with column_3:
        render_kpi_card(
            "Tổng tiền sau thuế",
            fmt_m(total_after_tax),
        )

    with column_4:
        render_kpi_card(
            "Doanh thu / RO",
            fmt_m(revenue_per_ro),
        )

    st.markdown(
        "<div style='height:18px;'></div>",
        unsafe_allow_html=True,
    )

# ============================================================
# KẾ HOẠCH MỤC TIÊU TƯƠNG TÁC
# GIỮ NGUYÊN HÌNH DẠNG CARD CŨ
# ============================================================

def render_interactive_target_planner(
    actual_ro,
    target_ro,
    actual_revenue,
    target_revenue,
    working_day_info,
    calculate_target_plan_function,
):
    remaining_days = working_day_info["remaining_working_days"]
    cutoff_date = working_day_info["data_cutoff_date"]
    total_working_days = working_day_info["total_working_days"]

    current_ro_percentage = (
        actual_ro / target_ro * 100
        if target_ro
        else 0
    )

    current_revenue_percentage = (
        actual_revenue / target_revenue * 100
        if target_revenue
        else 0
    )

    current_ro_default = min(
        100,
        max(0, round(current_ro_percentage)),
    )

    current_revenue_default = min(
        100,
        max(0, round(current_revenue_percentage)),
    )

    period_key = (
        f"{cutoff_date.isoformat()}_"
        f"{actual_ro}_"
        f"{actual_revenue}_"
        f"{target_ro}_"
        f"{target_revenue}"
    )

    if st.session_state.get("planner_period_key") != period_key:
        st.session_state["planner_period_key"] = period_key
        st.session_state["desired_ro_percentage"] = current_ro_default
        st.session_state["desired_revenue_percentage"] = (
            current_revenue_default
        )
        st.session_state["ro_slider_nonce"] = (
            st.session_state.get("ro_slider_nonce", 0) + 1
        )
        st.session_state["revenue_slider_nonce"] = (
            st.session_state.get("revenue_slider_nonce", 0) + 1
        )

    if "desired_ro_percentage" not in st.session_state:
        st.session_state["desired_ro_percentage"] = current_ro_default

    if "desired_revenue_percentage" not in st.session_state:
        st.session_state["desired_revenue_percentage"] = (
            current_revenue_default
        )

    if "ro_slider_nonce" not in st.session_state:
        st.session_state["ro_slider_nonce"] = 0

    if "revenue_slider_nonce" not in st.session_state:
        st.session_state["revenue_slider_nonce"] = 0

    st.markdown(
        "## 1. Lượt xe và Doanh thu: Thực hiện / Chỉ tiêu"
    )

    st.caption(
        f"Dữ liệu cập nhật đến "
        f"{cutoff_date.strftime('%d/%m/%Y')} · "
        f"Tháng có {total_working_days} ngày làm việc "
        f"sau khi loại Chủ nhật · "
        f"Còn {remaining_days} ngày làm việc."
    )

    card_left, card_right = st.columns(2)

    with card_left:
        with st.container(key="ro_target_card"):
            st.markdown(
                '<div class="progress-title">Lượt xe / RO</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="progress-sub">'
                f'<b>Thực hiện:</b> {actual_ro:,.0f} / '
                f'<b>Chỉ tiêu:</b> {target_ro:,.0f}'
                '</div>',
                unsafe_allow_html=True,
            )

            ro_component_value = carpla_slider(
                value=int(
                    st.session_state["desired_ro_percentage"]
                ),
                min_value=0,
                max_value=100,
                step=1,
                key=(
                    "desired_ro_percentage_component_"
                    f'{st.session_state["ro_slider_nonce"]}'
                ),
            )

            if (
                ro_component_value
                != st.session_state["desired_ro_percentage"]
            ):
                st.session_state["desired_ro_percentage"] = (
                    int(ro_component_value)
                )

            desired_ro_percentage = int(
                st.session_state["desired_ro_percentage"]
            )

    with card_right:
        with st.container(key="revenue_target_card"):
            st.markdown(
                '<div class="progress-title">'
                'Tổng Doanh thu'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="progress-sub">'
                f'<b>Thực hiện:</b> '
                f'{fmt_m(actual_revenue)} / '
                f'<b>Chỉ tiêu:</b> '
                f'{fmt_m(target_revenue)}'
                '</div>',
                unsafe_allow_html=True,
            )

            revenue_component_value = carpla_slider(
                value=int(
                    st.session_state[
                        "desired_revenue_percentage"
                    ]
                ),
                min_value=0,
                max_value=100,
                step=1,
                key=(
                    "desired_revenue_percentage_component_"
                    f'{st.session_state["revenue_slider_nonce"]}'
                ),
            )

            if (
                revenue_component_value
                != st.session_state["desired_revenue_percentage"]
            ):
                st.session_state[
                    "desired_revenue_percentage"
                ] = int(revenue_component_value)

            desired_revenue_percentage = int(
                st.session_state[
                    "desired_revenue_percentage"
                ]
            )

    ro_plan = calculate_target_plan_function(
        actual_value=actual_ro,
        monthly_target=target_ro,
        desired_percentage=desired_ro_percentage,
        remaining_working_days=remaining_days,
    )

    revenue_plan = calculate_target_plan_function(
        actual_value=actual_revenue,
        monthly_target=target_revenue,
        desired_percentage=desired_revenue_percentage,
        remaining_working_days=remaining_days,
    )

    desired_ro = math.ceil(ro_plan["desired_value"])
    remaining_ro = math.ceil(ro_plan["remaining_required"])
    average_ro = math.ceil(ro_plan["average_required"])

    desired_revenue = revenue_plan["desired_value"]
    remaining_revenue = revenue_plan["remaining_required"]
    average_revenue = revenue_plan["average_required"]

    result_left, result_right = st.columns(2)

    # ========================================================
    # KẾT QUẢ LƯỢT XE
    # Chỉ hiện khi người dùng kéo khỏi mức hiện tại
    # ========================================================

    with result_left:
        is_current_ro_level = (
            desired_ro_percentage == current_ro_default
        )

        if not is_current_ro_level:
            if ro_plan["already_achieved"]:
                st.success(
                    f"Đã đạt mức **{desired_ro_percentage}%** chỉ tiêu, "
                    f"tương đương **{desired_ro:,.0f} lượt xe**."
                )
            elif remaining_days > 0:
                st.info(
                    f"Để đạt **{desired_ro_percentage}%** chỉ tiêu, "
                    f"cần thêm **{remaining_ro:,.0f} lượt xe**. "
                    f"Bình quân cần **{average_ro:,.0f} lượt xe/ngày** "
                    f"trong **{remaining_days} ngày làm việc** còn lại."
                )
            else:
                st.warning(
                    "Không còn ngày làm việc trong tháng."
                )

            if st.button(
                "↺ Về mức hiện tại",
                key="reset_ro_target",
                use_container_width=True,
            ):
                st.session_state["desired_ro_percentage"] = (
                    current_ro_default
                )
                st.session_state["ro_slider_nonce"] += 1
                st.rerun()

    # ========================================================
    # KẾT QUẢ DOANH THU
    # Chỉ hiện khi người dùng kéo khỏi mức hiện tại
    # ========================================================

    with result_right:
        is_current_revenue_level = (
            desired_revenue_percentage
            == current_revenue_default
        )

        if not is_current_revenue_level:
            if revenue_plan["already_achieved"]:
                st.success(
                    f"Đã đạt mức "
                    f"**{desired_revenue_percentage}%** chỉ tiêu, "
                    f"tương đương **{fmt_m(desired_revenue)}**."
                )
            elif remaining_days > 0:
                st.info(
                    f"Để đạt "
                    f"**{desired_revenue_percentage}%** chỉ tiêu, "
                    f"cần thêm **{fmt_m(remaining_revenue)}**. "
                    f"Bình quân cần "
                    f"**{fmt_m(average_revenue)}/ngày** "
                    f"trong **{remaining_days} ngày làm việc** còn lại."
                )
            else:
                st.warning(
                    "Không còn ngày làm việc trong tháng."
                )

            if st.button(
                "↺ Về mức hiện tại",
                key="reset_revenue_target",
                use_container_width=True,
            ):
                st.session_state[
                    "desired_revenue_percentage"
                ] = current_revenue_default
                st.session_state["revenue_slider_nonce"] += 1
                st.rerun()

    return {
        "current_ro_percentage": current_ro_percentage,
        "current_revenue_percentage": current_revenue_percentage,
        "desired_ro_percentage": desired_ro_percentage,
        "desired_revenue_percentage": desired_revenue_percentage,
        "ro_plan": ro_plan,
        "revenue_plan": revenue_plan,
    }
