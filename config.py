from pathlib import Path

# ============================================================
# ĐƯỜNG DẪN GỐC
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_FILE = BASE_DIR / "carpla_services_logo_hd.png"
WORKSHOP_MANAGER_FILE = BASE_DIR / "workshop_manager.xlsx"


# ============================================================
# API PRODUCTION
# ============================================================

API_URL = (
    "https://synerlynk.carpla.vn/"
    "api/report.repair.order.api/"
    "method_not_record/get_repair_order_report"
)

API_CACHE_TTL_SECONDS = 1800
API_TIMEOUT_SECONDS = 120

# Mỗi request tối đa 1 tháng theo Ngày quyết toán.
# Khi xem 1 tháng dashboard: lấy tháng cần xem + 2 tháng trước.
API_BUFFER_MONTHS = 2


# ============================================================
# 7 CHI NHÁNH TOÀN HỆ THỐNG
# ============================================================

BRANCH_ORDER = ['Hà Nội', 'Tây Bắc Bộ', 'Đông Bắc Bộ', 'TP. HCM', 'Cần Thơ', 'Nghệ An', 'Đà Nẵng']


# ============================================================
# MAPPING CHI NHÁNH → XƯỞNG → BRANCH CODES API
# ============================================================
# Một xưởng có thể có nhiều mã lịch sử.
# Khi chọn xưởng, API sẽ nhận toàn bộ mã tương ứng.

BRANCH_WORKSHOP_CODES = {'Hà Nội': {'Giải Phóng': ['CSHN.GP'], 'Hà Nam': ['CS.HN'], 'Hà Đông': ['CSHN.HD'], 'Hưng Yên': ['CSHN.HY'], 'Hải Dương': ['DBB.HD'], 'Long Biên': ['CSHN.LB'], 'Ninh Bình': ['DBB.NB'], 'Phạm Văn Đồng': ['CSHANOI']}, 'Tây Bắc Bộ': {'Hà Giang': ['TBB.HG'], 'Hòa Bình': ['CSHN.HB', 'TBB.HB'], 'Lai Châu': ['TBB.LAC'], 'Lào Cai': ['TBB.LC'], 'Phú Thọ': ['CS.TBB'], 'Sơn La': ['TBB.SL'], 'Tuyên Quang': ['TBB.TQ'], 'Vĩnh Phúc': ['CSHN.VP', 'TBB.VP'], 'Yên Bái': ['TBB.YB'], 'Điện Biên': ['TBB.DB']}, 'Đông Bắc Bộ': {'Bắc Giang': ['CSHN.BG', 'DBB.BG'], 'Bắc Kạn': ['DBB.BK'], 'Bắc Ninh': ['DBB.BN'], 'Cao Bằng': ['DBB.CB'], 'Hải Phòng': ['CSHN.HP', 'DBB.HP'], 'Lạng Sơn': ['CS.LS', 'DBB.LS'], 'Nam Đinh': ['DBB.ND'], 'Nam Định': ['CSHN.ND'], 'Quảng Ninh': ['CSHN.QN', 'DBB.QNI'], 'Thái Bình': ['DBB.TB'], 'Thái Nguyên': ['CSHN.TN', 'CS.DBB']}, 'TP. HCM': {'Bà Rịa': ['CSHCM.BR'], 'Bình Dương': ['HCM.BD'], 'Bình Phước': ['HCM.BP'], 'Bình Thuận': ['CS.BT'], 'Chế Lan Viên': ['CS.CLV'], 'Long An': ['CSHCM.LA'], 'Lâm Đồng (Đà Lạt)': ['CS.LDDL'], 'Phú Mỹ Hưng': ['CSHCM.PMH'], 'Thuận An': ['HCM.TA'], 'Tiền Giang': ['HCM.TG'], 'Tân Cảng': ['CSHCM.TC'], 'Tân Phú': ['CSHCM'], 'Tây Ninh': ['CS.TN'], 'Vũng Tàu': ['CSHCM.VT'], 'Đăk Nông': ['HCM.DNO'], 'Đồng Nai': ['HCM.DNA']}, 'Cần Thơ': {'Bạc Liêu': ['CT.BL'], 'Bến Tre': ['CT.BT'], 'Cà Mau': ['CT.CM'], 'Cái Răng': ['CSCANTHO'], 'Hưng Phú': ['CT.HP'], 'Hậu Giang': ['CT.HG'], 'Kiên Giang (Phú Quốc)': ['CT.KGPQ'], 'Kiên Giang (Rạch Giá)': ['CT.KGRG'], 'Long Xuyên': ['CT.LX'], 'Sóc Trăng': ['CT.ST'], 'Trà Vinh': ['CT.TV'], 'Vĩnh Long': ['CT.VL'], 'Đồng Tháp': ['CT.DT']}, 'Nghệ An': {'Diễn Châu': ['NADC'], 'Hà Tĩnh': ['CSNA.HT'], 'TH Nghi Sơn': ['CS.NA_NS'], 'Thanh Hóa': ['CSNA.TH'], 'Thành phố Vinh': ['CSNA']}, 'Đà Nẵng': {'Bình Định': ['CSDN.BD'], 'Gia Lai': ['CSDN.GL'], 'Huế': ['CSDN.H'], 'Khánh Hòa': ['DN.KHH'], 'Kon Tum': ['CSDN.KTU'], 'Nha Trang': ['CSDN.NT'], 'Ninh Thuận': ['CSDN.NTH'], 'Phú Yên': ['CSDN.PY'], 'Quảng Bình': ['CSDN.QB'], 'Quảng Nam': ['CSDN.QNA'], 'Quảng Ngãi': ['CSDN.QN'], 'Quảng Trị': ['CSDN.QT'], 'TSC': ['CSDN'], 'Đăk Lăk': ['DN.DLK'], 'Đăk Nông': ['DN.DNO']}}


