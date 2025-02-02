import os
import glob
import csv

# Thư mục chứa file eGeMAPS (định dạng ARFF-style CSV của openSMILE)
INPUT_CSV_DIR = r"C:\Users\Admin\PycharmProjects\PythonProject\cremad_egemaps"

# Thư mục lưu file CSV đã chuyển đổi (chỉ giữ đặc trưng, bỏ name & class)
OUTPUT_CSV_DIR = r"C:\Users\Admin\PycharmProjects\PythonProject\cremad_egemaps_clean"


def convert_arff_to_csv(in_arff: str, out_csv: str):
    """
    Đọc file ARFF-style do openSMILE xuất ra (e.g. eGeMAPS),
    trích xuất danh sách attribute (bỏ 'name' & 'class'),
    rồi parse phần @data, bỏ cột đầu & cột cuối (?), chỉ giữ các cột feature numeric.

    Output: CSV (header = cột attribute, rows = giá trị float).
    """
    with open(in_arff, 'r', encoding='utf-8') as f_in, open(out_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)

        attribute_names = []
        in_data_section = False

        for line in f_in:
            line = line.strip()
            if not line:
                continue  # Bỏ dòng trống

            # 1) Tìm và lưu attribute
            if line.lower().startswith('@attribute '):
                parts = line.split()
                if len(parts) >= 3:
                    attr_name = parts[1].strip()  # Lấy tên attribute

                    # Bỏ dấu nháy đơn nếu có
                    if attr_name.startswith("'") and attr_name.endswith("'"):
                        attr_name = attr_name[1:-1]

                    # Bỏ cột "name" và "class"
                    if attr_name.lower() not in ["name", "class"]:
                        attribute_names.append(attr_name)

            # 2) Khi gặp @data -> chuyển sang parse data
            elif line.lower().startswith('@data'):
                # Ghi header CSV: attribute_names
                writer.writerow(attribute_names)
                in_data_section = True
                continue

            # 3) Nếu đang ở phần data
            elif in_data_section:
                # Dòng dạng: "1001_IEO_DIS_MD,2.8e+01,9.0e-02,...,?"
                fields = line.split(',')
                if len(fields) < 3:
                    continue

                # cột[0] = name, cột[-1] = "?", cột[1..-2] = feature
                data_vals = fields[1:-1]

                # Chuyển sang float (nếu lỗi -> NaN)
                row_floats = []
                for val in data_vals:
                    val = val.strip()
                    try:
                        row_floats.append(float(val))
                    except ValueError:
                        row_floats.append(float('nan'))

                # Ghi CSV
                writer.writerow(row_floats)

    print(f"Converted: {in_arff} -> {out_csv}")


def batch_convert_arff_to_csv(
        input_dir: str = INPUT_CSV_DIR,
        output_dir: str = OUTPUT_CSV_DIR
):
    """
    Chuyển đổi toàn bộ file ARFF-style CSV từ openSMILE trong input_dir.
    Lưu vào output_dir với định dạng CSV chuẩn.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Tìm file *.csv
    arff_files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not arff_files:
        print(f"Không tìm thấy file ARFF-style CSV nào trong {input_dir}")
        return

    for arff_path in arff_files:
        # Đổi tên file output
        basename = os.path.basename(arff_path).replace("_egemaps", "_converted")
        out_csv = os.path.join(output_dir, basename)

        convert_arff_to_csv(arff_path, out_csv)


# ======================
# CHẠY CHUYỂN ĐỔI HẾT
# ======================
if __name__ == "__main__":
    batch_convert_arff_to_csv()
