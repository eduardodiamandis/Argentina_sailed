import pandas as pd
import os
import datetime
import logging
import plotly.express as px
from latest_module import latest_file
# Caminho do banco
data_base = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Arg_sailed_database.xlsx')
# colunas
# ['Port', 'Terminal', 'Vessel', 'Status', 'Date', 'Tons', 'Cargo',
#        'Origin', 'Destination', 'Coordinator', 'Charterer', 'Month', 'Year'],
#       dtype='object')
df = pd.read_excel(data_base)