# ============================================================
# MAPPING TÊN XƯỞNG API → TÊN HIỂN THỊ / CHI NHÁNH
# ============================================================

API_WORKSHOP_NAME_MAP = {'CHI NHÁNH NGHỆ AN - THÀNH PHỐ VINH': 'Thành phố Vinh', 'CHI NHÁNH CẦN THƠ - CÁI RĂNG': 'Cái Răng', 'CHI NHÁNH HỒ CHÍ MINH - TÂN PHÚ': 'Tân Phú', 'CHI NHÁNH HÀ NỘI - PVĐ': 'Phạm Văn Đồng', 'CN Hà Nội-Long Biên': 'Long Biên', 'CN Hà Nội-Giải Phóng': 'Giải Phóng', 'Geely and Lynk&Co Hải Phòng': 'Hải Phòng', 'Geely and Lynk&Co Quảng Ninh': 'Quảng Ninh', 'Geely and Lynk&Co Vĩnh Phúc': 'Vĩnh Phúc', 'Geely and Lynk&Co Thái Nguyên': 'Thái Nguyên', 'CN Nghệ An-Thanh Hóa': 'Thanh Hóa', 'CN Nghệ An-Hà Tĩnh': 'Hà Tĩnh', 'CN HCM-Phú Mỹ Hưng': 'Phú Mỹ Hưng', 'CN HCM-Vũng Tàu': 'Vũng Tàu', 'CHI NHÁNH ĐÀ NẴNG-TSC': 'TSC', 'CN Hà Nội-Hà Đông': 'Hà Đông', 'CN Hà Nội-Hòa Bình': 'Hòa Bình', 'CN Hà Nội-Nam Định': 'Nam Định', 'CN Hà Nội-Hưng Yên': 'Hưng Yên', 'ĐĐKD Bắc Giang': 'Bắc Giang', 'CN Đà Nẵng-Nha Trang': 'Nha Trang', 'CN Đà Nẵng-Quảng Ngãi': 'Quảng Ngãi', 'CN Đà Nẵng-Ninh Thuận': 'Ninh Thuận', 'CN HCM-Bà Rịa': 'Bà Rịa', 'CN HCM-Long An': 'Long An', 'CN Cần Thơ-Long Xuyên': 'Long Xuyên', 'CN Cần Thơ-Cà Mau': 'Cà Mau', 'CN Đông Bắc Bộ-Lạng Sơn': 'Lạng Sơn', 'CN Hà Nội- Hà Nam': 'Hà Nam', 'CN Đà Nẵng-Quảng Bình': 'Quảng Bình', 'CN Đà Nẵng-Quảng Trị': 'Quảng Trị', 'CN Đà Nẵng-Gia Lai': 'Gia Lai', 'CN HCM-Bình Thuận': 'Bình Thuận', 'CN Tây Bắc Bộ-Tuyên Quang': 'Tuyên Quang', 'CN Tây Bắc Bộ-Lào Cai': 'Lào Cai', 'CN Tây Bắc Bộ-Lai Châu': 'Lai Châu', 'CN Tây Bắc Bộ-Điện Biên': 'Điện Biên', 'CN Tây Bắc Bộ-Sơn La': 'Sơn La', 'CN Hà Nội-Hải Dương': 'Hải Dương', 'CN Hà Nội-Ninh Bình': 'Ninh Bình', 'CN Đà Nẵng-Quảng Nam': 'Quảng Nam', 'CN Đà Nẵng-Phú Yên': 'Phú Yên', 'CN HCM-Lâm Đồng (Đà Lạt)': 'Lâm Đồng (Đà Lạt)', 'CN Cần Thơ-Đồng Tháp': 'Đồng Tháp', 'CN Cần Thơ-Kiên Giang (Rạch Giá)': 'Kiên Giang (Rạch Giá)', 'CN Cần Thơ-Kiên Giang (Phú Quốc)': 'Kiên Giang (Phú Quốc)', 'CN Cần Thơ-Bến Tre': 'Bến Tre', 'CN Cần Thơ-Vĩnh Long': 'Vĩnh Long', 'CN Cần Thơ-Trà Vinh': 'Trà Vinh', 'CN Cần Thơ-Hậu Giang': 'Hậu Giang', 'CN Cần Thơ-Sóc Trăng': 'Sóc Trăng', 'CN Cần Thơ-Bạc Liêu': 'Bạc Liêu', 'CN HCM-Tân Cảng': 'Tân Cảng', 'CN HCM-Chế Lan Viên': 'Chế Lan Viên', 'CN HCM-Tây Ninh': 'Tây Ninh', 'CHI NHÁNH TÂY BẮC BỘ-PHÚ THỌ': 'Phú Thọ', 'CHI NHÁNH ĐÔNG BẮC BỘ-THÁI NGUYÊN': 'Thái Nguyên', 'CN Đông Bắc Bộ-Hải Phòng': 'Hải Phòng', 'CN Tây Bắc Bộ-Vĩnh Phúc': 'Vĩnh Phúc', 'CN Đông Bắc Bộ-Quảng Ninh': 'Quảng Ninh', 'CN Tây Bắc Bộ-Hòa Bình': 'Hòa Bình', 'CN Đông Bắc Bộ-Nam Đinh': 'Nam Đinh', 'CN Đông Bắc Bộ-Bắc Giang': 'Bắc Giang', 'CN NEW': 'Lạng Sơn', 'CN Đông Bắc Bộ-Thái Bình': 'Thái Bình', 'CN Đông Bắc Bộ-Bắc Ninh': 'Bắc Ninh', 'CN Đông Bắc Bộ-Cao Bằng': 'Cao Bằng', 'CN Đông Bắc Bộ-Bắc Kạn': 'Bắc Kạn', 'CN Tây Bắc Bộ-Hà Giang': 'Hà Giang', 'CN Tây Bắc Bộ-Yên Bái': 'Yên Bái', 'CN HCM-Bình Dương': 'Bình Dương', 'CN HCM-Bình Phước': 'Bình Phước', 'CN HCM-Đồng Nai': 'Đồng Nai', 'CN Đà Nẵng-Đăk Lăk': 'Đăk Lăk', 'CN Đà Nẵng-Đăk Nông': 'Đăk Nông', 'CN Đà Nẵng-Kon Tum': 'Kon Tum', 'CN Cần Thơ-Hưng Phú': 'Hưng Phú', 'CN HCM-Tiền Giang': 'Tiền Giang', 'CN Nghệ An-Diễn Châu': 'Diễn Châu', 'CN Nghệ An-TH Nghi Sơn': 'TH Nghi Sơn', 'CN HCM-Thuận An': 'Thuận An', 'CN Đà Nẵng-Khánh Hòa': 'Khánh Hòa', 'CN Đà Nẵng-Huế': 'Huế', 'CN Đà Nẵng-Bình Định': 'Bình Định', 'CN HCM-Đăk Nông': 'Đăk Nông'}

