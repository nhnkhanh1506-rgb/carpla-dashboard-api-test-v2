# ============================================================
# progress_config.py
# CẤU HÌNH GOOGLE SHEET CHO BẢNG TIẾN ĐỘ SỬA CHỮA
# ============================================================

PROGRESS_SHEETS = {
    "Đà Nẵng": {
        "spreadsheet_id": "14PN4MuURy3pSKsvG2iy7c9EnCEKPgc4EpjjwIUww52A",
        "sheet_candidates": [
            "CN-ĐÀ NẴNG",
            "CN - ĐÀ NẴNG",
            "CN ĐÀ NẴNG",
        ],
    },
    "TP. HCM": {
        "spreadsheet_id": "1p7qxvtjtZveG4HWjTLV25h4d6AWxC42Bp5ECE74AhdE",
        "sheet_candidates": [
            "HCM",
            "CN-TP. HCM",
            "CN - TP. HCM",
            "CN TP. HCM",
            "CN-TP.HCM",
            "CN TP.HCM",
            "CN-TP HCM",
            "CN TP HCM",
            "CN-HCM",
            "CN HCM",
            "CN-HỒ CHÍ MINH",
            "CN - HỒ CHÍ MINH",
            "CN HỒ CHÍ MINH",
            "CN-TP.HỒ CHÍ MINH",
            "CN-TP HỒ CHÍ MINH",
            "CN TP HỒ CHÍ MINH",
        ],
    },
    "Cần Thơ": {
        "spreadsheet_id": "1Pce8RB2nn1dZUNVRsxVGmLd_tK01KnB4bLTaWqKU990",
        "sheet_candidates": [
            "CN-CẦN THƠ",
            "CN - CẦN THƠ",
            "CN CẦN THƠ",
        ],
    },
    "Hà Nội": {
        "spreadsheet_id": "1_i0MiDH8rVcQRSh0bAEKpablHiqk8f8Ua1HEoteJ-34",
        "sheet_candidates": [
            "CN-HÀ NỘI",
            "CN - HÀ NỘI",
            "CN HÀ NỘI",
        ],
    },
    "Tây Bắc Bộ": {
        "spreadsheet_id": "1rE7wLzkzsTyyIPAEpTY6yXyPEJVD9yfc0-lTWRVJdU8",
        "sheet_candidates": [
            "CN-TÂY BẮC BỘ",
            "CN - TÂY BẮC BỘ",
            "CN TÂY BẮC BỘ",
            "CN-TÂY BẮC",
        ],
    },
    "Đông Bắc Bộ": {
        "spreadsheet_id": "1_YhbVakB9d8jPObiXFXeruYra9PSH0SqIxmhQBiz2RA",
        "sheet_candidates": [
            "CN-ĐÔNG BẮC BỘ",
            "CN - ĐÔNG BẮC BỘ",
            "CN ĐÔNG BẮC BỘ",
            "CN-ĐÔNG BẮC",
        ],
    },
    "Nghệ An": {
        "spreadsheet_id": "1IF2ypCkDOtgweEujBecuv_ZCm6x6O1TFIGjGaK0hm3A",
        "sheet_candidates": [
            "CN-NGHỆ AN",
            "CN - NGHỆ AN",
            "CN NGHỆ AN",
        ],
    },
}

PROGRESS_CACHE_SECONDS = 60

# Cột tối thiểu dùng để nhận diện đúng tab raw.
PROGRESS_EXPECTED_COLUMNS = {
    "Số",
    "Công đoạn",
    "Trạng thái sửa chữa",
    "Trạng thái giao xe",
    "Xưởng dịch vụ",
}
