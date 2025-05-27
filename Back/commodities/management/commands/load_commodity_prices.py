# Back/commodities/management/commands/load_commodity_prices.py
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from commodities.models import Commodity, PriceHistory

class Command(BaseCommand):
    help = 'Loads commodity prices from CSV files into the database'

    def handle(self, *args, **options):
        # Commodity 객체 가져오기 또는 생성
        gold, created_gold = Commodity.objects.get_or_create(
            name='Gold', 
            defaults={'symbol': 'GOLD', 'description': 'Gold Price History'}
        )
        if created_gold:
            self.stdout.write(self.style.SUCCESS(f'Successfully created Commodity: {gold.name}'))
        #else:
            #self.stdout.write(f'Commodity {gold.name} already exists.') # 이미 존재한다는 메시지는 불필요할 수 있음

        silver, created_silver = Commodity.objects.get_or_create(
            name='Silver', 
            defaults={'symbol': 'SILVER', 'description': 'Silver Price History'}
        )
        if created_silver:
            self.stdout.write(self.style.SUCCESS(f'Successfully created Commodity: {silver.name}'))
        #else:
            #self.stdout.write(f'Commodity {silver.name} already exists.')

        data_dir = os.path.join(settings.BASE_DIR, 'commodities', 'data')
        
        files_commodities = {
            'gold_prices.csv': gold,
            'silver_prices.csv': silver,
        }

        for filename, commodity_obj in files_commodities.items():
            file_path = os.path.join(data_dir, filename)
            self.stdout.write(f"Processing file: {file_path} for commodity: {commodity_obj.name}")

            if not os.path.exists(file_path):
                self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
                continue

            try:
                # ★★★ 수정된 부분: 기본 인코딩을 'utf-8'로 설정 ★★★
                # 파일을 UTF-8 (BOM 없음)으로 저장했다고 가정합니다.
                with open(file_path, mode='r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    loaded_count = 0
                    updated_count = 0
                    skipped_count = 0
                    
                    for row_number, row in enumerate(reader, 1):
                        date_str = row.get('Date')
                        price_str = row.get('Close/Last')

                        if not date_str or not price_str:
                            self.stdout.write(self.style.WARNING(f"Skipping row #{row_number} due to missing Date or Price: {row}"))
                            skipped_count += 1
                            continue
                        
                        try:
                            trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            price_val = Decimal(price_str.replace(',', ''))

                            price_history_obj, created = PriceHistory.objects.update_or_create(
                                commodity=commodity_obj,
                                date=trade_date,
                                defaults={'price': price_val}
                            )
                            if created:
                                loaded_count += 1
                            else:
                                updated_count += 1
                                
                        except ValueError as ve:
                            self.stdout.write(self.style.WARNING(f"Skipping row #{row_number} due to ValueError (e.g., date format): {row} - {ve}"))
                            skipped_count += 1
                        except InvalidOperation:
                            self.stdout.write(self.style.WARNING(f"Skipping row #{row_number} due to InvalidOperation (e.g., price format '{price_str}'): {row}"))
                            skipped_count += 1
                        except Exception as e_inner:
                            self.stderr.write(self.style.ERROR(f"An unexpected error occurred for row #{row_number} {row}: {e_inner}"))
                            skipped_count += 1
                            
                    self.stdout.write(self.style.SUCCESS(
                        f"Finished processing {filename} for {commodity_obj.name}. "
                        f"Loaded: {loaded_count}, Updated: {updated_count}, Skipped: {skipped_count}"
                    ))

            except FileNotFoundError:
                self.stderr.write(self.style.ERROR(f"Could not open file: {file_path}"))
            except UnicodeDecodeError as ude:
                self.stderr.write(self.style.ERROR(f"UnicodeDecodeError for file {file_path} with encoding 'utf-8'. Ensure the file is saved as UTF-8 without BOM. Error: {ude}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to process file {file_path}: {e}"))

        self.stdout.write(self.style.SUCCESS('Commodity price loading process finished.'))