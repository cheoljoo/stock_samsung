# stock_samsung
삼성전자와 삼성전자(우)의 비교 : 언제 어떤 것을 사야 유리한지?

# 작업 순서
- old directory : 20년치 backtest
- 250630 directory : 5년치 backtest
- 5years : 5년치 backtest 
- 20years : 20년치 backtest에 여러가지 그래프 추가
- 5years_copied_from_20years : 5년치인데 20years처럼 여러가지 그래프 추가
- reverse/5years_copied_from_20years : 기존 사분위 25%이하이면 삼성전자 구매 -> 삼성전자(우)로 구매로 반대 매수
- reverse/20years : 기존 사분위 25%이하이면 삼성전자 구매 -> 삼성전자(우)로 구매로 반대 매수
- 20years_with_window_size : 사분위를 구할때 위의 것들은 모든 구간에 대해서 계산을 했지만, 구하는 시간의 2,3 5년 Window size를 가지고 계산하도록 수정함.
- years_with_window_size : windows size는 2,3,5년이고,  backtest 기간도 3,5,10,20,30년으로 한다.
