@echo off
rem python get_industry_prices.py

echo Obtendo preço de Materiais ...
python evecli.py priceEstimate noheader system=Jita resources\materials.json retries=2 > material_prices.txt

echo Obtendo preço de Modulos e Rigs ...
python evecli.py priceEstimate noheader system=Jita order-count=10 resources\modules.json retries=2 > module_prices.txt

echo Timestamp: %date% %time%
