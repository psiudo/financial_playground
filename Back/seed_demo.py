# back/seed_demo.py
#!/usr/bin/env python
# seed_demo.py

import os
import django
import sys
from datetime import date

# ── Django 환경 초기화 ───────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financial.settings")
django.setup()

# ── 공통 유틸 ────────────────────────────────────────────────
from django.contrib.auth import get_user_model

def get_or_create_user(username="test1", email="test1@example.com", password="test1234"):
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email}
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ User '{username}' created with password '{password}'")
    else:
        print(f"✅ User '{username}' already exists")
    return user

# ── 1) Financial Products 시드 ────────────────────────────
def seed_financial_products(user):
    from financial_products.models import Bank, FinancialProduct, ProductOption, JoinedProduct

    shinhan, _ = Bank.objects.get_or_create(code="088", name="신한은행")
    kb,      _ = Bank.objects.get_or_create(code="004", name="국민은행")
    print("  • Banks seeded")

    fp1, _ = FinancialProduct.objects.get_or_create(
        bank=shinhan,
        name="신한 스탠다드 예금",
        defaults={
            "product_type": FinancialProduct.DEPOSIT,
            "description": "Seed 데모용 정기예금",
        }
    )
    fp2, _ = FinancialProduct.objects.get_or_create(
        bank=kb,
        name="국민 저축 적금",
        defaults={
            "product_type": FinancialProduct.SAVING,
            "description": "Seed 데모용 적금",
        }
    )
    print("  • FinancialProducts seeded")

    opt1, _ = ProductOption.objects.get_or_create(
        product=fp1,
        term_months=6,
        defaults={"rate": 1.5}
    )
    opt2, _ = ProductOption.objects.get_or_create(
        product=fp2,
        term_months=12,
        defaults={"rate": 2.0}
    )
    print("  • ProductOptions seeded")

    jp1, created = JoinedProduct.objects.get_or_create(
        user=user,
        product=fp1,
        option=opt1,
        defaults={"amount": 100000, "joined_at": date.today()}
    )
    print("  • JoinedProduct", "created" if created else "already exists")

# ── 2) Simulator 시드 ──────────────────────────────────────
def seed_simulator(user):
    from simulator.models import VirtualPortfolio, VirtualTrade

    vp, _ = VirtualPortfolio.objects.get_or_create(user=user)
    print("  • VirtualPortfolio ensured")

    # 샘플 매수/매도 기록
    t1, _ = VirtualTrade.objects.get_or_create(
        portfolio=vp,
        stock_code="AAPL",
        defaults={"trade_type": VirtualTrade.BUY, "stock_name": "Apple", "price": 150, "quantity": 10}
    )
    t2, _ = VirtualTrade.objects.get_or_create(
        portfolio=vp,
        stock_code="GOOG",
        defaults={"trade_type": VirtualTrade.BUY, "stock_name": "Google", "price": 2800, "quantity": 5}
    )
    print("  • VirtualTrades seeded")

# ── 3) Insight 시드 ────────────────────────────────────────
def seed_insight(user):
    from insight.models import InterestStock

    is1, _ = InterestStock.objects.get_or_create(user=user, company_name="카카오", stock_code="035720")
    is2, _ = InterestStock.objects.get_or_create(user=user, company_name="삼성전자", stock_code="005930")
    print("  • InterestStock seeded")

# ── 4) Community 시드 ──────────────────────────────────────
def seed_community(user):
    from community.models import Post, Comment, Reaction

    p1, _ = Post.objects.get_or_create(
        author=user,
        title="Seed 데모 글",
        defaults={"content": "seed_demo.py 로 생성된 글입니다."}
    )
    c1, _ = Comment.objects.get_or_create(post=p1, author=user, content="첫 댓글입니다.")
    c2, _ = Comment.objects.get_or_create(post=p1, author=user, parent=c1, content="대댓글 예시입니다.")
    print("  • Post & Comments seeded")

    Reaction.objects.get_or_create(post=p1, user=user, reaction_type="like")
    Reaction.objects.get_or_create(post=p1, user=user, reaction_type="sad")
    print("  • Reactions seeded")

# ── 5) Commodities 시드 ────────────────────────────────────
def seed_commodities():
    from commodities.models import Commodity, PriceHistory

    gold, _   = Commodity.objects.get_or_create(symbol="XAU", name="Gold")
    silver, _ = Commodity.objects.get_or_create(symbol="XAG", name="Silver")
    PriceHistory.objects.get_or_create(commodity=gold, date=date.today(), defaults={"price": 2000.0})
    PriceHistory.objects.get_or_create(commodity=silver, date=date.today(), defaults={"price": 25.0})
    print("  • Commodities & PriceHistory seeded")

# ── 6) Bank Locations 시드 ─────────────────────────────────
def seed_bank_locations():
    from bank_locations.models import BankBranch

    BankBranch.objects.get_or_create(
        bank_name="신한은행",
        branch_name="강남지점",
        defaults={"address": "서울 강남구", "latitude":37.4979, "longitude":127.0276}
    )
    BankBranch.objects.get_or_create(
        bank_name="국민은행",
        branch_name="종로지점",
        defaults={"address": "서울 종로구", "latitude":37.5729, "longitude":126.9794}
    )
    print("  • BankBranch seeded")

# ── 7) (선택) Strategy·Marketplace 도메인 등 추가 시드 ───────

def run():
    print("🚀 Seed 시작")
    user = get_or_create_user()
    seed_financial_products(user)
    seed_simulator(user)
    seed_insight(user)
    seed_community(user)
    seed_commodities()
    seed_bank_locations()
    print("🎉 모든 도메인 시드 완료!")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("❌ Seed 실패:", e)
        sys.exit(1)
