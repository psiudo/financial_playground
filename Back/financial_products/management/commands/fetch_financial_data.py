# Back/financial_products/management/commands/fetch_financial_data.py
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from decimal import Decimal, InvalidOperation

from financial_products.models import Bank, FinancialProduct, ProductOption

class Command(BaseCommand):
    help = '금융감독원 API로부터 정기예금 및 적금 상품 정보를 가져와 DB에 저장합니다.'

    def fetch_and_save_data(self, product_type_code, product_type_name, api_url, api_key):
        current_page = 1
        total_pages = 1 

        # 기존 데이터 삭제 로직 (선택적: 매번 새로 모든 데이터를 가져오고 싶을 때)
        # self.stdout.write(self.style.WARNING(f'기존 {product_type_name} 상품 및 옵션 데이터를 삭제합니다...'))
        # ProductOption.objects.filter(product__product_type=product_type_code).delete()
        # FinancialProduct.objects.filter(product_type=product_type_code).delete()
        # self.stdout.write(self.style.SUCCESS(f'기존 {product_type_name} 데이터 삭제 완료.'))


        while current_page <= total_pages:
            params = {
                'auth': api_key,
                'topFinGrpNo': '020000', 
                'pageNo': str(current_page)
            }
            
            self.stdout.write(self.style.HTTP_INFO(f'{product_type_name} 데이터 요청 중... (Page: {current_page}/{total_pages})'))
            
            try:
                response = requests.get(api_url, params=params, timeout=10) # 타임아웃 추가
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.Timeout:
                self.stdout.write(self.style.ERROR(f'{product_type_name} API 호출 시간 초과 (Page: {current_page})'))
                # 재시도 로직을 추가하거나, 몇 번 실패 후 중단할 수 있습니다. 여기서는 단순 break.
                break
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'{product_type_name} API 호출 오류 (Page: {current_page}): {e}'))
                break
            except ValueError: 
                self.stdout.write(self.style.ERROR(f'{product_type_name} API 응답 JSON 파싱 오류 (Page: {current_page})'))
                self.stdout.write(self.style.NOTICE(f'받은 내용: {response.text[:200]}...'))
                break

            result = data.get('result')
            if not result:
                self.stdout.write(self.style.ERROR(f'{product_type_name} API 응답에 "result" 키가 없습니다.'))
                break

            if current_page == 1:
                try:
                    total_pages = int(result.get('max_page_no', 1))
                    if total_pages == 0 : total_pages = 1 # max_page_no가 0으로 오는 경우 방지
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(f'{product_type_name} API 응답에서 max_page_no를 읽을 수 없습니다. 1페이지만 처리합니다.'))
                    total_pages = 1
            
            base_list = result.get('baseList', [])
            option_list = result.get('optionList', [])

            if not base_list: # option_list는 base_list가 없으면 의미가 없을 수 있음
                self.stdout.write(self.style.WARNING(f'{product_type_name} baseList 데이터가 없습니다. (Page: {current_page})'))
                # 이 경우 다음 페이지로 넘어가지 않고, API 오류일 가능성을 고려해 중단할 수도 있습니다.
                # 여기서는 다음 페이지로 계속 진행합니다.
                if current_page < total_pages :
                    current_page += 1
                    continue
                else: # 마지막 페이지인데 데이터가 없으면 루프 종료
                    break


            for product_data in base_list:
                bank_code = product_data.get('fin_co_no')
                bank_name = product_data.get('kor_co_nm')
                fin_prdt_cd = product_data.get('fin_prdt_cd')
                dcls_month = product_data.get('dcls_month')

                if not all([bank_code, bank_name, fin_prdt_cd, dcls_month]):
                    self.stdout.write(self.style.WARNING(f'필수 은행/상품 정보 누락: {product_data.get("fin_prdt_nm", "이름 없는 상품")} ({fin_prdt_cd})'))
                    continue

                bank, _ = Bank.objects.update_or_create(
                    code=bank_code,
                    defaults={'name': bank_name}
                )

                product_defaults = {
                    'bank': bank,
                    'name': product_data.get('fin_prdt_nm'),
                    'product_type': product_type_code,
                    'join_way': product_data.get('join_way'),
                    'mtrt_int': product_data.get('mtrt_int'),
                    'spcl_cnd': product_data.get('spcl_cnd'),
                    'join_deny': product_data.get('join_deny'),
                    'join_member': product_data.get('join_member'),
                    'etc_note': product_data.get('etc_note'),
                    'max_limit': product_data.get('max_limit'), # 모델에서 BigIntegerField(null=True)이므로 None 허용
                    'dcls_strt_day': product_data.get('dcls_strt_day'),
                    'dcls_end_day': product_data.get('dcls_end_day'),
                    'fin_co_subm_day': product_data.get('fin_co_subm_day'),
                }
                # None이 아닌 값만 defaults에 포함 (모델 필드가 null=False인 경우 대비)
                product_defaults_cleaned = {k: v for k, v in product_defaults.items() if v is not None}
                
                try:
                    product_instance, created = FinancialProduct.objects.update_or_create(
                        fin_prdt_cd=fin_prdt_cd,
                        dcls_month=dcls_month,
                        defaults=product_defaults_cleaned
                    )
                    action_word = "생성" if created else "업데이트"
                    self.stdout.write(self.style.SUCCESS(f'상품 {action_word}: {product_instance.name} ({fin_prdt_cd})'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'상품 저장/업데이트 중 오류 ({product_data.get("fin_prdt_nm")}): {e}'))
                    continue
            
            # 옵션 처리
            product_cache = {p.fin_prdt_cd: p for p in FinancialProduct.objects.filter(dcls_month=dcls_month)}

            for option_data in option_list:
                opt_fin_prdt_cd = option_data.get('fin_prdt_cd')
                # optionList의 dcls_month는 baseList와 동일한 페이지의 것이므로, 해당 페이지의 dcls_month를 사용
                
                related_product = product_cache.get(opt_fin_prdt_cd)
                if not related_product:
                    self.stdout.write(self.style.WARNING(f'옵션에 해당하는 상품을 찾을 수 없음 (코드: {opt_fin_prdt_cd}, 공시월: {dcls_month})'))
                    continue

                try:
                    save_trm_str = option_data.get('save_trm')
                    if not save_trm_str: # 저축 기간이 없는 경우 건너뜀
                        self.stdout.write(self.style.WARNING(f'옵션 데이터에 저축 기간(save_trm) 누락: {option_data}, 상품: {related_product.name}'))
                        continue
                    save_trm_int = int(save_trm_str) # ★★★ 정수형으로 변환 ★★★
                except (ValueError, TypeError) as e:
                    self.stdout.write(self.style.WARNING(f'저축 기간(save_trm)을 정수로 변환 중 오류: {save_trm_str} ({e}), 옵션: {option_data}, 상품: {related_product.name}'))
                    continue

                intr_rate_val = option_data.get('intr_rate')
                intr_rate2_val = option_data.get('intr_rate2')
                
                try:
                    intr_rate = Decimal(intr_rate_val) if intr_rate_val is not None else None
                except (InvalidOperation, TypeError): intr_rate = None
                try:
                    intr_rate2 = Decimal(intr_rate2_val) if intr_rate2_val is not None else None
                except (InvalidOperation, TypeError): intr_rate2 = None

                option_key_fields = {
                    'product': related_product,
                    'save_trm': save_trm_int,
                    'intr_rate_type': option_data.get('intr_rate_type'),
                }
                # 적금(saving)일 경우에만 rsrv_type을 조회 조건에 포함 (unique_together 조건 때문)
                if related_product.product_type == FinancialProduct.SAVING:
                    option_key_fields['rsrv_type'] = option_data.get('rsrv_type')

                option_defaults = {
                    'intr_rate_type_nm': option_data.get('intr_rate_type_nm'),
                    'intr_rate': intr_rate,
                    'intr_rate2': intr_rate2,
                }
                # 적금(saving)일 경우에만 rsrv_type_nm을 defaults에 포함
                if related_product.product_type == FinancialProduct.SAVING:
                    option_defaults['rsrv_type_nm'] = option_data.get('rsrv_type_nm')
                
                option_defaults_cleaned = {k: v for k, v in option_defaults.items() if v is not None}

                try:
                    option_instance, created = ProductOption.objects.update_or_create(
                        **option_key_fields,
                        defaults=option_defaults_cleaned
                    )
                    action_word = "생성" if created else "업데이트"
                    self.stdout.write(f'  옵션 {action_word}: {option_instance}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'옵션 저장/업데이트 중 오류 ({related_product.name} - {save_trm_str}개월): {e}'))
                    self.stdout.write(self.style.NOTICE(f'옵션 키 필드: {option_key_fields}'))
                    self.stdout.write(self.style.NOTICE(f'옵션 기본값: {option_defaults_cleaned}'))


            current_page += 1
            if current_page > total_pages and total_pages > 0:
                 self.stdout.write(self.style.SUCCESS(f'{product_type_name} 데이터 처리 완료. 총 {total_pages} 페이지.'))
                 break # 명시적으로 루프 종료

    @transaction.atomic
    def handle(self, *args, **options):
        api_key = settings.FSS_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR('FSS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.'))
            return

        # (선택사항) 모든 관련 데이터 삭제 후 시작
        # ProductOption.objects.all().delete()
        # FinancialProduct.objects.all().delete()
        # Bank.objects.all().delete()
        # self.stdout.write(self.style.WARNING('기존 모든 금융상품 관련 데이터 삭제 완료.'))

        deposit_url = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
        self.fetch_and_save_data(FinancialProduct.DEPOSIT, "정기예금", deposit_url, api_key)
        
        self.stdout.write("\n" + "="*50 + "\n")

        saving_url = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
        self.fetch_and_save_data(FinancialProduct.SAVING, "적금", saving_url, api_key)

        self.stdout.write(self.style.SUCCESS('\n모든 금융상품 데이터 처리 완료!'))