from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Document
import json
from django.contrib import messages
from datetime import datetime

# Create your views here.
def dashboard_view(request):
    documents = Document.objects.all()

    # For filters:
    tickers = Document.objects.values_list('equity_ticker', flat=True).distinct()
    content_types = Document.objects.values_list('content_type', flat=True).distinct()

    context = {
        'documents': documents,
        'tickers': tickers,
        'content_types': content_types,
    }
    return render(request, 'dashboard.html', context)

def upload_json(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        try:
            data = json.load(json_file)
            # No deletion here; update or create documents
            for item in data:
                pub_date = datetime.strptime(item['published_date'], '%Y-%m-%d').date()

                Document.objects.update_or_create(
                    equity_ticker=item['equity_ticker'],
                    content_type=item['content_type'],
                    fiscal_year=item['fiscal_year'],
                    fiscal_quarter=item.get('fiscal_quarter'),
                    defaults={
                        'published_date': pub_date,
                        'is_missing': item.get('is_missing', False),
                        'r2_url': item.get('r2_url')
                    }
                )
            messages.success(request, "JSON uploaded and data saved successfully.")
        except Exception as e:
            messages.error(request, f"Error processing JSON file: {e}")

        return redirect('dashboard')
    return redirect('dashboard')
