import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class DataManager:
    def _get_default_categories(self):
        """Get default generic categories"""
        return [
            'General',
            'Other'
        ]
    
    def _get_business_categories(self, business_type: str) -> List[str]:
        """Get categories based on business type"""
        business_category_map = {
            'grocery': [
                'Fruits & Vegetables',
                'Dairy & Eggs',
                'Meat & Poultry',
                'Beverages',
                'Snacks & Confectionery',
                'Canned & Packaged Foods',
                'Spices & Condiments',
                'Bread & Bakery',
                'Household Items',
                'Personal Care',
                'Other'
            ],
            'electronics': [
                'Mobile Phones & Accessories',
                'Computers & Laptops',
                'Audio & Video',
                'Gaming',
                'Home Appliances',
                'Cables & Chargers',
                'Storage Devices',
                'Cameras & Photography',
                'Electronic Components',
                'Batteries & Power',
                'Other'
            ],
            'hair_salon': [
                'Hair Care Products',
                'Hair Styling Tools',
                'Hair Color & Dyes',
                'Hair Extensions',
                'Salon Equipment',
                'Beauty Accessories',
                'Skin Care',
                'Nail Care',
                'Professional Tools',
                'Salon Supplies',
                'Other'
            ],
            'tailoring': [
                'Fabrics',
                'Threads & Yarns',
                'Buttons & Fasteners',
                'Zippers',
                'Sewing Tools',
                'Measuring Tools',
                'Patterns',
                'Embellishments',
                'Interfacing',
                'Sewing Machine Parts',
                'Other'
            ],
            'pharmacy': [
                'Prescription Medicines',
                'Over-the-Counter Medicines',
                'Vitamins & Supplements',
                'Personal Care',
                'Baby Care',
                'First Aid',
                'Medical Devices',
                'Health Monitoring',
                'Herbal Products',
                'Beauty & Cosmetics',
                'Other'
            ],
            'restaurant': [
                'Appetizers',
                'Main Courses',
                'Beverages',
                'Desserts',
                'Snacks',
                'Breakfast Items',
                'Lunch Specials',
                'Dinner Specials',
                'Vegetarian',
                'Take Away',
                'Other'
            ],
            'bookstore': [
                'Fiction',
                'Non-Fiction',
                'Educational',
                'Children\'s Books',
                'Stationery',
                'Office Supplies',
                'Art Supplies',
                'Magazines',
                'Religious Books',
                'Reference Books',
                'Other'
            ],
            'clothing': [
                'Men\'s Clothing',
                'Women\'s Clothing',
                'Children\'s Clothing',
                'Shoes',
                'Accessories',
                'Bags & Purses',
                'Jewelry',
                'Undergarments',
                'Sportswear',
                'Traditional Wear',
                'Other'
            ],
            'auto_parts': [
                'Engine Parts',
                'Brake Parts',
                'Electrical Components',
                'Body Parts',
                'Filters',
                'Oils & Fluids',
                'Tires & Wheels',
                'Accessories',
                'Tools',
                'Car Care Products',
                'Other'
            ],
            'bakery': [
                'Bread & Rolls',
                'Cakes & Cupcakes',
                'Pastries',
                'Cookies & Biscuits',
                'Pies & Tarts',
                'Baking Ingredients',
                'Decorating Supplies',
                'Seasonal Items',
                'Custom Orders',
                'Beverages',
                'Other'
            ],
            'hardware': [
                'Hand Tools',
                'Power Tools',
                'Fasteners',
                'Electrical Supplies',
                'Plumbing Supplies',
                'Paint & Finishes',
                'Building Materials',
                'Safety Equipment',
                'Garden Tools',
                'Hardware Accessories',
                'Other'
            ],
            'jewelry': [
                'Rings',
                'Necklaces',
                'Earrings',
                'Bracelets',
                'Watches',
                'Precious Metals',
                'Gemstones',
                'Custom Jewelry',
                'Repair Services',
                'Accessories',
                'Other'
            ],
            'sports': [
                'Football Equipment',
                'Basketball Equipment',
                'Tennis Equipment',
                'Fitness Equipment',
                'Athletic Wear',
                'Sports Shoes',
                'Outdoor Gear',
                'Team Sports',
                'Individual Sports',
                'Accessories',
                'Other'
            ],
            'pet_store': [
                'Dog Supplies',
                'Cat Supplies',
                'Bird Supplies',
                'Fish & Aquarium',
                'Small Animals',
                'Pet Food',
                'Toys & Treats',
                'Health & Medicine',
                'Grooming Supplies',
                'Accessories',
                'Other'
            ],
            'flower_shop': [
                'Fresh Flowers',
                'Potted Plants',
                'Seeds & Bulbs',
                'Garden Tools',
                'Fertilizers',
                'Pots & Planters',
                'Floral Arrangements',
                'Wedding Flowers',
                'Funeral Flowers',
                'Decorative Items',
                'Other'
            ],
            'office_supplies': [
                'Writing Instruments',
                'Paper Products',
                'Filing & Storage',
                'Desktop Accessories',
                'Technology',
                'Furniture',
                'Printing Supplies',
                'Presentation Materials',
                'Binding & Laminating',
                'Office Machines',
                'Other'
            ],
            'cosmetics': [
                'Facial Care',
                'Body Care',
                'Hair Care',
                'Makeup',
                'Perfumes',
                'Nail Care',
                'Men\'s Grooming',
                'Tools & Accessories',
                'Gift Sets',
                'Natural Products',
                'Other'
            ],
            'toy_store': [
                'Action Figures',
                'Dolls & Accessories',
                'Educational Toys',
                'Board Games',
                'Electronic Toys',
                'Outdoor Toys',
                'Arts & Crafts',
                'Puzzles',
                'Baby Toys',
                'Remote Control',
                'Other'
            ],
            'mobile_shop': [
                'Smartphones',
                'Feature Phones',
                'Cases & Covers',
                'Screen Protectors',
                'Chargers & Cables',
                'Headphones',
                'Memory Cards',
                'Power Banks',
                'Repair Parts',
                'Accessories',
                'Other'
            ],
            'furniture': [
                'Living Room',
                'Bedroom',
                'Dining Room',
                'Office Furniture',
                'Storage Solutions',
                'Outdoor Furniture',
                'Mattresses',
                'Home Decor',
                'Lighting',
                'Kitchen Furniture',
                'Other'
            ],
            'general_store': [
                'Food Items',
                'Beverages',
                'Household Items',
                'Personal Care',
                'Stationery',
                'Electronics',
                'Clothing',
                'Tools',
                'Seasonal Items',
                'Miscellaneous',
                'Other'
            ]
        }
        
        return business_category_map.get(business_type.lower(), self._get_default_categories())
    
    def __init__(self):
        self.items = []
        self.sales = []
        self.inventory = {}
        self.alerts = []
        self.settings = {
            'low_stock_threshold': 5,
            'currency': 'K',  # Kwacha
            'business_type': None,
            'business_name': None,
            'setup_completed': False
        }
        self.business_categories = self._get_default_categories()
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with some basic item categories - no sample data"""
        self.item_categories = self.business_categories.copy()
    
    def add_item(self, name: str, category: str, cost_price: float, selling_price: float, initial_stock: int = 0) -> Dict:
        """Add a new item to the catalog"""
        item_id = len(self.items) + 1
        item = {
            'id': item_id,
            'name': name.strip().title(),
            'category': category,
            'cost_price': float(cost_price),
            'selling_price': float(selling_price),
            'created_date': datetime.now().isoformat(),
            'active': True
        }
        self.items.append(item)
        
        # Initialize inventory
        self.inventory[item_id] = {
            'quantity': initial_stock,
            'last_updated': datetime.now().isoformat()
        }
        
        return item
    
    def search_items(self, query: str) -> List[Dict]:
        """Search items by name with suggestions"""
        if not query:
            return self.items[:10]  # Return first 10 items if no query
        
        query = query.lower().strip()
        exact_matches = []
        partial_matches = []
        
        for item in self.items:
            if not item['active']:
                continue
                
            item_name = item['name'].lower()
            if query == item_name:
                exact_matches.append(item)
            elif query in item_name:
                partial_matches.append(item)
        
        # Return exact matches first, then partial matches
        results = exact_matches + partial_matches
        return results[:20]  # Limit to 20 results
    
    def get_item_suggestions(self, query: str) -> List[str]:
        """Get item name suggestions for autocomplete"""
        if not query or len(query) < 2:
            return []
        
        query = query.lower().strip()
        suggestions = []
        
        for item in self.items:
            if not item['active']:
                continue
            
            item_name = item['name'].lower()
            if query in item_name and item['name'] not in suggestions:
                suggestions.append(item['name'])
        
        return suggestions[:10]
    
    def add_sale(self, item_id: int, quantity: int, sale_price: float, notes: str = '') -> Dict:
        """Record a sale"""
        item = self.get_item_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        
        # Check inventory
        current_stock = self.inventory.get(item_id, {}).get('quantity', 0)
        if current_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {current_stock}")
        
        sale_id = len(self.sales) + 1
        sale = {
            'id': sale_id,
            'item_id': item_id,
            'item_name': item['name'],
            'quantity': quantity,
            'unit_price': float(sale_price),
            'total_amount': float(sale_price * quantity),
            'cost_price': item['cost_price'],
            'profit': float((sale_price - item['cost_price']) * quantity),
            'sale_date': datetime.now().isoformat(),
            'notes': notes.strip()
        }
        
        self.sales.append(sale)
        
        # Update inventory
        self.inventory[item_id]['quantity'] -= quantity
        self.inventory[item_id]['last_updated'] = datetime.now().isoformat()
        
        # Check for low stock alert
        self._check_low_stock_alert(item_id)
        
        return sale
    
    def update_inventory(self, item_id: int, quantity: int, operation: str = 'add') -> Dict:
        """Update inventory quantity"""
        if item_id not in self.inventory:
            self.inventory[item_id] = {'quantity': 0, 'last_updated': datetime.now().isoformat()}
        
        if operation == 'add':
            self.inventory[item_id]['quantity'] += quantity
        elif operation == 'set':
            self.inventory[item_id]['quantity'] = quantity
        elif operation == 'subtract':
            self.inventory[item_id]['quantity'] = max(0, self.inventory[item_id]['quantity'] - quantity)
        
        self.inventory[item_id]['last_updated'] = datetime.now().isoformat()
        
        # Check for low stock alert
        self._check_low_stock_alert(item_id)
        
        return self.inventory[item_id]
    
    def get_item_by_id(self, item_id: int) -> Dict:
        """Get item by ID"""
        for item in self.items:
            if item['id'] == item_id:
                return item
        return None
    
    def get_inventory_status(self) -> List[Dict]:
        """Get current inventory status with item details"""
        inventory_status = []
        
        for item in self.items:
            if not item['active']:
                continue
                
            item_id = item['id']
            stock_info = self.inventory.get(item_id, {'quantity': 0, 'last_updated': datetime.now().isoformat()})
            
            status = {
                'item': item,
                'quantity': stock_info['quantity'],
                'last_updated': stock_info['last_updated'],
                'is_low_stock': stock_info['quantity'] <= self.settings['low_stock_threshold'],
                'total_value': item['selling_price'] * stock_info['quantity']
            }
            inventory_status.append(status)
        
        return inventory_status
    
    def _check_low_stock_alert(self, item_id: int):
        """Check and create low stock alert if needed"""
        item = self.get_item_by_id(item_id)
        stock = self.inventory.get(item_id, {}).get('quantity', 0)
        
        if stock <= self.settings['low_stock_threshold']:
            # Check if alert already exists
            existing_alert = any(
                alert['type'] == 'low_stock' and alert['item_id'] == item_id and alert['active']
                for alert in self.alerts
            )
            
            if not existing_alert:
                alert = {
                    'id': len(self.alerts) + 1,
                    'type': 'low_stock',
                    'item_id': item_id,
                    'item_name': item['name'],
                    'message': f"Low stock alert: {item['name']} has only {stock} units remaining",
                    'created_date': datetime.now().isoformat(),
                    'active': True
                }
                self.alerts.append(alert)
    
    def get_sales_analytics(self, days: int = 30) -> Dict:
        """Get sales analytics for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_sales = [
            sale for sale in self.sales 
            if datetime.fromisoformat(sale['sale_date']) >= cutoff_date
        ]
        
        if not recent_sales:
            return {
                'total_sales': 0,
                'total_revenue': 0,
                'total_profit': 0,
                'top_items': [],
                'sales_by_day': [],
                'category_performance': []
            }
        
        # Calculate totals
        total_revenue = sum(sale['total_amount'] for sale in recent_sales)
        total_profit = sum(sale['profit'] for sale in recent_sales)
        total_quantity = sum(sale['quantity'] for sale in recent_sales)
        
        # Top selling items
        item_sales = {}
        for sale in recent_sales:
            item_id = sale['item_id']
            if item_id not in item_sales:
                item_sales[item_id] = {
                    'item_name': sale['item_name'],
                    'quantity': 0,
                    'revenue': 0,
                    'profit': 0
                }
            item_sales[item_id]['quantity'] += sale['quantity']
            item_sales[item_id]['revenue'] += sale['total_amount']
            item_sales[item_id]['profit'] += sale['profit']
        
        top_items = sorted(item_sales.values(), key=lambda x: x['revenue'], reverse=True)[:10]
        
        # Sales by day
        daily_sales = {}
        for sale in recent_sales:
            date = datetime.fromisoformat(sale['sale_date']).date().isoformat()
            if date not in daily_sales:
                daily_sales[date] = {'revenue': 0, 'quantity': 0}
            daily_sales[date]['revenue'] += sale['total_amount']
            daily_sales[date]['quantity'] += sale['quantity']
        
        sales_by_day = [
            {'date': date, **data}
            for date, data in sorted(daily_sales.items())
        ]
        
        return {
            'total_sales': len(recent_sales),
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'total_quantity': total_quantity,
            'average_sale': total_revenue / len(recent_sales) if recent_sales else 0,
            'top_items': top_items,
            'sales_by_day': sales_by_day,
            'period_days': days
        }
    
    def get_restock_suggestions(self) -> List[Dict]:
        """Get items that need restocking based on sales velocity"""
        suggestions = []
        analytics = self.get_sales_analytics(30)  # Last 30 days
        
        for item_data in analytics['top_items'][:10]:  # Top 10 selling items
            # Find the actual item
            item = None
            for i in self.items:
                if i['name'] == item_data['item_name']:
                    item = i
                    break
            
            if not item:
                continue
                
            current_stock = self.inventory.get(item['id'], {}).get('quantity', 0)
            daily_avg_sales = item_data['quantity'] / 30  # Average daily sales
            
            if current_stock <= self.settings['low_stock_threshold'] or current_stock < (daily_avg_sales * 7):
                suggested_quantity = max(int(daily_avg_sales * 14), self.settings['low_stock_threshold'] * 2)
                
                suggestions.append({
                    'item': item,
                    'current_stock': current_stock,
                    'daily_avg_sales': round(daily_avg_sales, 2),
                    'suggested_quantity': suggested_quantity,
                    'reason': 'High sales velocity' if current_stock > self.settings['low_stock_threshold'] else 'Low stock',
                    'priority': 'High' if current_stock <= self.settings['low_stock_threshold'] else 'Medium'
                })
        
        return sorted(suggestions, key=lambda x: x['current_stock'])
    
    def get_daily_summary(self, date: str = None) -> Dict:
        """Get daily sales summary"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        daily_sales = [
            sale for sale in self.sales
            if datetime.fromisoformat(sale['sale_date']).date().isoformat() == date
        ]
        
        if not daily_sales:
            return {
                'date': date,
                'total_sales': 0,
                'total_revenue': 0,
                'total_profit': 0,
                'total_items_sold': 0,
                'sales_count': 0
            }
        
        return {
            'date': date,
            'total_sales': len(daily_sales),
            'total_revenue': sum(sale['total_amount'] for sale in daily_sales),
            'total_profit': sum(sale['profit'] for sale in daily_sales),
            'total_items_sold': sum(sale['quantity'] for sale in daily_sales),
            'sales_count': len(daily_sales),
            'sales': daily_sales
        }
    
    def dismiss_alert(self, alert_id: int):
        """Dismiss an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['active'] = False
                break
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [alert for alert in self.alerts if alert['active']]
    
    def parse_sale_input(self, input_text: str) -> Dict:
        """Parse natural language sale input"""
        # Simple parsing for inputs like "sold milk for K15" or "milk 2 K15"
        input_text = input_text.lower().strip()
        
        # Remove common words
        input_text = input_text.replace('sold', '').replace('for', '').strip()
        
        # Try to extract item name, quantity, and price
        parts = input_text.split()
        
        if len(parts) < 2:
            raise ValueError("Please provide item name and price")
        
        # Look for price (starts with K or is a number)
        price = None
        price_index = -1
        for i, part in enumerate(parts):
            if part.startswith('k') and len(part) > 1:
                try:
                    price = float(part[1:])
                    price_index = i
                    break
                except ValueError:
                    continue
            try:
                if float(part) > 0:
                    price = float(part)
                    price_index = i
                    break
            except ValueError:
                continue
        
        if price is None:
            raise ValueError("Could not find price in input")
        
        # Look for quantity (number before price)
        quantity = 1
        quantity_index = -1
        if price_index > 0:
            try:
                quantity = int(parts[price_index - 1])
                quantity_index = price_index - 1
            except (ValueError, IndexError):
                quantity = 1
        
        # Extract item name (everything before quantity/price)
        end_index = quantity_index if quantity_index > 0 else price_index
        item_name_parts = parts[:end_index]
        item_name = ' '.join(item_name_parts).title()
        
        if not item_name:
            raise ValueError("Could not identify item name")
        
        return {
            'item_name': item_name,
            'quantity': quantity,
            'price': price
        }
    
    def setup_business(self, business_name: str, business_type: str) -> bool:
        """Setup business with type and update categories"""
        try:
            self.settings['business_name'] = business_name
            self.settings['business_type'] = business_type
            self.settings['setup_completed'] = True
            
            # Update categories based on business type
            self.business_categories = self._get_business_categories(business_type)
            self.item_categories = self.business_categories.copy()
            
            return True
        except Exception as e:
            print(f"Error setting up business: {e}")
            return False
    
    def is_setup_completed(self) -> bool:
        """Check if business setup is completed"""
        return self.settings.get('setup_completed', False)
    
    def get_business_types(self) -> List[Dict[str, str]]:
        """Get available business types"""
        return [
            {'id': 'grocery', 'name': 'Grocery Store', 'description': 'Food, beverages, and household items'},
            {'id': 'electronics', 'name': 'Electronics Store', 'description': 'Mobile phones, computers, and gadgets'},
            {'id': 'hair_salon', 'name': 'Hair Salon', 'description': 'Hair care products and styling tools'},
            {'id': 'tailoring', 'name': 'Tailoring Shop', 'description': 'Fabrics, threads, and sewing supplies'},
            {'id': 'pharmacy', 'name': 'Pharmacy', 'description': 'Medicines and health products'},
            {'id': 'restaurant', 'name': 'Restaurant/Cafe', 'description': 'Food and beverage service'},
            {'id': 'bookstore', 'name': 'Bookstore', 'description': 'Books and stationery items'},
            {'id': 'clothing', 'name': 'Clothing Store', 'description': 'Fashion and accessories'},
            {'id': 'auto_parts', 'name': 'Auto Parts Store', 'description': 'Car parts, accessories, and automotive supplies'},
            {'id': 'bakery', 'name': 'Bakery', 'description': 'Bread, cakes, pastries, and baking supplies'},
            {'id': 'hardware', 'name': 'Hardware Store', 'description': 'Tools, construction materials, and home improvement'},
            {'id': 'jewelry', 'name': 'Jewelry Store', 'description': 'Jewelry, watches, and precious accessories'},
            {'id': 'sports', 'name': 'Sports Store', 'description': 'Sports equipment, fitness gear, and athletic wear'},
            {'id': 'pet_store', 'name': 'Pet Store', 'description': 'Pet supplies, food, toys, and accessories'},
            {'id': 'flower_shop', 'name': 'Flower Shop', 'description': 'Fresh flowers, plants, and gardening supplies'},
            {'id': 'office_supplies', 'name': 'Office Supplies', 'description': 'Business equipment, stationery, and office furniture'},
            {'id': 'cosmetics', 'name': 'Cosmetics Store', 'description': 'Beauty products, makeup, and skincare'},
            {'id': 'toy_store', 'name': 'Toy Store', 'description': 'Toys, games, and children\'s entertainment'},
            {'id': 'mobile_shop', 'name': 'Mobile Phone Shop', 'description': 'Mobile phones, accessories, and repair services'},
            {'id': 'furniture', 'name': 'Furniture Store', 'description': 'Home and office furniture, decor items'},
            {'id': 'paint_shop', 'name': 'Paint Shop', 'description': 'Paints, brushes, and painting supplies'},
            {'id': 'shoe_store', 'name': 'Shoe Store', 'description': 'Footwear, sandals, and shoe accessories'},
            {'id': 'fabric_shop', 'name': 'Fabric Shop', 'description': 'Textiles, fabrics, and sewing materials'},
            {'id': 'computer_shop', 'name': 'Computer Shop', 'description': 'Computers, laptops, and IT equipment'},
            {'id': 'gift_shop', 'name': 'Gift Shop', 'description': 'Gifts, souvenirs, and novelty items'},
            {'id': 'music_store', 'name': 'Music Store', 'description': 'Musical instruments, audio equipment, and music accessories'},
            {'id': 'bicycle_shop', 'name': 'Bicycle Shop', 'description': 'Bicycles, cycling gear, and repair services'},
            {'id': 'general_store', 'name': 'General Store', 'description': 'Mixed goods and everyday essentials'},
            {'id': 'other', 'name': 'Other Business', 'description': 'Custom business type with general categories'}
        ]

# Global data manager instance
data_manager = DataManager()
