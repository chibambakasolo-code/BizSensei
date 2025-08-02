from flask import render_template, request, jsonify, redirect, url_for, flash, send_file
from app import app
from data_manager import data_manager
from datetime import datetime, timedelta
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

@app.route('/')
def index():
    """Dashboard home page"""
    # Check if business setup is completed
    if not data_manager.is_setup_completed():
        return redirect(url_for('business_setup'))
    
    # Get today's summary
    today_summary = data_manager.get_daily_summary()
    
    # Get recent sales (last 5)
    recent_sales = sorted(data_manager.sales, key=lambda x: x['sale_date'], reverse=True)[:5]
    
    # Get active alerts
    alerts = data_manager.get_active_alerts()
    
    # Get low stock items
    inventory_status = data_manager.get_inventory_status()
    low_stock_items = [item for item in inventory_status if item['is_low_stock']][:5]
    
    # Get quick analytics
    analytics = data_manager.get_sales_analytics(7)  # Last 7 days
    
    return render_template('index.html',
                         today_summary=today_summary,
                         recent_sales=recent_sales,
                         alerts=alerts,
                         low_stock_items=low_stock_items,
                         analytics=analytics)

@app.route('/setup')
def business_setup():
    """Business setup page"""
    business_types = data_manager.get_business_types()
    return render_template('setup.html', business_types=business_types)

@app.route('/setup', methods=['POST'])
def setup_business():
    """Handle business setup form submission"""
    try:
        business_name = request.form.get('business_name', '').strip()
        business_type = request.form.get('business_type', '').strip()
        
        if not business_name or not business_type:
            flash('Please provide both business name and type', 'error')
            return redirect(url_for('business_setup'))
        
        success = data_manager.setup_business(business_name, business_type)
        
        if success:
            flash(f'Welcome to {business_name}! Your business is now set up.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to setup business. Please try again.', 'error')
            return redirect(url_for('business_setup'))
            
    except Exception as e:
        print(f"Business setup error: {e}")
        flash('An error occurred during setup. Please try again.', 'error')
        return redirect(url_for('business_setup'))

@app.route('/catalog')
def catalog():
    """Item catalog page"""
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')
    
    items = data_manager.items
    
    # Filter by search query
    if search_query:
        items = data_manager.search_items(search_query)
    
    # Filter by category
    if category:
        items = [item for item in items if item['category'] == category]
    
    # Only show active items
    items = [item for item in items if item['active']]
    
    return render_template('catalog.html',
                         items=items,
                         categories=data_manager.item_categories,
                         search_query=search_query,
                         selected_category=category)

@app.route('/catalog/bulk-add')
def bulk_add_items():
    """Bulk add items page"""
    return render_template('bulk_add_items.html',
                         categories=data_manager.item_categories)

