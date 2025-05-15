import json
from django.shortcuts import render
from dashboard.utils import get_available_categories, get_equity_tickers_by_category, load_json_data
from datetime import datetime

# Required content per quarter/year
REQUIRED_CONTENT = {
    'Q1': ['quarterly_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
    'Q2': ['quarterly_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
    'Q3': ['quarterly_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
    'Q4': ['annual_report', 'earnings_presentation', 'earnings_transcript', 'earnings_press_release'],
}

def dashboard_view(request):
    selected_category = request.GET.get('category')
    selected_equity = request.GET.get('equity')

    categories = get_available_categories()
    equities = get_equity_tickers_by_category(selected_category) if selected_category else []

    documents = []
    missing_docs = {}
    current_year = datetime.now().year

    if selected_category and selected_equity:
        data = load_json_data(selected_category, selected_equity)
        if data and isinstance(data, list):
            filtered_data = [d for d in data if d.get('fiscal_year') is not None and d['fiscal_year'] >= 2006]
            present_docs = {}
            all_fiscal_years = set()

            for doc in filtered_data:
                fy = doc.get('fiscal_year')
                fq = str(doc.get('fiscal_quarter'))
                ct = doc.get('content_type')
                if fy and fq and ct:
                    key = (fy, fq)
                    present_docs.setdefault(key, set()).add(ct)
                    all_fiscal_years.add(fy)

            # Ensure complete missing doc detection
            synthetic_missing_docs = []
            if all_fiscal_years:
                min_year = min(all_fiscal_years)
                for year in range(min_year, current_year + 1):
                    for quarter in ['1', '2', '3', '4']:
                        required_types = set(REQUIRED_CONTENT.get(f"Q{quarter}", []))
                        present_types = present_docs.get((year, quarter), set())
                        missing_types = required_types - present_types
                        if missing_types:
                            for missing_type in missing_types:
                                missing_docs.setdefault((year, quarter), set()).add(missing_type)
                                synthetic_missing_docs.append({
                                    "equity_ticker": selected_equity,
                                    "geography": None,
                                    "content_name": None,
                                    "file_type": None,
                                    "content_type": missing_type,
                                    "published_date": None,
                                    "fiscal_date": None,
                                    "fiscal_year": year,
                                    "fiscal_quarter": quarter,
                                    "periodicity": "quarterly" if quarter in ['1', '2', '3'] else "annual",
                                    "is_missing": True,
                                    "link": None,
                                })

            # 🔧 Append actual + synthetic
            documents = filtered_data + synthetic_missing_docs
        else:
            documents = [{"error": "Error: JSON data is missing or not a list"}]

    return render(request, 'dashboard.html', {
        'categories': categories,
        'selected_category': selected_category,
        'equities': equities,
        'selected_equity': selected_equity,
        'documents': documents,
        'missing_docs': missing_docs,
    })
