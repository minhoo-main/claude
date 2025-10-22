"""
샘플 데이터를 ETL 변환하여 레포트 생성용 데이터 준비
"""
import pandas as pd

print("=" * 70)
print("🔄 샘플 데이터 변환 시작")
print("=" * 70)

# 샘플 데이터 로드
print("📥 샘플 데이터 로딩 중...")
df = pd.read_csv('bloomberg_sample_data.csv')
print(f"✅ {len(df)}개 레코드 로드")

# 날짜 형식 변환
df['date'] = pd.to_datetime(df['date'])

# 예측 오차 계산
print("🔄 예측 오차 계산 중...")
df['forecast_error'] = df['actual'] - df['forecast']
df['forecast_error_pct'] = ((df['actual'] - df['forecast']) / df['forecast'] * 100).round(2)

# 전월 대비 변화
print("🔄 전월 대비 변화 계산 중...")
df['mom_change'] = df['actual'] - df['previous']
df['mom_change_pct'] = ((df['actual'] - df['previous']) / df['previous'] * 100).round(2)

# 예측 정확도
print("🔄 예측 정확도 계산 중...")
df['forecast_accuracy'] = (100 - abs(df['forecast_error_pct'])).clip(0, 100).round(2)

# 서프라이즈 판단
print("🔄 서프라이즈 판단 중...")
df['surprise'] = df['forecast_error_pct'].apply(
    lambda x: 'Positive Surprise' if x > 1 else
             'Negative Surprise' if x < -1 else
             'In Line'
)

# 트렌드 판단
print("🔄 트렌드 판단 중...")
df['trend'] = df['mom_change'].apply(
    lambda x: '↑ Improving' if x > 0 else
             '↓ Declining' if x < 0 else
             '→ Stable'
)

# 저장
output_path = 'bloomberg_transformed_data.csv'
print(f"💾 변환된 데이터 저장 중: {output_path}")
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print()
print("=" * 70)
print("✅ 샘플 데이터 변환 완료")
print("=" * 70)
print(f"\n📊 변환된 데이터 정보:")
print(f"  - 총 레코드: {len(df)}")
print(f"  - 컬럼 수: {len(df.columns)}")
print(f"  - 국가: {', '.join(df['country'].unique())}")
print(f"  - 지표: {', '.join(df['indicator'].unique())}")
print(f"\n📁 출력 파일: {output_path}")
