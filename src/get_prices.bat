@echo off

setlocal

set system=Jita

echo Obtendo preço dos Itens ...
python evecli.py priceEstimate noheader ^
    system=%system% ^
    order-count=10 ^
    order-type=all ^
    retries=2 ^
    resources\tracked_items.json > prices.txt

set _date=%date%
set _time=%time%
set timestamp=%date%_%_time%

echo Timestamp: %_date% %_time%

rem echo prices.txt price_history\prices_%system%_%timestamp%.txt

endlocal