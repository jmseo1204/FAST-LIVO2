import os


def get_start_and_end_timestamps(filepath):
    """
    파일을 읽어 첫 번째와 마지막 데이터 행의 타임스탬프를 찾아 반환합니다.

    Args:
        filepath (str): 읽어올 파일의 경로

    Returns:
        tuple or None: (start_ts, end_ts)를 찾으면 float 튜플로 반환하고,
                       데이터가 없거나 오류 발생 시 None을 반환합니다.
    """
    first_ts = None
    last_ts = None
    try:
        with open(filepath, "r") as f:
            for line in f:
                # 주석(#)이거나 빈 줄은 건너뛰기
                if line.strip().startswith("#") or not line.strip():
                    continue

                parts = line.strip().split()
                if not parts:
                    continue

                try:
                    current_ts = float(parts[0])
                    if first_ts is None:
                        first_ts = current_ts
                    last_ts = current_ts  # 마지막으로 유효한 타임스탬프로 계속 덮어씀
                except (ValueError, IndexError):
                    print(f"경고: 숫자 변환 불가 라인 건너뜀: {line.strip()}")
                    continue

        if first_ts is None:
            print(f"오류: '{filepath}' 파일에서 유효한 데이터를 찾을 수 없습니다.")
            return None

        return first_ts, last_ts

    except FileNotFoundError:
        print(f"오류: '{filepath}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"파일 처리 중 오류 발생: {e}")
        return None


# --- 메인 코드 실행 부분 ---
if __name__ == "__main__":
    # 파일 경로 설정
    gt_filepath = "results/exp06_gt_inverted.txt"
    x_filepath = "results/exp06_4cam_no_calib.txt"
    output_filepath = "results/exp06_4cam_no_calib_time.txt"

    try:
        # 1. 각 파일의 시작과 끝 타임스탬프 가져오기
        gt_start_ts, gt_end_ts = get_start_and_end_timestamps(gt_filepath)
        x_start_ts, x_end_ts = get_start_and_end_timestamps(x_filepath)

        if any(ts is None for ts in [gt_start_ts, gt_end_ts, x_start_ts, x_end_ts]):
            raise ValueError("하나 이상의 파일에서 시작/끝 타임스탬프를 읽어오는 데 실패했습니다.")

        # 2. 스케일(scale)과 바이어스(bias) 계산
        gt_duration = gt_end_ts - gt_start_ts
        x_duration = x_end_ts - x_start_ts

        # 엣지 케이스 처리: X 파일에 데이터가 하나만 있어 duration이 0인 경우
        if x_duration == 0:
            scale = 1.0
            bias = gt_start_ts - x_start_ts
        else:
            scale = gt_duration / x_duration
            bias = gt_start_ts - (x_start_ts * scale)

        print("=" * 40)
        print("타임스탬프 정보:")
        print(f"  - GT 범위:  {gt_start_ts:.6f} -> {gt_end_ts:.6f} (길이: {gt_duration:.6f})")
        print(f"  - X 원본 범위: {x_start_ts:.6f} -> {x_end_ts:.6f} (길이: {x_duration:.6f})")
        print("\n계산된 변환 파라미터:")
        print(f"  - 스케일 (Scale): {scale:.10f}")
        print(f"  - 바이어스 (Bias): {bias:.10f}")
        print("=" * 40)

        # 3. 변환을 적용하여 새로운 파일 생성
        output_dir = os.path.dirname(output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(x_filepath, "r") as infile, open(output_filepath, "w") as outfile:
            for line in infile:
                if line.strip().startswith("#") or not line.strip():
                    outfile.write(line)
                    continue

                parts = line.strip().split()
                try:
                    original_timestamp = float(parts[0])

                    # 스케일과 바이어스를 적용하여 새로운 타임스탬프 계산
                    new_timestamp = (original_timestamp * scale) + bias

                    parts[0] = f"{new_timestamp:.6f}"
                    outfile.write(" ".join(parts) + "\n")
                except (ValueError, IndexError):
                    outfile.write(line)
                    continue

        print(f"\n성공적으로 타임스탬프 스케일 및 평행 이동 완료!")
        print(f"결과가 '{output_filepath}' 파일에 저장되었습니다.")

        # 검증: 생성된 파일의 시작/끝 타임스탬프 확인
        print("\n--- 검증 ---")
        final_start, final_end = get_start_and_end_timestamps(output_filepath)
        if final_start is not None:
            print(f"생성된 파일의 시작 타임스탬프: {final_start:.6f} (GT 시작: {gt_start_ts:.6f})")
            print(f"생성된 파일의 끝 타임스탬프:   {final_end:.6f} (GT 끝:   {gt_end_ts:.6f})")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
