import os

# 원본 파일 경로와 결과를 저장할 파일 경로 설정
input_filepath = "results/exp06_main.txt"
output_filepath = "results/exp06_main_000.txt"

try:
    # 1단계: 첫 번째 데이터 행을 찾아 평행 이동의 기준이 될 오프셋(offset) 값을 구하기
    x_offset, y_offset, z_offset = 0.0, 0.0, 0.0
    first_data_line_found = False

    with open(input_filepath, "r") as f:
        for line in f:
            # 주석(#)이나 빈 줄은 건너뛰기
            if line.strip().startswith("#") or not line.strip():
                continue

            # 파일에서 가장 처음 만나는 데이터 라인
            parts = line.strip().split()
            try:
                # 2, 3, 4번째 열의 값을 오프셋으로 저장
                x_offset = float(parts[1])
                y_offset = float(parts[2])
                z_offset = float(parts[3])
                first_data_line_found = True
                break  # 첫 번째 데이터 라인을 찾았으므로 루프 중단
            except (ValueError, IndexError):
                print(f"경고: 첫 데이터 라인 분석 중 오류 발생. 다음 라인으로 넘어갑니다: {line.strip()}")
                continue

    # 데이터 라인을 찾았는지 확인
    if not first_data_line_found:
        print("오류: 파일에서 유효한 데이터 라인을 찾을 수 없습니다.")
    else:
        print("=" * 40)
        print("평행 이동의 기준이 될 첫 행의 좌표값:")
        print(f"  - X 오프셋: {x_offset}")
        print(f"  - Y 오프셋: {y_offset}")
        print(f"  - Z 오프셋: {z_offset}")
        print("=" * 40)

        # 2단계: 오프셋을 적용하여 모든 좌표를 평행 이동시키고 새 파일에 저장

        # 결과를 저장할 디렉터리가 없으면 생성
        output_dir = os.path.dirname(output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_filepath, "r") as infile, open(output_filepath, "w") as outfile:
            for line in infile:
                # 주석(#)이나 빈 줄은 그대로 복사
                if line.strip().startswith("#") or not line.strip():
                    outfile.write(line)
                    continue

                parts = line.strip().split()
                try:
                    # 타임스탬프와 5번째 이후의 데이터는 그대로 유지
                    timestamp = parts[0]
                    remaining_parts = parts[4:]

                    # 2, 3, 4번째 열(x, y, z)의 값을 오프셋만큼 빼서 평행 이동
                    new_x = float(parts[1]) - x_offset
                    new_y = float(parts[2]) - y_offset
                    new_z = float(parts[3]) - z_offset

                    # 새로운 데이터 라인을 조합
                    # 소수점 정밀도를 유지하기 위해 f-string 포맷팅 사용
                    new_line_parts = [timestamp, f"{new_x:.10f}", f"{new_y:.10f}", f"{new_z:.10f}"] + remaining_parts
                    outfile.write(" ".join(new_line_parts) + "\n")

                except (ValueError, IndexError):
                    # 혹시 모를 형식 오류가 있는 라인은 원본 그대로 복사
                    outfile.write(line)
                    continue

        print(f"\n성공적으로 평행 이동 완료! 결과가 '{output_filepath}' 파일에 저장되었습니다.")

except FileNotFoundError:
    print(f"오류: '{input_filepath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
