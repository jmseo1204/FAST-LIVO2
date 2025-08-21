import os

# 원본 파일 경로와 저장될 파일 경로 설정
input_filepath = "results/exp06_gt.txt"
output_filepath = "results/exp06_gt_inverted.txt"

try:
    # 결과를 저장할 디렉터리가 없으면 생성
    output_dir = os.path.dirname(output_filepath)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 파일을 읽고 쓰기 모드로 열기
    with open(input_filepath, "r") as infile, open(output_filepath, "w") as outfile:
        # 파일의 모든 라인을 순회
        for line in infile:
            # 주석(#)으로 시작하는 라인은 그대로 복사
            if line.strip().startswith("#"):
                outfile.write(line)
                continue

            # 공백을 기준으로 데이터를 분리
            parts = line.strip().split()

            # 데이터가 비어있는 라인은 건너뛰기
            if not parts:
                continue

            # 첫 번째 열(timestamp)은 그대로 유지

            # 나머지 열들의 부호를 반전
            inverted_values = []
            for i, value_str in enumerate(parts):
                try:
                    if i == 0 or i == 2:
                        inverted_value = float(value_str)
                    else:
                        inverted_value = -float(value_str)
                    # 문자열을 float으로 변환하여 부호 반전
                    # inverted_value = -float(value_str)
                    inverted_values.append(str(inverted_value))
                except ValueError:
                    # 만약 숫자로 변환할 수 없는 값이 있다면 원래 값 유지
                    inverted_values.append(value_str)

            # 새로운 라인을 생성하여 파일에 쓰기
            new_line = " ".join(inverted_values) + "\n"
            outfile.write(new_line)

    print(f"성공적으로 변환 완료! 결과가 '{output_filepath}' 파일에 저장되었습니다.")

except FileNotFoundError:
    print(f"오류: '{input_filepath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
