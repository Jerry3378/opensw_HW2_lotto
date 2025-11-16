# lotto_site/lottery/models.py
# Django models for the lottery application

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Draw(models.Model):
    # 관리자가 생성하는 복권 추첨 이벤트 모델
    round = models.IntegerField(unique=True) # 추첨 회차
    numbers = models.CharField(max_length=30)  # 당첨 번호를 쉼표로 구분된 문자열로 저장(예: 1,5,10,16,27,42)
    bonus_number = models.IntegerField()  # 보너스 번호
    draw_date = models.DateField(default=timezone.now)  # 추첨 날짜
    
    def __str__(self):
        return f"{self.round}회차 "

class Ticket(models.Model):
    # 사용자가 구매한 복권 티켓 모델
    round = models.IntegerField(null = True, blank=True) # 추첨 전이면 Null, 추첨 후에는 회차 정보
    numbers = models.CharField(max_length=30)  # 구매한 번호를 쉼표로 구분된 문자열로 저장(예: 3,11,15,22,28,35)
    purchase_date = models.DateTimeField(default=timezone.now)  # 구매 날짜 및 시간
    is_auto = models.BooleanField(default=False)  # 자동 구매 여부
    
    access_code = models.UUIDField(default=uuid.uuid4, editable=False)  # 비회원 확인용
    
    def __str__(self):
        return f"{self.id}번 티켓: {self.numbers}"


class WinningResult(models.Model):
    
    """사용자별 당첨 결과 저장"""
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)  # 해당 티켓
    rank = models.IntegerField(null=True, blank=True)  # 당첨 등수 (1~5등, 미당첨은 Null)
    matched_numbers = models.IntegerField(default=0)  # 맞춘 번호 개수, 상금액
    
    def __str__(self):
        return f"티켓 {self.ticket.id}번 - {self.rank}등" + f" ({self.matched_numbers}개 맞춤)"