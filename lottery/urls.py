from django.urls import path
from . import views

# URL에 lottery안에서 url을 연결합니다
urlpatterns = [
    # path('route/', views.view_function, name='route_name'),
    path('buy/', views.buy_ticket, name="buy_ticket"), # buy라는 url요청이 들어오면 사용자 티켓 구매 함수로 연결합니다.
    path('my_tickets/', views.my_tickets, name="my_tickets"),  # my_tickets라는 url요청이 들어오면 사용자 티켓 확인 함수로 연결합니다.
    path('check/<int:ticket_id>/<uuid:access_code>/', views.check_ticket, name="check_ticket"),  # check/티켓ID/접근코드/ 형태의 url요청이 들어오면 티켓 확인 함수로 연결합니다.
    path('draw/', views.draw_lottery, name="draw_lottery"),  # draw라는 url요청이 들어오면 관리자 추첨 함수로 연결합니다.
]