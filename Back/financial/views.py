# financial/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from community.models import Post
from insight.models import InterestStock, StockAnalysis
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    # 커뮤니티 인기글 상위 3개: 총 반응 수 기준
    popular_posts = Post.objects.annotate(
        total_reactions=Count('reactions')
    ).order_by('-total_reactions')[:3]

    # 사용자의 관심 종목
    interest_stocks = InterestStock.objects.filter(user=request.user)

    # 분석 정보가 존재하는 종목만 필터링 + 임시 수익률 계산
    stock_infos = []
    for stock in interest_stocks:
        try:
            analysis = stock.stockanalysis
            # 임시 수익률 계산 로직 (실제로는 수익률 필드 또는 메서드 필요)
            sentiment = analysis.sentiment_stats
            rate = sentiment.get('positive', 0) - sentiment.get('negative', 0)
            stock_infos.append({
                'stock': stock,
                'analysis': analysis,
                'profit_rate': rate,
            })
        except StockAnalysis.DoesNotExist:
            continue

    # 수익률 높은 순 정렬
    sorted_stocks = sorted(stock_infos, key=lambda x: x['profit_rate'], reverse=True)

    return render(request, 'dashboard.html', {
        'popular_posts': popular_posts,
        'sorted_stocks': sorted_stocks,
    })
