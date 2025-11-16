from django.shortcuts import render, redirect # 장고의 렌더링 및 리다이렉트 함수 임포트
from django.contrib.admin.views.decorators import staff_member_required # 관리자 전용 뷰 데코레이터 임포트
from .models import Ticket, Draw, WinningResult # 티켓 및 추첨/당첨 결과 모델 임포트
from .utils import generate_lotto_numbers # 로또 넘버를 생성하는 유틸리티 함수 임포트

# 티켓 구매 뷰 함수, 뷰어는 urls.py에서 /lottery/buy_ticket/ 이 함수를 호출하여 티켓 구매 페이지를 렌더링하거나 티켓 구매 요청을 처리합니다.
def buy_ticket(request):
    if request.method == "POST":
        buy_type = request.POST.get("type")

        if buy_type == "manual":
            numbers = request.POST.get("numbers").replace(" ", "").split(",")
        else:
            numbers = generate_lotto_numbers()

        ticket = Ticket.objects.create(
            numbers=",".join(map(str, numbers)),
            is_auto=(buy_type != "manual")
        )
        
        # 비 회원이므로 쿠키/세션으로 티켓 ID목록을 저장합니다
        # 세션 저장
        session_list = request.session.get("tickets", [])
        session_list.append(ticket.id)
        request.session["tickets"] = session_list
        # 티켓 확인 URL 생성
        from django.urls import reverse
        check_url = request.build_absolute_uri(
            reverse("check_ticket", args=[ticket.id, ticket.access_code])
        )
        return render(request, "lottery/buy_success.html", {
            "ticket": ticket,
            "check_url": check_url
        })

    return render(request, "lottery/buy_ticket.html")


# 티켓 확인 뷰 함수, 비회원도 접근 가능
from django.shortcuts import get_object_or_404
def check_ticket(request, ticket_id, access_code):
    ticket = get_object_or_404(Ticket, id=ticket_id, access_code=access_code)
    return render(request, "lottery/check_ticket.html", {"ticket": ticket})

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
    nums = generate_lotto_numbers() # 로또 번호 생성
    bonus = random.choice([n for n in range(1, 46) if n not in nums]) # 보너스 번호 선택

    # 새로운 추첨 회차 생성
    draw = Draw.objects.create(
        round=last_round + 1,
        numbers=",".join(map(str, nums)),
        bonus=bonus
    )

    # 당첨 판정
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

# 독립된 홈 페이지 템플릿으로 처음 접속시 보여줄 뷰 함수입니다,
def home(request):
    return render(request, 'lottery/home.html')

def my_tickets(request):
    ticket_ids = request.session.get("tickets", [])
    tickets = Ticket.objects.filter(id__in=ticket_ids)

    return render(request, "lottery/my_tickets.html", {
        "tickets": tickets,
    })