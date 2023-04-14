#Code généré automatiquement à partir du script 'generate_computation_file.py'

from Body import Body
from decimal import Decimal

def computeNorme(a:Body, b:Body):
  return Decimal('6.6743e-11') * a.masse * b.masse / (((a.pos_x - b.pos_x) ** 2) + ((a.pos_y - b.pos_y) ** 2 ))