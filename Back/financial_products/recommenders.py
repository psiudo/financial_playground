# Back/financial_products/recommenders.py
from datetime import date
from django.db.models import (
    Q, Max, Min, Prefetch, Case, When, Value, IntegerField, FloatField,
    CharField, Subquery, OuterRef, Count, Avg
)
from django.db.models.functions import Coalesce, Cast
from accounts.models import CustomUser # 사용자 모델
from .models import FinancialProduct, ProductOption, Bank # 상품, 옵션, 은행 모델
import logging # 로깅 추가

logger = logging.getLogger(__name__) # 로거 생성

# --- Helper Functions ---
def _calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    # Ensure birth_date is a date object if it's not already
    if isinstance(birth_date, str):
        try:
            birth_date = date.fromisoformat(birth_date)
        except ValueError:
            logger.warning(f"Invalid birth_date format: {birth_date}")
            return None
            
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def _get_product_features_for_scoring(product: FinancialProduct):
    features = {
        "product_type": product.product_type,
        "bank_name": product.bank.name if product.bank else "정보없음",
        "max_interest_rate2": 0.0,
        "avg_interest_rate": 0.0,
        "min_term": None,
        "max_term": None,
        "spcl_keywords": set()
    }

    options_list = list(product.options.all())

    if options_list:
        rates2 = [float(opt.intr_rate2) for opt in options_list if opt.intr_rate2 is not None]
        rates = [float(opt.intr_rate) for opt in options_list if opt.intr_rate is not None]
        terms = [int(opt.save_trm) for opt in options_list if opt.save_trm is not None]

        if rates2: features["max_interest_rate2"] = max(rates2)
        if rates: features["avg_interest_rate"] = round(sum(rates) / len(rates), 2) if rates else 0.0
        if terms:
            features["min_term"] = min(terms)
            features["max_term"] = max(terms)
        
        # ★ 수정: spcl_cnd는 FinancialProduct 모델의 필드이므로 product 객체에서 직접 가져옵니다.
        if product.spcl_cnd:
            keywords = product.spcl_cnd.lower()
            for char_to_replace in [',', '.', ';', '(', ')', '/']:
                keywords = keywords.replace(char_to_replace, ' ')
            features["spcl_keywords"].update(keywords.split())
            
    return features

def _get_product_score_v2(product_features, user_age, user_risk_grade, user_annual_income, preferred_bank_name, similar_user_group_prefs=None):
    score = 0.0
    reasons = []

    # 1. 기본 점수 (최고 금리)
    max_rate2_feat = product_features.get("max_interest_rate2", 0.0)
    if max_rate2_feat > 0:
        score += max_rate2_feat * 10 
        if max_rate2_feat >= 3.5:
            reasons.append(f"높은 최고금리({max_rate2_feat:.2f}%)")

    # 2. 투자 성향 매칭
    product_type_feat = product_features.get("product_type")
    avg_rate_feat = product_features.get("avg_interest_rate", 0.0)

    if user_risk_grade == 'low':
        if product_type_feat == FinancialProduct.DEPOSIT:
            score += 30; reasons.append("안정적인 예금")
        if avg_rate_feat >= 2.0: score += 10

    elif user_risk_grade == 'middle':
        if product_type_feat == FinancialProduct.SAVING:
            score += 20; reasons.append("목돈마련 적금")
        else: score += 10 
        if max_rate2_feat >= 3.0: score += 10
            
    elif user_risk_grade == 'high':
        if product_type_feat == FinancialProduct.SAVING:
            score += 30; reasons.append("고수익 추구 적금")
        if max_rate2_feat >= 4.0: score += 20

    # 3. 나이대별 선호도
    spcl_keywords_feat = product_features.get("spcl_keywords", set())
    youth_keywords_match = {'청년', 'young', '2030', 'mz'} & spcl_keywords_feat
    senior_keywords_match = {'시니어', '은퇴', '50+', '골든', '노후'} & spcl_keywords_feat
    min_term_feat = product_features.get("min_term")
    max_term_feat = product_features.get("max_term")

    if user_age is not None:
        if 20 <= user_age < 35:
            if youth_keywords_match: # ★ 수정: set이 비어있지 않은지 확인
                keyword_to_add = list(youth_keywords_match)[0] # ★ 수정: 첫 번째 요소 안전하게 가져오기
                score += 25; reasons.append(f"{keyword_to_add} 대상 상품")
            if min_term_feat is not None and min_term_feat <= 12 : score += 10
        elif user_age >= 50:
            if senior_keywords_match: # ★ 수정: set이 비어있지 않은지 확인
                keyword_to_add = list(senior_keywords_match)[0] # ★ 수정: 첫 번째 요소 안전하게 가져오기
                score += 20; reasons.append(f"{keyword_to_add} 맞춤 상품")
            if product_type_feat == FinancialProduct.DEPOSIT: score += 10 # product_type_feat 사용
            if max_term_feat is not None and max_term_feat >= 24: score += 5
            
    # 4. 선호 은행
    bank_name_feat = product_features.get("bank_name", "정보없음")
    if preferred_bank_name and preferred_bank_name.lower() in bank_name_feat.lower():
        score += 20; reasons.append(f"선호은행({bank_name_feat}) 상품")
    
    unique_reasons = sorted(list(set(reasons)))
    reason_summary = ", ".join(unique_reasons[:3]) if unique_reasons else "추천 상품입니다."
    if len(unique_reasons) > 3: reason_summary += " 등"
    
    return score, reason_summary


