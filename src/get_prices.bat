@echo off

echo Obtendo preço dos Itens ...
python evecli.py priceEstimate noheader ^
    system=Jita ^
    order-count=10 ^
    order-type=all ^
    retries=2 ^
    resources\tracked_items.json > prices.txt

echo Timestamp: %date% %time%