@app.route('/catalog/bulk-add', methods=['POST'])
def process_bulk_add():
    """Process bulk add items form"""
    try:
        items_data = []
        added_count = 0
        error_count = 0
        errors = []
        
        # Parse form data
        form_data = request.form.to_dict()
        
        # Group by item index
        items_dict = {}
        for key, value in form_data.items():
            if key.startswith('items[') and value.strip():
                # Extract index and field name
                import re
                match = re.match(r'items\[(\d+)\]\[(\w+)\]', key)
                if match:
                    index = int(match.group(1))
                    field = match.group(2)
                    
                    if index not in items_dict:
                        items_dict[index] = {}
                    items_dict[index][field] = value.strip()
        
        # Process each item
        for index, item_data in items_dict.items():
            try:
                # Check if required fields are present
                if not all(field in item_data and item_data[field] for field in ['name', 'category', 'cost_price', 'selling_price']):
                    continue  # Skip incomplete rows
                
                name = item_data['name']
                category = item_data['category']
                cost_price = float(item_data['cost_price'])
                selling_price = float(item_data['selling_price'])
                initial_stock = int(item_data.get('initial_stock', 0))
                
                # Validate data
                if cost_price < 0:
                    errors.append(f"Row {index + 1}: Cost price cannot be negative")
                    error_count += 1
                    continue
                
                if selling_price <= 0:
                    errors.append(f"Row {index + 1}: Selling price must be positive")
                    error_count += 1
                    continue
                
                if selling_price <= cost_price:
                    errors.append(f"Row {index + 1}: Selling price should be higher than cost price")
                    error_count += 1
                    continue
                
                if initial_stock < 0:
                    errors.append(f"Row {index + 1}: Initial stock cannot be negative")
                    error_count += 1
                    continue
                
                # Add the item
                item = data_manager.add_item(name, category, cost_price, selling_price, initial_stock)
                if item:
                    added_count += 1
                else:
                    errors.append(f"Row {index + 1}: Failed to add item '{name}'")
                    error_count += 1
                    
            except ValueError as e:
                errors.append(f"Row {index + 1}: Invalid number format - {str(e)}")
                error_count += 1
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                error_count += 1
        
        # Show results
        if added_count > 0:
            flash(f'Successfully added {added_count} items to your catalog!', 'success')
        
        if error_count > 0:
            flash(f'{error_count} items had errors and were not added.', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(error, 'error')
            
            if len(errors) > 5:
                flash(f'... and {len(errors) - 5} more errors', 'error')
        
        if added_count == 0 and error_count == 0:
            flash('No items were processed. Please fill in at least one complete row.', 'warning')
        
        # Redirect based on results
        if added_count > 0:
            return redirect(url_for('catalog'))
        else:
            return redirect(url_for('bulk_add_items'))
            
    except Exception as e:
        flash(f'Error processing bulk add: {str(e)}', 'error')
        return redirect(url_for('bulk_add_items'))

@app.route('/catalog/add', methods=['POST'])
def add_item():
    """Add new item to catalog"""
    try:
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        cost_price = float(request.form.get('cost_price', 0))
        selling_price = float(request.form.get('selling_price', 0))
        initial_stock = int(request.form.get('initial_stock', 0))
        
        if not name or not category:
            raise ValueError("Name and category are required")
        
        if cost_price < 0 or selling_price < 0:
            raise ValueError("Prices cannot be negative")
        
        item = data_manager.add_item(name, category, cost_price, selling_price, initial_stock)
        flash(f'Successfully added "{item["name"]}" to catalog', 'success')
        
    except ValueError as e:
        flash(f'Error adding item: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('catalog'))

@app.route('/api/search-suggestions')
def search_suggestions():
    """API endpoint for search suggestions"""
    query = request.args.get('q', '')
    suggestions = data_manager.get_item_suggestions(query)
    return jsonify(suggestions)

@app.route('/sales')
def sales():
    """Sales management page"""
    # Get recent sales
    recent_sales = sorted(data_manager.sales, key=lambda x: x['sale_date'], reverse=True)[:20]
    
    # Get items for dropdown
    items = [item for item in data_manager.items if item['active']]
    
    return render_template('sales.html',
                         recent_sales=recent_sales,
                         items=items)

@app.route('/sales/add', methods=['POST'])
def add_sale():
    """Add new sale"""
    try:
        # Check if it's a smart input or regular form
        smart_input = request.form.get('smart_input', '').strip()
        
        if smart_input:
            # Parse smart input
            parsed = data_manager.parse_sale_input(smart_input)
            
            # Find matching item
            matching_items = data_manager.search_items(parsed['item_name'])
            if not matching_items:
                raise ValueError(f"No item found matching '{parsed['item_name']}'")
            
            item = matching_items[0]  # Use best match
            quantity = parsed['quantity']
            sale_price = parsed['price']
            notes = f"Smart input: {smart_input}"
            
        else:
            # Regular form input
            item_id = int(request.form.get('item_id', 0))
            quantity = int(request.form.get('quantity', 1))
            sale_price = float(request.form.get('sale_price', 0))
            notes = request.form.get('notes', '').strip()
            
            item = data_manager.get_item_by_id(item_id)
            if not item:
                raise ValueError("Item not found")
        
        # Validate inputs
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if sale_price <= 0:
            raise ValueError("Sale price must be positive")
        
        # Add the sale
        sale = data_manager.add_sale(item['id'], quantity, sale_price, notes)
        flash(f'Sale recorded: {quantity}x {item["name"]} for {data_manager.settings["currency"]}{sale_price:.2f}', 'success')
        
    except ValueError as e:
        flash(f'Error recording sale: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('sales'))

@app.route('/inventory')
def inventory():
    """Inventory management page"""
    # Get inventory status
    inventory_status = data_manager.get_inventory_status()
    
    # Sort by low stock first
    inventory_status.sort(key=lambda x: (not x['is_low_stock'], x['quantity']))
    
    # Get restock suggestions
    restock_suggestions = data_manager.get_restock_suggestions()
    
    return render_template('inventory.html',
                         inventory_status=inventory_status,
                         restock_suggestions=restock_suggestions,
                         low_stock_threshold=data_manager.settings['low_stock_threshold'])

@app.route('/inventory/update', methods=['POST'])
def update_inventory():
    """Update inventory quantity"""
    try:
        item_id = int(request.form.get('item_id', 0))
        quantity = int(request.form.get('quantity', 0))
        operation = request.form.get('operation', 'add')
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        updated = data_manager.update_inventory(item_id, quantity, operation)
        item = data_manager.get_item_by_id(item_id)
        
        operation_text = {
            'add': 'Added',
            'subtract': 'Removed',
            'set': 'Set to'
        }.get(operation, 'Updated')
        
        flash(f'{operation_text} {quantity} units for {item["name"]}. New stock: {updated["quantity"]}', 'success')
        
    except ValueError as e:
        flash(f'Error updating inventory: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('inventory'))

@app.route('/reports')
def reports():
    """Reports and analytics page"""
    # Get analytics for different periods
    analytics_7d = data_manager.get_sales_analytics(7)
    analytics_30d = data_manager.get_sales_analytics(30)
    analytics_90d = data_manager.get_sales_analytics(90)
    
    return render_template('reports.html',
                         analytics_7d=analytics_7d,
                         analytics_30d=analytics_30d,
                         analytics_90d=analytics_90d)

@app.route('/analytics')
def analytics():
    """Analytics dashboard with charts"""
    period = request.args.get('period', '30')
    try:
        period_days = int(period)
    except ValueError:
        period_days = 30
    
    analytics = data_manager.get_sales_analytics(period_days)
    inventory_status = data_manager.get_inventory_status()
    
    return render_template('analytics.html',
                         analytics=analytics,
                         inventory_status=inventory_status,
                         period=period_days)

@app.route('/api/analytics-data')
def analytics_data():
    """API endpoint for chart data"""
    period = request.args.get('period', '30')
    chart_type = request.args.get('type', 'sales')
    
    try:
        period_days = int(period)
    except ValueError:
        period_days = 30
    
    analytics = data_manager.get_sales_analytics(period_days)
    
    if chart_type == 'sales':
        # Sales by day chart data
        data = {
            'labels': [item['date'] for item in analytics['sales_by_day']],
            'datasets': [{
                'label': 'Daily Revenue',
                'data': [item['revenue'] for item in analytics['sales_by_day']],
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }]
        }
    elif chart_type == 'top_items':
        # Top items chart data
        top_items = analytics['top_items'][:10]
        data = {
            'labels': [item['item_name'] for item in top_items],
            'datasets': [{
                'label': 'Revenue',
                'data': [item['revenue'] for item in top_items],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 205, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(199, 199, 199, 0.5)',
                    'rgba(83, 102, 255, 0.5)',
                    'rgba(255, 99, 255, 0.5)',
                    'rgba(99, 255, 132, 0.5)'
                ]
            }]
        }
    else:
        data = {'labels': [], 'datasets': []}
    
    return jsonify(data)

@app.route('/export/sales-csv')
def export_sales_csv():
    """Export sales data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Sale ID', 'Date', 'Item Name', 'Quantity', 'Unit Price', 'Total Amount', 'Profit', 'Notes'])
    
    # Write sales data
    for sale in sorted(data_manager.sales, key=lambda x: x['sale_date'], reverse=True):
        writer.writerow([
            sale['id'],
            datetime.fromisoformat(sale['sale_date']).strftime('%Y-%m-%d %H:%M'),
            sale['item_name'],
            sale['quantity'],
            f"{data_manager.settings['currency']}{sale['unit_price']:.2f}",
            f"{data_manager.settings['currency']}{sale['total_amount']:.2f}",
            f"{data_manager.settings['currency']}{sale['profit']:.2f}",
            sale['notes']
        ])
    
    output.seek(0)
    
    # Create file-like object for sending
    mem_file = io.BytesIO()
    mem_file.write(output.getvalue().encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        as_attachment=True,
        download_name=f'sales_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

@app.route('/export/inventory-csv')
def export_inventory_csv():
    """Export inventory data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Item Name', 'Category', 'Current Stock', 'Cost Price', 'Selling Price', 'Total Value', 'Status'])
    
    # Write inventory data
    inventory_status = data_manager.get_inventory_status()
    for item_info in inventory_status:
        item = item_info['item']
        status = 'Low Stock' if item_info['is_low_stock'] else 'Normal'
        
        writer.writerow([
            item['name'],
            item['category'],
            item_info['quantity'],
            f"{data_manager.settings['currency']}{item['cost_price']:.2f}",
            f"{data_manager.settings['currency']}{item['selling_price']:.2f}",
            f"{data_manager.settings['currency']}{item_info['total_value']:.2f}",
            status
        ])
    
    output.seek(0)
    
    # Create file-like object for sending
    mem_file = io.BytesIO()
    mem_file.write(output.getvalue().encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        as_attachment=True,
        download_name=f'inventory_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

@app.route('/export/report-pdf')
def export_report_pdf():
    """Export analytics report as PDF"""
    period = request.args.get('period', '30')
    try:
        period_days = int(period)
    except ValueError:
        period_days = 30
    
    analytics = data_manager.get_sales_analytics(period_days)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    story = []
    
    # Title
    story.append(Paragraph(f"Sales Report - Last {period_days} Days", title_style))
    story.append(Spacer(1, 20))
    
    # Summary table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Sales', str(analytics['total_sales'])],
        ['Total Revenue', f"{data_manager.settings['currency']}{analytics['total_revenue']:.2f}"],
        ['Total Profit', f"{data_manager.settings['currency']}{analytics['total_profit']:.2f}"],
        ['Average Sale', f"{data_manager.settings['currency']}{analytics['average_sale']:.2f}"],
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Top selling items
    if analytics['top_items']:
        story.append(Paragraph("Top Selling Items", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        top_items_data = [['Item Name', 'Quantity Sold', 'Revenue', 'Profit']]
        for item in analytics['top_items'][:10]:
            top_items_data.append([
                item['item_name'],
                str(item['quantity']),
                f"{data_manager.settings['currency']}{item['revenue']:.2f}",
                f"{data_manager.settings['currency']}{item['profit']:.2f}"
            ])
        
        top_items_table = Table(top_items_data)
        top_items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(top_items_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'sales_report_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@app.route('/api/dismiss-alert', methods=['POST'])
def dismiss_alert():
    """Dismiss an alert"""
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
        
        alert_id = int(request_data.get('alert_id', 0))
        data_manager.dismiss_alert(alert_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page"""
    if request.method == 'POST':
        try:
            threshold = int(request.form.get('low_stock_threshold', 5))
            currency = request.form.get('currency', 'K').strip()
            
            if threshold < 0:
                raise ValueError("Threshold cannot be negative")
            
            data_manager.settings['low_stock_threshold'] = threshold
            data_manager.settings['currency'] = currency
            
            flash('Settings updated successfully', 'success')
            
        except ValueError as e:
            flash(f'Error updating settings: {str(e)}', 'error')
    
    return render_template('settings.html', settings=data_manager.settings)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
