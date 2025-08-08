from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AlgorithmExecution, MT5Account
from .serializers import (
    MT5AccountSerializer, 
    MT5AccountConnectionSerializer,
    MT5AccountStatusSerializer,
    AlgorithmExecutionSerializer
)
from .mt5_service import MT5ConnectionManager, MT5AlgorithmManager
import logging
import MetaTrader5 as mt5
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# Removed redundant code since the APIs are now imported from separate files.
# The file now only contains imports and no direct API implementations.