API_WORKSHOP_BRANCH_MAP = {'CHI NHÁNH NGHỆ AN - THÀNH PHỐ VINH': 'Nghệ An', 'CHI NHÁNH CẦN THƠ - CÁI RĂNG': 'Cần Thơ', 'CHI NHÁNH HỒ CHÍ MINH - TÂN PHÚ': 'TP. HCM', 'CHI NHÁNH HÀ NỘI - PVĐ': 'Hà Nội', 'CN Hà Nội-Long Biên': 'Hà Nội', 'CN Hà Nội-Giải Phóng': 'Hà Nội', 'Geely and Lynk&Co Hải Phòng': 'Đông Bắc Bộ', 'Geely and Lynk&Co Quảng Ninh': 'Đông Bắc Bộ', 'Geely and Lynk&Co Vĩnh Phúc': 'Tây Bắc Bộ', 'Geely and Lynk&Co Thái Nguyên': 'Đông Bắc Bộ', 'CN Nghệ An-Thanh Hóa': 'Nghệ An', 'CN Nghệ An-Hà Tĩnh': 'Nghệ An', 'CN HCM-Phú Mỹ Hưng': 'TP. HCM', 'CN HCM-Vũng Tàu': 'TP. HCM', 'CHI NHÁNH ĐÀ NẴNG-TSC': 'Đà Nẵng', 'CN Hà Nội-Hà Đông': 'Hà Nội', 'CN Hà Nội-Hòa Bình': 'Tây Bắc Bộ', 'CN Hà Nội-Nam Định': 'Đông Bắc Bộ', 'CN Hà Nội-Hưng Yên': 'Hà Nội', 'ĐĐKD Bắc Giang': 'Đông Bắc Bộ', 'CN Đà Nẵng-Nha Trang': 'Đà Nẵng', 'CN Đà Nẵng-Quảng Ngãi': 'Đà Nẵng', 'CN Đà Nẵng-Ninh Thuận': 'Đà Nẵng', 'CN HCM-Bà Rịa': 'TP. HCM', 'CN HCM-Long An': 'TP. HCM', 'CN Cần Thơ-Long Xuyên': 'Cần Thơ', 'CN Cần Thơ-Cà Mau': 'Cần Thơ', 'CN Đông Bắc Bộ-Lạng Sơn': 'Đông Bắc Bộ', 'CN Hà Nội- Hà Nam': 'Hà Nội', 'CN Đà Nẵng-Quảng Bình': 'Đà Nẵng', 'CN Đà Nẵng-Quảng Trị': 'Đà Nẵng', 'CN Đà Nẵng-Gia Lai': 'Đà Nẵng', 'CN HCM-Bình Thuận': 'TP. HCM', 'CN Tây Bắc Bộ-Tuyên Quang': 'Tây Bắc Bộ', 'CN Tây Bắc Bộ-Lào Cai': 'Tây Bắc Bộ', 'CN Tây Bắc Bộ-Lai Châu': 'Tây Bắc Bộ', 'CN Tây Bắc Bộ-Điện Biên': 'Tây Bắc Bộ', 'CN Tây Bắc Bộ-Sơn La': 'Tây Bắc Bộ', 'CN Hà Nội-Hải Dương': 'Hà Nội', 'CN Hà Nội-Ninh Bình': 'Hà Nội', 'CN Đà Nẵng-Quảng Nam': 'Đà Nẵng', 'CN Đà Nẵng-Phú Yên': 'Đà Nẵng', 'CN HCM-Lâm Đồng (Đà Lạt)': 'TP. HCM', 'CN Cần Thơ-Đồng Tháp': 'Cần Thơ', 'CN Cần Thơ-Kiên Giang (Rạch Giá)': 'Cần Thơ', 'CN Cần Thơ-Kiên Giang (Phú Quốc)': 'Cần Thơ', 'CN Cần Thơ-Bến Tre': 'Cần Thơ', 'CN Cần Thơ-Vĩnh Long': 'Cần Thơ', 'CN Cần Thơ-Trà Vinh': 'Cần Thơ', 'CN Cần Thơ-Hậu Giang': 'Cần Thơ', 'CN Cần Thơ-Sóc Trăng': 'Cần Thơ', 'CN Cần Thơ-Bạc Liêu': 'Cần Thơ', 'CN HCM-Tân Cảng': 'TP. HCM', 'CN HCM-Chế Lan Viên': 'TP. HCM', 'CN HCM-Tây Ninh': 'TP. HCM', 'CHI NHÁNH TÂY BẮC BỘ-PHÚ THỌ': 'Tây Bắc Bộ', 'CHI NHÁNH ĐÔNG BẮC BỘ-THÁI NGUYÊN': 'Đông Bắc Bộ', 'CN Đông Bắc Bộ-Hải Phòng': 'Đông Bắc Bộ', 'CN Tây Bắc Bộ-Vĩnh Phúc': 'Tây Bắc Bộ', 'CN Đông Bắc Bộ-Quảng Ninh': 'Đông Bắc Bộ', 'CN Tây Bắc Bộ-Hòa Bình': 'Tây Bắc Bộ', 'CN Đông Bắc Bộ-Nam Đinh': 'Đông Bắc Bộ', 'CN Đông Bắc Bộ-Bắc Giang': 'Đông Bắc Bộ', 'CN NEW': 'Đông Bắc Bộ', 'CN Đông Bắc Bộ-Thái Bình': 'Đông Bắc Bộ', 'CN Đông Bắc Bộ-Bắc Ninh': 'Đông Bắc Bộ', 'CN Đông Bắc Bộ-Cao Bằng': 'Đông Bắc Bộ', 'CN Đông Bắc Bộ-Bắc Kạn': 'Đông Bắc Bộ', 'CN Tây Bắc Bộ-Hà Giang': 'Tây Bắc Bộ', 'CN Tây Bắc Bộ-Yên Bái': 'Tây Bắc Bộ', 'CN HCM-Bình Dương': 'TP. HCM', 'CN HCM-Bình Phước': 'TP. HCM', 'CN HCM-Đồng Nai': 'TP. HCM', 'CN Đà Nẵng-Đăk Lăk': 'Đà Nẵng', 'CN Đà Nẵng-Đăk Nông': 'Đà Nẵng', 'CN Đà Nẵng-Kon Tum': 'Đà Nẵng', 'CN Cần Thơ-Hưng Phú': 'Cần Thơ', 'CN HCM-Tiền Giang': 'TP. HCM', 'CN Nghệ An-Diễn Châu': 'Nghệ An', 'CN Nghệ An-TH Nghi Sơn': 'Nghệ An', 'CN HCM-Thuận An': 'TP. HCM', 'CN Đà Nẵng-Khánh Hòa': 'Đà Nẵng', 'CN Đà Nẵng-Huế': 'Đà Nẵng', 'CN Đà Nẵng-Bình Định': 'Đà Nẵng', 'CN HCM-Đăk Nông': 'TP. HCM'}


