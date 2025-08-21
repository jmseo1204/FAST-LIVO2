import numpy as np
import os

# 원본 파일 경로와 결과를 저장할 파일 경로 설정
input_filepath = "results/exp06_main"
output_filepath = input_filepath + "_centered.txt"
input_filepath = input_filepath + ".txt"

try:
    # 1단계: 모든 x, y, z 좌표를 읽어 각 축의 평균 계산
    x_coords, y_coords, z_coords = [], [], []

    with open(input_filepath, "r") as f:
        for line in f:
            # 주석(#)이나 빈 줄은 건너뛰기
            if line.strip().startswith("#") or not line.strip():
                continue

            parts = line.strip().split()
            try:
                # 2, 3, 4번째 열(인덱스 1, 2, 3)의 값을 float으로 변환하여 리스트에 추가
                x_coords.append(float(parts[1]))
                y_coords.append(float(parts[2]))
                z_coords.append(float(parts[3]))
            except (ValueError, IndexError):
                print(f"경고: 숫자 변환에 실패했거나 열이 부족한 라인을 건너뜁니다: {line.strip()}")
                continue

    # 리스트가 비어있지 않다면 평균 계산
    if not x_coords:
        print("오류: 파일에서 좌표 데이터를 찾을 수 없습니다.")
    else:
        # 각 축의 평균 계산
        mean_x = np.mean(x_coords)
        mean_y = np.mean(y_coords)
        mean_z = np.mean(z_coords)

        print("=" * 30)
        print("계산된 좌표별 평균값:")
        print(f"  - X축 평균: {mean_x}")
        print(f"  - Y축 평균: {mean_y}")
        print(f"  - Z축 평균: {mean_z}")
        print("=" * 30)

        # 2단계: 각 좌표에서 평균을 빼서 평행 이동시키고 새 파일에 저장

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
                    # 첫 번째 열(timestamp)과 5번째 이후 열들은 그대로 유지
                    timestamp = parts[0]
                    remaining_parts = parts[4:]

                    # 2, 3, 4번째 열의 값을 평행 이동
                    new_x = float(parts[1]) - mean_x
                    new_y = float(parts[2]) - mean_y
                    new_z = float(parts[3]) - mean_z

                    # 새로운 데이터 라인 생성
                    # 소수점 정밀도를 유지하기 위해 f-string 포맷팅 사용
                    new_line_parts = [timestamp, f"{new_x:.10f}", f"{new_y:.10f}", f"{new_z:.10f}"] + remaining_parts
                    outfile.write(" ".join(new_line_parts) + "\n")

                except (ValueError, IndexError):
                    # 원본 파일에 문제가 있는 라인이 있다면 그대로 복사
                    outfile.write(line)
                    continue

        print(f"\n성공적으로 평행 이동 완료! 결과가 '{output_filepath}' 파일에 저장되었습니다.")

except FileNotFoundError:
    print(f"오류: '{input_filepath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
