"""
블룸버그 단말기에서 거시경제 데이터 추출 ETL 코드
실제 환경에서는 블룸버그 API (blpapi)를 사용합니다.
"""
import pandas as pd
from datetime import datetime, timedelta


class BloombergETL:
    """블룸버그 단말기 데이터 추출, 변환, 적재"""

    def __init__(self, use_sample=False):
        """
        Args:
            use_sample: True면 샘플 데이터 사용, False면 실제 블룸버그 API 사용
        """
        self.use_sample = use_sample
        self.raw_data = None
        self.transformed_data = None

    def extract_from_bloomberg(self, indicators, countries, start_date, end_date):
        """
        블룸버그 단말기에서 데이터 추출 (실제 환경용)

        Args:
            indicators: 지표 리스트 (예: ['GDP', 'CPI', 'UNEMPLOYMENT'])
            countries: 국가 리스트 (예: ['US', 'CN', 'JP'])
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        """
        print("📥 블룸버그 단말기에서 데이터 추출 중...")

        if self.use_sample:
            # 샘플 데이터 사용
            print("⚠️  샘플 데이터 모드 - 실제 블룸버그 API 대신 샘플 데이터 사용")
            self.raw_data = pd.read_csv('bloomberg_sample_data.csv')
        else:
            # 실제 블룸버그 API 사용
            try:
                import blpapi

                # 블룸버그 세션 시작
                sessionOptions = blpapi.SessionOptions()
                sessionOptions.setServerHost("localhost")
                sessionOptions.setServerPort(8194)
                session = blpapi.Session(sessionOptions)

                if not session.start():
                    raise Exception("블룸버그 세션 시작 실패")

                if not session.openService("//blp/refdata"):
                    raise Exception("블룸버그 서비스 열기 실패")

                # 데이터 추출 로직
                # (실제 블룸버그 티커와 필드를 사용하여 데이터 요청)
                refDataService = session.getService("//blp/refdata")
                request = refDataService.createRequest("HistoricalDataRequest")

                data_list = []
                for country in countries:
                    for indicator in indicators:
                        # 블룸버그 티커 형식: INDICATOR COUNTRY Index
                        ticker = f"{indicator} {country} Index"
                        request.append("securities", ticker)

                request.set("startDate", start_date.replace("-", ""))
                request.set("endDate", end_date.replace("-", ""))
                request.append("fields", "PX_LAST")  # 실제값
                request.append("fields", "ECO_FUTURE_MEDIAN")  # 예측값

                session.sendRequest(request)

                # 응답 처리
                while True:
                    ev = session.nextEvent(500)
                    # 응답 파싱 및 DataFrame 변환 로직
                    # ... (실제 구현 필요)
                    if ev.eventType() == blpapi.Event.RESPONSE:
                        break

                self.raw_data = pd.DataFrame(data_list)
                session.stop()

            except ImportError:
                print("❌ blpapi 패키지가 설치되지 않았습니다.")
                print("   pip install blpapi 로 설치하거나")
                print("   use_sample=True로 샘플 데이터를 사용하세요.")
                raise
            except Exception as e:
                print(f"❌ 블룸버그 데이터 추출 실패: {e}")
                raise

        print(f"✅ {len(self.raw_data)}개 레코드 추출 완료")
        return self.raw_data

    def transform(self):
        """데이터 변환 및 계산"""
        print("🔄 데이터 변환 중...")

        if self.raw_data is None:
            raise ValueError("먼저 extract_from_bloomberg()를 실행해주세요.")

        df = self.raw_data.copy()

        # 날짜 형식 변환
        df['date'] = pd.to_datetime(df['date'])

        # 예측 오차 계산
        df['forecast_error'] = df['actual'] - df['forecast']
        df['forecast_error_pct'] = ((df['actual'] - df['forecast']) / df['forecast'] * 100).round(2)

        # 전월 대비 변화
        df['mom_change'] = df['actual'] - df['previous']
        df['mom_change_pct'] = ((df['actual'] - df['previous']) / df['previous'] * 100).round(2)

        # 예측 정확도
        df['forecast_accuracy'] = (100 - abs(df['forecast_error_pct'])).clip(0, 100).round(2)

        # 서프라이즈 판단 (예측과 실제의 차이가 클 때)
        df['surprise'] = df['forecast_error_pct'].apply(
            lambda x: 'Positive Surprise' if x > 1 else
                     'Negative Surprise' if x < -1 else
                     'In Line'
        )

        # 트렌드 판단
        df['trend'] = df['mom_change'].apply(
            lambda x: '↑ Improving' if x > 0 else
                     '↓ Declining' if x < 0 else
                     '→ Stable'
        )

        self.transformed_data = df
        print(f"✅ 데이터 변환 완료 - {len(df)}개 레코드, {len(df.columns)}개 컬럼")
        return self.transformed_data

    def load(self, output_path):
        """변환된 데이터를 CSV로 저장"""
        print(f"💾 데이터 저장 중: {output_path}")

        if self.transformed_data is None:
            raise ValueError("먼저 transform()을 실행해주세요.")

        self.transformed_data.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 데이터 저장 완료")
        return self.transformed_data

    def run_pipeline(self, indicators=None, countries=None,
                     start_date=None, end_date=None, output_path='bloomberg_data.csv'):
        """전체 ETL 파이프라인 실행"""
        print("=" * 70)
        print("🚀 블룸버그 ETL 파이프라인 시작")
        print("=" * 70)

        # 기본값 설정
        if indicators is None:
            indicators = ['GDP', 'CPI', 'UNEMPLOYMENT']
        if countries is None:
            countries = ['US', 'CN', 'JP']
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        print(f"📍 지표: {', '.join(indicators)}")
        print(f"📍 국가: {', '.join(countries)}")
        print(f"📍 기간: {start_date} ~ {end_date}")
        print()

        self.extract_from_bloomberg(indicators, countries, start_date, end_date)
        self.transform()
        result = self.load(output_path)

        print()
        print("=" * 70)
        print("✅ ETL 파이프라인 완료")
        print("=" * 70)

        return result


if __name__ == "__main__":
    # ETL 실행 예제 (샘플 데이터 모드)
    etl = BloombergETL(use_sample=True)
    data = etl.run_pipeline(output_path='bloomberg_transformed_data.csv')

    print("\n📊 변환된 데이터 샘플:")
    print(data.head(10))

    print("\n📈 데이터 요약:")
    print(f"총 레코드 수: {len(data)}")
    print(f"국가: {', '.join(data['country'].unique())}")
    print(f"지표: {', '.join(data['indicator'].unique())}")
    print(f"날짜 범위: {data['date'].min()} ~ {data['date'].max()}")
