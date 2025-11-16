# lottery/admin.py

from django.contrib import admin
from .models import Draw, Ticket, WinningResult
import random

# --- TicketAdmin에서 사용할 Inline ---
class WinningResultInline(admin.StackedInline):
    model = WinningResult
    extra = 0
    can_delete = False
    # 'prize' 필드 대신 'rank', 'matched_numbers'를 읽기 전용으로 설정
    readonly_fields = ('rank', 'matched_numbers') 

# --- ModelAdmin 정의 ---

@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    # 'bonus' 대신 'bonus_number' 사용
    list_display = ('round', 'numbers', 'bonus_number', 'draw_date', 'ticket_count')
    actions = ['perform_draw', 'calculate_winners'] # 2, 3번 기능

    # 1. 판매 실적 확인 (Ticket 모델의 'round' 필드와 'draw'의 'round'를 비교)
    def ticket_count(self, obj):
        # obj는 Draw 인스턴스 (예: 100회차)
        # 100회차에 해당하는 Ticket의 개수를 셈
        return Ticket.objects.filter(round=obj.round).count()
    ticket_count.short_description = "판매된 티켓 수"

    # 2. 로또 추첨 (모델 필드에 맞게 수정)
    def perform_draw(self, request, queryset):
        for draw in queryset:
            if draw.numbers:
                self.message_user(request, f"{draw.round}회차는 이미 추첨되었습니다.", level='WARNING')
                continue
            
            picked_numbers = random.sample(range(1, 46), 7)
            winning_set = sorted(picked_numbers[:6])
            
            # CharField에 맞게 쉼표로 구분된 문자열로 변환
            draw.numbers = ",".join(map(str, winning_set))
            # 'bonus'가 아니라 'bonus_number' 필드에 저장
            draw.bonus_number = picked_numbers[6] 
            draw.save()
            self.message_user(request, f"{draw.round}회차 추첨 완료. (번호: {draw.numbers}, 보너스: {draw.bonus_number})")
    perform_draw.short_description = "선택한 회차의 당첨 번호 추첨하기"

    # 3-A. 당첨 결과 계산 (모델 필드에 맞게 수정)
    def calculate_winners(self, request, queryset):
        for draw in queryset:
            if not draw.numbers:
                self.message_user(request, f"{draw.round}회차는 추첨이 완료되지 않았습니다.", level='ERROR')
                continue
            
            try:
                # '1,2,3' 형태의 문자열을 set{1, 2, 3}으로 변환
                winning_nums = set(map(int, draw.numbers.split(',')))
                bonus_num = draw.bonus_number # 'bonus_number' 사용
            except (ValueError, AttributeError):
                self.message_user(request, f"{draw.round}회차의 당첨 번호 형식이 잘못되었습니다. (예: 1,2,3,4,5,6)", level='ERROR')
                continue

            # "아직 추첨되지 않은" (round=None) 티켓들만 대상으로 함
            # (models.py 주석 "추첨 전이면 Null"에 근거)
            tickets_to_check = Ticket.objects.filter(round__isnull=True)
            
            if not tickets_to_check.exists():
                self.message_user(request, f"결과를 계산할 티켓이 없습니다 (모든 티켓에 이미 회차가 할당됨).", level='WARNING')
                continue

            winners_found = 0
            for ticket in tickets_to_check:
                try:
                    ticket_nums = set(map(int, ticket.numbers.split(',')))
                except (ValueError, AttributeError):
                    continue # 번호 형식이 잘못된 티켓은 스킵
                
                match_count = len(winning_nums.intersection(ticket_nums))
                has_bonus = bonus_num in ticket_nums
                
                rank = 0
                if match_count == 6: rank = 1
                elif match_count == 5 and has_bonus: rank = 2
                elif match_count == 5: rank = 3
                elif match_count == 4: rank = 4
                elif match_count == 3: rank = 5
                
                # 모든 티켓에 현재 회차 번호를 할당
                ticket.round = draw.round
                ticket.save()
                
                if rank > 0:
                    # 'prize' 대신 'matched_numbers' 필드에 저장
                    WinningResult.objects.update_or_create(
                        ticket=ticket,
                        defaults={'rank': rank, 'matched_numbers': match_count}
                    )
                    winners_found += 1
            
            self.message_user(request, f"{draw.round}회차의 당첨자 {winners_found}명을 처리하고, {tickets_to_check.count()}개 티켓에 회차를 할당했습니다.")
    calculate_winners.short_description = "선택한 회차의 당첨 결과 계산하기 (미할당 티켓 대상)"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    search_fields = ('numbers',)
    inlines = [WinningResultInline] # 3-B (Inline)

    # 3-B (List Display)
    def winning_rank(self, obj):
        try:
            return f"{obj.winningresult.rank}등"
        except WinningResult.DoesNotExist:
            return "낙첨"
    winning_rank.short_description = "당첨 결과"


@admin.register(WinningResult)
class WinningResultAdmin(admin.ModelAdmin):
    # 'ticket__draw' 대신 'ticket__round'로 필터링
    list_filter = ('rank', 'ticket__round') 
    
    def ticket_id(self, obj):
        return obj.ticket.id

    def draw_round(self, obj):
        return obj.ticket.round