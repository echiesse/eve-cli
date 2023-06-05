@echo off

echo Obtendo preço dos Itens ...
python evecli.py priceEstimate noheader system=Jita order-count=10 order-type=all resources\market.json retries=2 > market_prices.txt

echo Timestamp: %date% %time%
