from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_list_or_404
from .models import Document
import json
from django.contrib import messages
from datetime import datetime

# Create your views here.

from datetime import date
from django.shortcuts import render
from .models import Document

from datetime import date
from django.shortcuts import render
from .models import Document

def dashboard_view(request):
    # ✅ Include only documents published on or after 2006-01-01
    cutoff_date = date(2006, 1, 1)
    documents = Document.objects.filter(published_date__gte=cutoff_date).order_by('-published_date')

    # Get distinct tickers and content types from the filtered documents
    tickers = documents.values_list('equity_ticker', flat=True).distinct()
    content_types = documents.values_list('content_type', flat=True).distinct()

    # Required content per quarter/year
    required_content = {
        'Q1': ['quarterly_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
        'Q2': ['quarterly_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
        'Q3': ['quarterly_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
        'Q4': ['annual_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
    }

    # Build a dictionary keyed by (ticker, fiscal_year, fiscal_quarter) with content types present
    present_docs = {}
    fiscal_years = set()
    for doc in documents:
        key = (doc.equity_ticker, doc.fiscal_year, doc.fiscal_quarter)
        fiscal_years.add(doc.fiscal_year)
        present_docs.setdefault(key, set()).add(doc.content_type)

    # Build all possible expected keys
    all_possible_keys = set()
    for ticker in tickers:
        for year in fiscal_years:
            for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
                all_possible_keys.add((ticker, year, quarter))

    # Compute missing documents per (ticker, year, quarter)
    missing_docs = {}
    for key in all_possible_keys:
        ticker, year, quarter = key
        required = set(required_content.get(quarter, []))
        present = present_docs.get(key, set())
        missing = required - present
        if missing:
            missing_docs[key] = missing

    context = {
        'documents': documents,
        'tickers': tickers,
        'content_types': content_types,
        'missing_docs': missing_docs,
    }
    return render(request, 'dashboard.html', context)



@require_POST
def upload_json(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        try:
            data = json.load(json_file)
            for item in data:
                pub_date = datetime.strptime(item['published_date'], '%Y-%m-%d').date()
                fiscal_date = None
                if item.get('fiscal_date'):
                    fiscal_date = datetime.strptime(item['fiscal_date'], '%Y-%m-%d').date()

                # Determine uniqueness conditionally
                if item.get('periodicity') == 'periodic':
                    lookup = {
                        'equity_ticker': item['equity_ticker'],
                        'content_type': item['content_type'],
                        'content_name': item.get('content_name'),
                        'fiscal_year': item['fiscal_year'],
                        'fiscal_quarter': item.get('fiscal_quarter'),
                    }
                else:  # non-periodic
                    # Use content_name and published_date to uniquely identify
                    lookup = {
                        'equity_ticker': item['equity_ticker'],
                        'content_type': item['content_type'],
                        'content_name': item.get('content_name'),
                        'published_date': pub_date,
                    }

                Document.objects.update_or_create(
                    **lookup,
                    defaults={
                        'published_date': pub_date,
                        'geography': item.get('geography'),
                        'file_type': item.get('file_type'),
                        'fiscal_date': fiscal_date,
                        'fiscal_year': item.get('fiscal_year'),  # can be None
                        'fiscal_quarter': item.get('fiscal_quarter'),
                        'periodicity': item.get('periodicity'),
                        'is_missing': item.get('is_missing', False),
                        'r2_url': item.get('r2_url')
                    }
                )
                print(f"Processed item: {item['equity_ticker']} - {item['content_type']} ({item['fiscal_year']})")
            messages.success(request, "JSON uploaded and data saved successfully.")
        except Exception as e:
            print(f"Error processing JSON file: {e}")
            messages.error(request, f"Error processing JSON file: {e}")
        print("Redirecting to dashboard after upload...")
        return redirect('dashboard')
    print("No file uploaded or invalid request method.")
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