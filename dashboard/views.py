from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_list_or_404
from .models import Document
import json
from django.contrib import messages
from datetime import datetime

# Create your views here.

def dashboard_view(request):
    documents = Document.objects.all().order_by('-published_date')  # descending order
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
                fiscal_date = datetime.strptime(item['fiscal_date'], '%Y-%m-%d').date()

                Document.objects.update_or_create(
                    equity_ticker=item['equity_ticker'],
                    content_type=item['content_type'],
                    fiscal_year=item['fiscal_year'],
                    fiscal_quarter=item.get('fiscal_quarter'),
                    defaults={
                        'geography': item.get('geography'),
                        'content_name': item.get('content_name'),
                        'file_type': item.get('file_type'),
                        'published_date': pub_date,
                        'fiscal_date': fiscal_date,
                        'periodicity': item.get('periodicity'),
                        'is_missing': item.get('is_missing', False),
                        'r2_url': item.get('r2_url')
                    }
                )
            messages.success(request, "JSON uploaded and data saved successfully.")
        except Exception as e:
            messages.error(request, f"Error processing JSON file: {e}")

        return redirect('dashboard')
    return redirect('dashboard')

@csrf_exempt
def delete_equity_documents(request, ticker):
    if request.method == "POST":
        try:
            # Delete all documents related to the ticker
            deleted_count, _ = Document.objects.filter(equity_ticker=ticker).delete()
            return JsonResponse({"status": "success", "deleted_count": deleted_count})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)