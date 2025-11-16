from django.shortcuts import render, redirect # 장고의 렌더링 및 리다이렉트 함수 임포트
from django.contrib.auth.decorators import login_required # 로그인 필요 데코레이터 임포트
from .models import Ticket # 티켓 모델 임포트
from .utils import generate_lotto_numbers # 로또 넘버를 생성하는 유틸리티 함수 임포트

# 티켓 구매 뷰 함수, 뷰어는 urls.py에서 /lottery/buy_ticket/ 이 함수를 호출하여 티켓 구매 페이지를 렌더링하거나 티켓 구매 요청을 처리합니다.
@login_required
def buy_ticket(request):
    """
    티켓 구매 요청을 처리하거나 구매 페이지를 렌더링합니다.
    수동 : POST 요청에서 사용자가 선택한 번호로 티켓 생성
    자동 : generate_lotto_numbers 유틸리티 함수를 사용하여 무작위 번호 생성
    GET 요청 시 구매 페이지를 렌더링합니다.
    """
    
    if request.method == 'POST':
        buy_type = request.POST.get('buy_type')  # 구매 유형(수동/자동) 가져오기
        if buy_type == "manual":
            # 수동 구매 처리
            numbers = request.POST.get("numbers").replace(" ", "").split(",")  # 사용자가 입력한 번호 가져오기
        else: #자동
            # 자동 구매 처리
            numbers = generate_lotto_numbers()  # 유틸리티 함수로 무작위 번호 생성
        
        ticket = Ticket.objects.create(
            user=request.user,  # 현재 로그인한 사용자
            numbers=",".join(map(str, numbers)),  # 번호를 문자열로 저장
            is_auto=(buy_type == "auto")
        )
        return redirect('ticket_success')  # 구매 성공 페이지로 리다이렉트
    
    return render(request, 'lottery/buy_ticket.html')  # GET 요청 시 구매 페이지 렌더링

# 관리자 : 추첨 & 당첨을 확인합니다.
@staff_member_required
def draw_lottery(request):
    """
    관리자가 복권 추첨을 수행하고 당첨 결과를 확인하는 뷰 함수입니다.
    추첨 번호를 생성하고, 각 티켓과 비교하여 당첨 결과를 저장합니다.
    """
    """
    관리자가 추첨 버튼을 누르면 새로운 회차 생성
    """
    import random
    last_round = Draw.objects.count() # 마지막 회차 번호 가져오기
    nums = random.sample(range(1, 46), 6) # 1~45 사이에서 6개 번호 무작위 선택
    nums.sort() # 번호 정렬
    bonus = random.choice([n for n in range(1, 46) if n not in nums]) # 보너스 번호 선택

    # 새로운 추첨 회차 생성
    draw = Draw.objects.create(
        round=last_round + 1,
        numbers=",".join(map(str, nums)),
        bonus=bonus
    )

    # 모든 사용자 티켓에 대해 당첨 판별 수행
    tickets = Ticket.objects.filter(round__isnull=True)
    for t in tickets:
        t.round = draw.round
        t.save()

        matched = len(set(map(int, t.numbers.split(","))) & set(map(int, draw.numbers.split(","))))

        if matched == 6:
            rank, prize = 1, 2000000000
        elif matched == 5:
            rank, prize = 2, 50000000
        elif matched == 4:
            rank, prize = 3, 1500000
        elif matched == 3:
            rank, prize = 4, 50000
        else:
            continue

        WinningResult.objects.create(ticket=t, rank=rank, prize=prize)

    return render(request, "lottery/draw_complete.html", {"draw": draw})