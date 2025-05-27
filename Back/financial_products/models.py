# Back/financial_products/models.py
from django.db import models
from django.conf import settings

class Bank(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="금융회사 코드")
    name = models.CharField(max_length=100, verbose_name="금융회사 명")

    def __str__(self):
        return self.name

class FinancialProduct(models.Model):
    DEPOSIT = "deposit"
    SAVING  = "saving"
    PRODUCT_TYPE_CHOICES = [(DEPOSIT, "정기예금"), (SAVING, "적금")]

    bank              = models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name="은행")
    # bank_type       = models.CharField(max_length=20, choices=BANK_TYPE_CHOICES, null=True, blank=True) # API: bank_type (예: 은행, 저축은행 등)

    fin_prdt_cd       = models.CharField(max_length=100, verbose_name="금융상품 코드") # API: fin_prdt_cd
    dcls_month        = models.CharField(max_length=6, verbose_name="공시월 (YYYYMM)", null = True) # API: dcls_month
    
    name              = models.CharField(max_length=255, verbose_name="금융상품명") # API: fin_prdt_nm
    product_type      = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, verbose_name="상품 유형")
    
    join_way          = models.TextField(blank=True, null=True, verbose_name="가입 방법") # API: join_way
    mtrt_int          = models.TextField(blank=True, null=True, verbose_name="만기 후 이자율") # API: mtrt_int
    spcl_cnd          = models.TextField(blank=True, null=True, verbose_name="우대 조건") # API: spcl_cnd
    join_deny         = models.CharField(max_length=10, blank=True, null=True, verbose_name="가입제한") # API: join_deny (1:제한없음, 2:서민전용, 3:일부제한)
    join_member       = models.TextField(blank=True, null=True, verbose_name="가입 대상") # API: join_member
    etc_note          = models.TextField(blank=True, null=True, verbose_name="기타 유의사항") # API: etc_note
    max_limit         = models.BigIntegerField(null=True, blank=True, verbose_name="최고 한도") # API: max_limit (숫자일 수 있음)
    
    dcls_strt_day     = models.CharField(max_length=8, blank=True, null=True, verbose_name="공시 시작일") # API: dcls_strt_day (YYYYMMDD)
    dcls_end_day      = models.CharField(max_length=8, blank=True, null=True, verbose_name="공시 종료일") # API: dcls_end_day (YYYYMMDD or null)
    fin_co_subm_day   = models.CharField(max_length=12, blank=True, null=True, verbose_name="금융회사 제출일") # API: fin_co_subm_day (YYYYMMDDHHMM)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "금융 상품"
        verbose_name_plural = "금융 상품 목록"
        unique_together = ("fin_prdt_cd", "dcls_month") # 공시월 + 금융상품코드로 상품 구분
        ordering = ['dcls_month', 'bank__name', 'name']

    def __str__(self):
        return f"[{self.dcls_month}] {self.bank.name} - {self.name}"

class ProductOption(models.Model):
    INTEREST_TYPE_CHOICES = [
        ("S", "단리"),
        ("M", "복리"),
    ]
    # 적금의 적립 유형 (API: rsrv_type)
    RESERVE_TYPE_CHOICES = [
        ("S", "정액적립식"),
        ("F", "자유적립식"),
    ]

    product            = models.ForeignKey(FinancialProduct, on_delete=models.CASCADE, related_name="options", verbose_name="상품")
    
    intr_rate_type     = models.CharField(max_length=1, choices=INTEREST_TYPE_CHOICES, verbose_name="이자율 유형 코드") # API: intr_rate_type
    intr_rate_type_nm  = models.CharField(max_length=10, verbose_name="이자율 유형명") # API: intr_rate_type_nm
    
    # 적금상품의 경우 추가되는 필드
    rsrv_type          = models.CharField(max_length=1, choices=RESERVE_TYPE_CHOICES, blank=True, null=True, verbose_name="적립 유형 코드") # API: rsrv_type
    rsrv_type_nm       = models.CharField(max_length=20, blank=True, null=True, verbose_name="적립 유형명") # API: rsrv_type_nm

    save_trm           = models.PositiveSmallIntegerField(verbose_name="저축 기간 (개월)")
    intr_rate          = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="저축 금리 (기본)") # API: intr_rate
    intr_rate2         = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="최고 우대 금리") # API: intr_rate2

    class Meta:
        verbose_name = "상품 옵션"
        verbose_name_plural = "상품 옵션 목록"
        # 한 상품에 대해 (기간, 이자율유형, 적립유형(적금의경우)) 조합은 유니크해야 함
        unique_together = ("product", "save_trm", "intr_rate_type", "rsrv_type") 
        ordering = ['product', 'save_trm', 'intr_rate_type', 'rsrv_type']

    def __str__(self):
        return f"{self.product.name} - {self.save_trm}개월 ({self.intr_rate_type_nm}, {self.rsrv_type_nm or ''}) {self.intr_rate}% (최대 {self.intr_rate2}%)"


class JoinedProduct(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="joined_financial_products", verbose_name="사용자")
    product   = models.ForeignKey(FinancialProduct, on_delete=models.CASCADE, verbose_name="가입 상품") # 사용 편의를 위해 직접 연결
    option    = models.ForeignKey(ProductOption, on_delete=models.PROTECT, verbose_name="선택 옵션") # 특정 옵션에 가입
    amount    = models.PositiveIntegerField(verbose_name="가입 금액")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="가입일시")

    class Meta:
        verbose_name = "가입 상품"
        verbose_name_plural = "가입 상품 목록"
        unique_together = ("user", "option") # 사용자는 특정 옵션에 한 번만 가입 가능하도록
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.option}"