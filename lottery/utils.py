# 여기서는 로또 번호 생성 같이 전체 앱에서 공통적으로 사용되지만, View나 Model에 속하지 않는 유틸리티 함수들을 정의합니다.
# lotto_site/lottery/utils.py
# 주로 로직 재사용, 프로젝트 전역 공통 유틸, 서비스 로직 보조 함수들을 포함

import random

def generate_lotto_numbers():
    """6개의 고유한 로또 번호를 무작위로 생성하여 정렬된 리스트로 반환"""
    numbers = random.sample(range(1, 46), 6)  # 1부터 45까지의 숫자 중 6개를 무작위로 선택
    numbers.sort()  # 번호를 오름차순으로 정렬
    return numbers