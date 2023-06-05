import subprocess

print('--------------------------------------------------------------------------------')
print("Materiais")
subprocess.run(['python', 'eveMarket.py', 'priceEstimate', 'system=Jita', 'resources\materials.json'])

print()
print('--------------------------------------------------------------------------------')
print("Modulos e Rigs")
subprocess.run(['python', 'eveMarket.py', 'priceEstimate', 'system=Jita', 'order-count=10', 'resources\modules.json'])
