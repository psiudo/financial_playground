# Back/insight/views.py
import threading
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import InterestStock, StockAnalysis, Comment
from .forms import InterestStockForm
from analysis.services import (
    fetch_and_save_comments,
    analyze_stock_comments,
    summarize_analysis,
)

# ─────────────────────────────────────────────
@login_required
def profile(request):
    insight = InterestStock.objects.filter(user=request.user)
    if request.method == "POST":
        form = InterestStockForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["company_name"]
            if not insight.filter(company_name__iexact=name).exists():
                s = form.save(commit=False)
                s.user = request.user
                s.stock_code = "000000"
                s.save()
            return redirect("insight:profile")
    else:
        form = InterestStockForm()
    return render(request, "insight/profile.html", {"insight": insight, "form": form})

# ─────────────────────────────────────────────
def _backend_classify(analysis_id):
    analysis = StockAnalysis.objects.get(id=analysis_id)
    analyze_stock_comments(analysis)

@login_required
def collect_comments(request, stock_id):
    stock = get_object_or_404(InterestStock, id=stock_id, user=request.user)
    analysis = fetch_and_save_comments(stock)

    if analysis is None:
        return render(request, "insight/analysis_result.html", {"error": "댓글을 찾을 수 없습니다.", "stock": stock})

    threading.Thread(target=_backend_classify, args=(analysis.id,), daemon=True).start()
    return render(request, "insight/analysis_result.html", {"stock": stock, "analysis": analysis})

@login_required
def perform_analysis(request, stock_id):
    stock = get_object_or_404(InterestStock, id=stock_id, user=request.user)
    analysis = stock.stockanalysis

    if not analysis.batch_ready:
        return render(request, "insight/analysis_result.html", {"error": "아직 배치가 준비되지 않았습니다.", "stock": stock, "analysis": analysis})

    summarize_analysis(analysis)
    return render(request, "insight/analysis_result.html", {"stock": stock, "analysis": analysis})

@login_required
def refresh_comments(request, stock_id):
    return collect_comments(request, stock_id)

@login_required
def analysis_status(request, stock_id):
    analysis = get_object_or_404(StockAnalysis, stock_id=stock_id)
    return JsonResponse({"ready": analysis.batch_ready})

@login_required
def delete_stock(request, stock_id):
    get_object_or_404(InterestStock, id=stock_id, user=request.user).delete()
    return redirect("insight:profile")