def get_advanced_recommendations(user: CustomUser, top_n=5):
    try:
        logger.info(f"Starting advanced recommendations for user: {user.username} (ID: {user.id})")
        
        if not user.birth_date:
            logger.warning(f"User {user.username} has no birth_date. Age-based scoring will be affected.")
        if not user.risk_grade:
            logger.warning(f"User {user.username} has no risk_grade. Risk-based scoring will be affected.")

        user_age = _calculate_age(user.birth_date)
        user_risk_grade = user.risk_grade 
        user_annual_income = user.annual_income 
        preferred_bank_name = user.preferred_bank

        all_products_qs = FinancialProduct.objects.select_related("bank").prefetch_related(
            Prefetch("options", queryset=ProductOption.objects.order_by('-intr_rate2')) 
        ).filter(options__isnull=False, bank__isnull=False).distinct()

        if not all_products_qs.exists():
            logger.warning("No products available in the database for recommendations.")
            return []

        joined_fin_codes = user.joined_financial_products.values_list('product__fin_prdt_cd', flat=True)
        
        eligible_products_list = [p for p in list(all_products_qs) if p.fin_prdt_cd not in joined_fin_codes]

        if not eligible_products_list:
            logger.info(f"User {user.username} has no eligible products for new recommendations (all joined or no products).")
            return []
            
        similar_user_group_prefs = None 

        scored_products = []
        for product_obj in eligible_products_list: 
            product_features = _get_product_features_for_scoring(product_obj)
            score, reason = _get_product_score_v2(
                product_features, user_age, user_risk_grade, 
                user_annual_income, preferred_bank_name,
                similar_user_group_prefs 
            )
            if score > 5: 
                scored_products.append({
                    "product": product_obj,
                    "features": product_features,
                    "score": score,
                    "reason": reason,
                })
        
        logger.info(f"Scored {len(scored_products)} products for user {user.username} before sorting.")
        
        sorted_recommendations = sorted(
            scored_products,
            key=lambda x: (
                x['score'], 
                x['features'].get('max_interest_rate2', 0.0), 
                x['product'].name 
            ),
            reverse=True
        )
        
        final_recommendations = sorted_recommendations[:top_n]

        if len(final_recommendations) < top_n:
            num_needed = top_n - len(final_recommendations)
            current_product_ids = [item['product'].id for item in final_recommendations] 
            
            fallback_products_qs = FinancialProduct.objects.select_related("bank").prefetch_related(
                Prefetch("options", queryset=ProductOption.objects.order_by('-intr_rate2'))
            ).annotate(
                annotated_max_intr_rate2=Coalesce(Cast(Max('options__intr_rate2', filter=Q(options__intr_rate2__isnull=False)), FloatField()), Value(0.0))
            ).filter(
                options__isnull=False, bank__isnull=False
            ).exclude(
                id__in=current_product_ids 
            )
            if joined_fin_codes: 
                fallback_products_qs = fallback_products_qs.exclude(fin_prdt_cd__in=joined_fin_codes)
            
            fallback_products_qs = fallback_products_qs.distinct().order_by('-annotated_max_intr_rate2', 'name')
            additional_products = list(fallback_products_qs[:num_needed])
            
            for product_fallback in additional_products:
                product_features_fallback = _get_product_features_for_scoring(product_fallback) 
                max_rate_fallback = product_features_fallback.get('max_interest_rate2', 0.0)
                fallback_reason = f"높은 금리({max_rate_fallback:.2f}%)의 인기 상품입니다." 
                final_recommendations.append({
                    "product": product_fallback,
                    "features": product_features_fallback,
                    "score": max_rate_fallback * 5, 
                    "reason": fallback_reason
                })
            
            final_recommendations = sorted(
                final_recommendations, 
                key=lambda x: x['score'], 
                reverse=True
            )[:top_n]
        
        logger.info(f"Successfully generated {len(final_recommendations)} recommendations for user {user.username}.")
        return final_recommendations

    except Exception as e:
        logger.error(f"Critical Error in get_advanced_recommendations for user {user.username}: {e}", exc_info=True)
        return []