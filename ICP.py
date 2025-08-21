import numpy as np
from scipy.spatial import cKDTree
import os


def find_rigid_transform(P, Q):
    """
    Kabsch 알고리즘을 사용하여 두 대응점 집합 P와 Q 사이의
    최적의 회전 행렬(R)과 평행 이동 벡터(t)를 찾습니다.
    Q ≈ R * P + t
    """
    centroid_P = np.mean(P, axis=0)
    centroid_Q = np.mean(Q, axis=0)

    P_centered = P - centroid_P
    Q_centered = Q - centroid_Q

    H = P_centered.T @ Q_centered

    U, S, Vt = np.linalg.svd(H)
    V = Vt.T

    R = V @ U.T

    # 반사 현상 보정
    if np.linalg.det(R) < 0:
        V[:, -1] *= -1
        R = V @ U.T

    t = centroid_Q - R @ centroid_P

    return R, t


def icp(source_points, target_points, max_iterations=100, tolerance=1e-6):
    """
    ICP 알고리즘을 사용하여 source_points를 target_points에 정합합니다.
    """
    transformed_points = np.copy(source_points)
    target_kdtree = cKDTree(target_points)
    prev_error = float("inf")

    final_R = np.eye(3)
    final_t = np.zeros(3)

    for i in range(max_iterations):
        distances, indices = target_kdtree.query(transformed_points)
        corresponding_points = target_points[indices]

        # 변환된 현재 source 포인트와 대응점 사이의 변환을 계산
        R, t = find_rigid_transform(transformed_points, corresponding_points)

        # 전체 변환을 누적
        final_R = R @ final_R
        final_t = R @ final_t + t

        # 원본 source 포인트에 누적된 변환을 적용
        transformed_points = (final_R @ source_points.T).T + final_t

        mean_error = np.mean(distances**2)
        if abs(prev_error - mean_error) < tolerance:
            print(f"오차가 임계값 이하로 수렴하여 {i+1}번째 반복에서 종료합니다.")
            break
        prev_error = mean_error

        print(f"반복 {i+1}/{max_iterations}, RMSD: {np.sqrt(mean_error):.6f}")

    return transformed_points


def load_full_data_from_file(filepath):
    """
    지정된 경로의 txt 파일에서 모든 데이터를 읽어 리스트로 반환합니다.
    """
    full_data = []
    with open(filepath, "r") as f:
        for line in f:
            if line.strip().startswith("#") or not line.strip():
                continue
            parts = line.strip().split()
            try:
                full_data.append([float(p) for p in parts])
            except (ValueError, IndexError):
                continue
    return full_data


# --- 메인 코드 실행 부분 ---
if __name__ == "__main__":
    # 파일 경로 설정
    gt_filepath = "results/exp06_gt_inverted.txt"
    x_filepath = "results/exp06_main.txt"
    output_filepath = "results/exp06_main_icp.txt"

    try:
        # 파일에서 전체 데이터 로드
        gt_data = load_full_data_from_file(gt_filepath)
        x_data = load_full_data_from_file(x_filepath)

        if not gt_data or not x_data:
            raise ValueError("하나 이상의 파일에서 데이터를 읽어오지 못했습니다.")

        # 좌표 데이터만 추출하여 Numpy 배열로 변환
        points_gt = np.array([row[1:4] for row in gt_data])
        points_x = np.array([row[1:4] for row in x_data])

        print(f"Target(GT) 포인트 수: {len(points_gt)}")
        print(f"Source(X) 포인트 수: {len(points_x)}")
        print("-" * 30)

        # ICP 알고리즘 실행
        transformed_x_points = icp(points_x, points_gt)

        # --- 타임스탬프 스케일 및 바이어스 계산 ---
        # 1. 각 파일의 시작과 끝 타임스탬프 가져오기
        gt_start_ts, gt_end_ts = gt_data[0][0], gt_data[-1][0]
        x_start_ts, x_end_ts = x_data[0][0], x_data[-1][0]

        # 2. 시간 길이(Duration) 계산
        gt_duration = gt_end_ts - gt_start_ts
        x_duration = x_end_ts - x_start_ts

        # 3. 스케일(scale)과 바이어스(bias) 계산
        if x_duration == 0:
            scale = 1.0
            bias = gt_start_ts - x_start_ts
        else:
            scale = gt_duration / x_duration
            bias = gt_start_ts - (x_start_ts * scale)

        print("\n" + "=" * 40)
        print("타임스탬프 정보:")
        print(f"  - GT 범위:  {gt_start_ts:.6f} -> {gt_end_ts:.6f} (길이: {gt_duration:.6f})")
        print(f"  - X 원본 범위: {x_start_ts:.6f} -> {x_end_ts:.6f} (길이: {x_duration:.6f})")
        print("\n계산된 변환 파라미터:")
        print(f"  - 스케일 (Scale): {scale:.10f}")
        print(f"  - 바이어스 (Bias): {bias:.10f}")
        print("=" * 40)

        # 변환된 데이터를 새 파일에 저장
        output_dir = os.path.dirname(output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        header_lines = []
        with open(x_filepath, "r") as infile:
            for line in infile:
                if line.strip().startswith("#"):
                    header_lines.append(line)
                else:
                    break

        with open(output_filepath, "w") as outfile:
            outfile.writelines(header_lines)

            for i, original_row in enumerate(x_data):
                # 타임스탬프에 스케일과 바이어스 적용
                new_timestamp = (original_row[0] * scale) + bias

                # ICP로 변환된 좌표 가져오기
                new_x, new_y, new_z = transformed_x_points[i]

                # 나머지 파트(쿼터니언 등)는 그대로 유지
                remaining_parts = [f"{v:.10f}" for v in original_row[4:]]

                # 새로운 라인 조합
                new_line_parts = [
                    f"{new_timestamp:.6f}",
                    f"{new_x:.10f}",
                    f"{new_y:.10f}",
                    f"{new_z:.10f}",
                ] + remaining_parts
                outfile.write(" ".join(new_line_parts) + "\n")

        print(f"\n성공적으로 정합 및 타임스탬프 변환 완료!")
        print(f"결과가 '{output_filepath}' 파일에 저장되었습니다.")

    except FileNotFoundError as e:
        print(f"오류: 파일을 찾을 수 없습니다. ({e.filename})")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