# ============================================================
# TARGET - CHỈ ÁP DỤNG THÁNG 7/2026
# ============================================================

TARGETS = {
    ("Hà Nội", "Phạm Văn Đồng", 2026, 7): {
        "ro": 714,
        "revenue": 1_429_000_000,
    },
    ("Hà Nội", "Long Biên", 2026, 7): {
        "ro": 643,
        "revenue": 1_287_000_000,
    },
    ("Hà Nội", "Giải Phóng", 2026, 7): {
        "ro": 527,
        "revenue": 1_055_000_000,
    },
    ("Hà Nội", "Hà Đông", 2026, 7): {
        "ro": 427,
        "revenue": 855_000_000,
    },
    ("Hà Nội", "Hưng Yên", 2026, 7): {
        "ro": 216,
        "revenue": 432_000_000,
    },
    ("Hà Nội", "Hà Nam", 2026, 7): {
        "ro": 154,
        "revenue": 309_000_000,
    },
    ("Hà Nội", "Hải Dương", 2026, 7): {
        "ro": 287,
        "revenue": 575_000_000,
    },
    ("Hà Nội", "Ninh Bình", 2026, 7): {
        "ro": 74,
        "revenue": 148_000_000,
    },
}


# ============================================================
# PHÂN NHÓM QUAN HỆ THƯƠNG HIỆU
# ============================================================

