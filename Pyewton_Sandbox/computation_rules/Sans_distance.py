#Code g�n�r� automatiquement � partir du script 'generate_computation_file.py'

from Body import Body
from decimal import Decimal

def computeNorme(a:Body, b:Body):
  return a.masse * b.masse