TASCO_OFFICIAL_BRANDS = [
    "GEELY",
    "LYNK & CO",
    "ZEEKR",
    "LOTUS",
]

PARTNER_BRANDS = [
    "HYUNDAI",
    "TOYOTA",
    "KIA",
    "MAZDA",
    "MITSUBISHI",
    "FORD",
    "HONDA",
    "VOLVO",
    "MERCEDES-BENZ",
    "BMW",
    "AUDI",
    "LEXUS",
    "PORSCHE",
    "LAND ROVER",
    "JAGUAR",
    "PEUGEOT",
    "VOLKSWAGEN",
    "SUZUKI",
    "MG",
    "VINFAST",
    "OMODA & JAECOO",
    "WULING",
]


# ============================================================
# PHÂN NHÓM PHÂN KHÚC XE
# ============================================================

LUXURY_BRANDS = [
    "AUDI",
    "BMW",
    "JAGUAR",
    "LAND ROVER",
    "LEXUS",
    "LOTUS",
    "MERCEDES-BENZ",
    "PORSCHE",
    "VOLVO",
    "ZEEKR",
]

MASS_MARKET_BRANDS = [
    "FORD",
    "GEELY",
    "HONDA",
    "HYUNDAI",
    "KIA",
    "LYNK & CO",
    "MAZDA",
    "MG",
    "MITSUBISHI",
    "OMODA & JAECOO",
    "PEUGEOT",
    "SUZUKI",
    "TOYOTA",
    "VINFAST",
    "VOLKSWAGEN",
    "WULING",
]


# ============================================================
# GIỮ BIẾN CŨ ĐỂ TƯƠNG THÍCH
# ============================================================

WORKING_DAYS = 27
