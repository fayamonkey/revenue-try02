import streamlit as st
from datetime import datetime, timedelta
import os

# Initialize session state for step tracking and data if not exists
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'order_data' not in st.session_state:
    current_date = datetime.now()
    st.session_state.order_data = {
        'customer_name': 'BikeWorld Wholesale',
        'product': 'Mountain Bike (Black)',
        'quantity': 100,
        'unit_price': 500,
        'total_value': 50000,
        'credit_status': None,
        'inventory_status': None,
        'materials_status': None,
        'start_date': current_date,
        'current_date': current_date,
        'expected_delivery': current_date + timedelta(days=5),
        'documents': {},
        'costs': {
            'product_cost': 50000,
            'shipping': 0,
            'procurement': 0,
            'production': 0
        }
    }

# Add function to handle document downloads
def create_download_button(title, content, filename):
    """Create a download button for a document"""
    # Clean the content (remove any streamlit-specific formatting)
    clean_content = content.replace("    ", "")  # Remove leading spaces
    
    # Create the full markdown content with proper formatting
    markdown_content = f"""# {title}\n\n{clean_content}"""
    
    # Create download button
    st.download_button(
        label=f"💾 Download {title}",
        data=markdown_content,
        file_name=f"{filename}.md",
        mime="text/markdown"
    )

def display_document(title, content, document_type="notice", filename=None):
    """Display a document with consistent formatting and optional download button"""
    st.markdown("---")
    st.markdown(f"### 📄 {title}")
    
    if document_type == "notice":
        st.info(content)
    elif document_type == "warning":
        st.warning(content)
    elif document_type == "error":
        st.error(content)
    else:
        st.markdown(content)
    
    # Add download button if filename is provided
    if filename:
        create_download_button(title, content, filename)
    
    st.markdown("---")

def format_date(date):
    """Format datetime object to string"""
    return date.strftime("%B %d, %Y")

def update_timeline(days_to_add):
    """Update the timeline with additional days"""
    st.session_state.order_data['current_date'] += timedelta(days=days_to_add)
    st.session_state.order_data['expected_delivery'] = max(
        st.session_state.order_data['current_date'] + timedelta(days=5),
        st.session_state.order_data['expected_delivery']
    )

# Define the steps
STEPS = {
    1: "Customer Inquiry & Response",
    2: "Order Placement",
    3: "Credit Check & Approval",
    4: "Inventory Management",
    5: "Back Order Processing",
    6: "Procurement",
    7: "Production",
    8: "Shipping Process",
    9: "Billing Process",
    10: "Cash Collections"
}

def proceed_to_next_step():
    current = st.session_state.current_step
    
    # Handle Credit Check Decision
    if current == 3:
        st.session_state.order_data['credit_status'] = st.session_state.credit_decision
        if st.session_state.credit_decision == "Reject":
            st.session_state.order_data['documents']['rejection_notice'] = {
                'reason': 'Credit Check Failed',
                'date': format_date(st.session_state.order_data['current_date']),
                'customer': st.session_state.order_data['customer_name']
            }
            st.session_state.current_step = 1  # Reset to start
            return
        update_timeline(1)  # 1 day for credit check
    
    # Handle Inventory Decision
    elif current == 4:
        st.session_state.order_data['inventory_status'] = st.session_state.inventory_decision
        if st.session_state.inventory_decision == "In Stock":
            st.session_state.order_data['costs']['shipping'] = 2000
            st.session_state.current_step = 8  # Skip to Shipping
            update_timeline(1)
            return
        update_timeline(1)
    
    # Handle Raw Materials Decision
    elif current == 5:
        st.session_state.order_data['materials_status'] = st.session_state.materials_decision
        if st.session_state.materials_decision == "Available":
            st.session_state.order_data['costs']['production'] = 35000
            st.session_state.current_step = 7  # Skip to Production
            update_timeline(1)
            return
        update_timeline(1)
    
    # Add procurement costs
    elif current == 6:
        st.session_state.order_data['costs']['procurement'] = 40000
        update_timeline(10)  # 10 days for procurement
    
    # Add production time
    elif current == 7:
        st.session_state.order_data['costs']['production'] = 35000
        update_timeline(3)  # 3 days for production
    
    # Add shipping costs for out of stock
    elif current == 8:
        if st.session_state.order_data.get('inventory_status') == "Out of Stock":
            st.session_state.order_data['costs']['shipping'] = 3500
        update_timeline(2)  # 2 days for shipping
    
    # Normal progression
    if st.session_state.current_step < len(STEPS):
        st.session_state.current_step += 1

# Sidebar with progress tracker and timeline
st.sidebar.title("Revenue Cycle Progress")

# Display timeline in sidebar
st.sidebar.markdown("### Timeline")
st.sidebar.markdown(f"""
- Start Date: {format_date(st.session_state.order_data['start_date'])}
- Current Date: {format_date(st.session_state.order_data['current_date'])}
- Expected Delivery: {format_date(st.session_state.order_data['expected_delivery'])}
""")

# Display costs in sidebar
total_cost = sum(st.session_state.order_data['costs'].values())
st.sidebar.markdown("### Cost Summary")
for cost_type, amount in st.session_state.order_data['costs'].items():
    if amount > 0:
        st.sidebar.markdown(f"- {cost_type.replace('_', ' ').title()}: ${amount:,}")
if total_cost > 0:
    st.sidebar.markdown(f"**Total Cost: ${total_cost:,}**")

# Display progress
for step_num, step_name in STEPS.items():
    if step_num < st.session_state.current_step:
        st.sidebar.markdown(f"✅ {step_num}. {step_name}")
    elif step_num == st.session_state.current_step:
        st.sidebar.markdown(f"🔵 {step_num}. {step_name}")
    else:
        st.sidebar.markdown(f"⚪ {step_num}. {step_name}")

# Main content area
st.title("Revenue Cycle Simulator")

# Display current step content
current_step = st.session_state.current_step
st.header(f"Step {current_step}: {STEPS[current_step]}")

# Placeholder content for each step
if current_step == 1:
    st.markdown("### Your Role: Sales Representative")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Customer submits an inquiry about product availability, pricing, and delivery times.""")
    
    display_document("Response to Inquiry", f"""
    **Date:** {format_date(st.session_state.order_data['current_date'])}
    **To:** {st.session_state.order_data['customer_name']}
    **Subject:** Response to Product Inquiry
    
    **Product Details:**
    - Product: {st.session_state.order_data['product']}
    - Unit Price: ${st.session_state.order_data['unit_price']}
    - Available Quantity: 120 units
    - Delivery Timeframe: 5 business days
    
    Please submit a Purchase Order (PO) if these terms are acceptable.
    """, filename="response_to_inquiry")
    
    # Show rejection notice if coming back from credit check
    if 'rejection_notice' in st.session_state.order_data.get('documents', {}):
        display_document("Rejected Order Notification", f"""
        **To:** {st.session_state.order_data['documents']['rejection_notice']['customer']}
        **Date:** {st.session_state.order_data['documents']['rejection_notice']['date']}
        **Subject:** Order Status Update
        
        We regret to inform you that your order could not be processed at this time.
        Reason: {st.session_state.order_data['documents']['rejection_notice']['reason']}
        
        Please contact our credit department for further information.
        """, "error", filename="order_rejection_notice")

elif current_step == 2:
    st.markdown("### Your Role: Sales Representative")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Customer submits a Purchase Order (PO) specifying product details and requirements.""")
    
    display_document("Purchase Order Received", f"""
    **Purchase Order**
    PO Number: PO-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    
    **Order Details:**
    - Customer: {st.session_state.order_data['customer_name']}
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']}
    - Unit Price: ${st.session_state.order_data['unit_price']}
    - Total Value: ${st.session_state.order_data['total_value']:,}
    
    **Delivery Requirements:**
    - Requested Delivery Date: {format_date(st.session_state.order_data['expected_delivery'])}
    - Shipping Address: BikeWorld Wholesale, 123 Bike Street, NY
    
    🔜 Next Step: Check customer's credit limit before approving the order.
    """, filename="purchase_order")

elif current_step == 3:
    st.markdown("### Your Role: Credit Manager")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: The system retrieves customer's credit information for review.""")
    
    display_document("Credit Check Report", f"""
    **Credit Assessment Report**
    Customer: {st.session_state.order_data['customer_name']}
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Current Credit Status:**
    - Credit Limit: $100,000
    - Current Open Liabilities: $30,000
    - New Order Value: ${st.session_state.order_data['total_value']:,}
    - Total Exposure After Order: $80,000
    
    **Decision Required:**
    ✅ Approved: Order moves to Inventory Check
    ❌ Rejected: Generate Rejection Notice
    """, filename="credit_check_report")
    
    decision = st.radio("Credit Check Decision", ["Approve", "Reject"], key="credit_decision")
    st.markdown("""**Note:** If you reject, the process will restart and a rejection notice will be generated.""")

elif current_step == 4:
    st.markdown("### Your Role: Inventory Manager")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: The system checks Finished Goods (FG) inventory.""")
    
    display_document("Inventory Status Report", f"""
    **Inventory Check Report**
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Required:**
    - Product: {st.session_state.order_data['product']}
    - Quantity Needed: {st.session_state.order_data['quantity']}
    
    **Current Inventory Status:**
    - Available in FG Stock: 120 units
    - Location: Warehouse Aisle 7, Shelf 3
    
    **Decision Required:**
    ✅ FG in Stock: Proceed to Shipping
    ❌ FG Out of Stock: Create Back Order & Move to Production
    """, filename="inventory_status_report")
    
    decision = st.radio("Inventory Status", ["In Stock", "Out of Stock"], key="inventory_decision")
    st.markdown("""**Note:** 
    - If 'In Stock': Process will skip to Shipping
    - If 'Out of Stock': Back Order process will begin""")

elif current_step == 5:
    st.markdown("### Your Role: Production Manager")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Back Order is created. Production must be scheduled.""")
    
    display_document("Back Order Processing", f"""
    **Back Order & Production Check**
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Back Order Details:**
    - Order ID: BO-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']}
    
    **Raw Materials Check:**
    - Required: Bike Frames (Black)
    - Quantity Needed: {st.session_state.order_data['quantity']} units
    
    **Decision Required:**
    ✅ Raw Materials Available: Proceed with Production
    ❌ Raw Materials Out of Stock: Trigger Procurement Process
    """, filename="back_order_processing")
    
    decision = st.radio("Raw Materials Status", ["Available", "Not Available"], key="materials_decision")
    st.markdown("""**Note:**
    - If 'Available': Production Order will be issued
    - If 'Not Available': Procurement Process will begin""")

elif current_step == 6:
    st.markdown("### Your Role: Procurement Manager")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Purchase Requisition (PR) is issued to Procurement.""")
    
    display_document("Purchase Requisition", f"""
    **Purchase Requisition (PR)**
    PR Number: PR-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Material Requirements:**
    - Item: Bike Frames (Black)
    - Quantity: {st.session_state.order_data['quantity']} units
    - Required By: {format_date(st.session_state.order_data['expected_delivery'])}
    
    **Vendor Information:**
    - Supplier: Premium Bike Frames Ltd.
    - Terms: Net 30
    - Expected Delivery: 10 business days
    """, filename="purchase_requisition")
    
    display_document("Purchase Order to Vendor", f"""
    **Purchase Order (PO) to Vendor**
    PO Number: PO-V-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    
    **Order Details:**
    - Vendor: Premium Bike Frames Ltd.
    - Material: Bike Frames (Black)
    - Quantity: {st.session_state.order_data['quantity']} units
    - Unit Cost: $400
    - Total Cost: ${st.session_state.order_data['costs']['procurement']:,}
    
    **Delivery Requirements:**
    - Delivery Address: Warehouse Receiving Dock
    - Required By: {format_date(st.session_state.order_data['expected_delivery'])}
    """, filename="purchase_order_vendor")

elif current_step == 7:
    st.markdown("### Your Role: Production Manager")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Raw Materials are available, production can begin.""")
    
    display_document("Production Order", f"""
    **Production Order**
    Production Order #: PO-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Production Details:**
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']} units
    - Status: In Production
    - Start Date: {format_date(st.session_state.order_data['current_date'])}
    - Estimated Completion: {format_date(st.session_state.order_data['current_date'] + timedelta(days=3))}
    
    **Cost Information:**
    - Production Cost: ${st.session_state.order_data['costs']['production']:,}
    
    **Next Steps:**
    ✔ Production team notified
    ✔ Materials allocated
    ✔ Production scheduled
    """, filename="production_order")

elif current_step == 8:
    st.markdown("### Your Role: Warehouse Operations")
    st.markdown("#### Scenario")
    shipping_source = "Production" if st.session_state.order_data.get('inventory_status') == "Out of Stock" else "Inventory"
    st.markdown(f"""📥 Input: Shipping process initiated for order from {shipping_source}.""")
    
    display_document("Picking Ticket", f"""
    **Picking Ticket**
    Picking Ticket #: PT-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    
    **Order Information:**
    - Sales Order ID: SO-2025-0043
    - Customer: {st.session_state.order_data['customer_name']}
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']}
    - Source: {shipping_source}
    - Location: Aisle 7, Shelf 3
    - Status: Ready for Picking
    """, filename="picking_ticket")
    
    display_document("Packing Slip", f"""
    **Packing Slip**
    Packing Slip #: PS-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    
    **Shipment Details:**
    - Customer: {st.session_state.order_data['customer_name']}
    - Sales Order ID: SO-2025-0043
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']}
    - Total Weight: 1,500 kg
    - Packing Date: {format_date(st.session_state.order_data['current_date'])}
    - Status: Packed
    """, filename="packing_slip")
    
    display_document("Bill of Lading", f"""
    **Bill of Lading (BoL)**
    BoL #: BOL-{st.session_state.order_data['current_date'].strftime('%Y%m%d')}
    
    **Shipment Information:**
    - Carrier: Fast Freight Logistics
    - Shipment ID: SHP-2025-0012
    - Origin: Bicycle Manufacturer Warehouse, CA
    - Destination: {st.session_state.order_data['customer_name']}, NY
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']}
    - Total Weight: 1,500 kg
    
    **Shipping Terms:**
    - Freight Charges: ${st.session_state.order_data['costs']['shipping']:,}
    - Incoterms: FOB (Free on Board)
    - Insurance: $200,000 coverage
    
    **Status:** Ready for Shipment
    """, filename="bill_of_lading")

elif current_step == 9:
    st.markdown("### Your Role: Billing Clerk")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Shipping documents received, ready for invoice generation.""")
    
    additional_costs = st.session_state.order_data['costs']['shipping']
    total_invoice = st.session_state.order_data['total_value'] + additional_costs
    
    display_document("Invoice", f"""
    **Invoice**
    Invoice #: INV-2025-0103
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Bill To:**
    {st.session_state.order_data['customer_name']}
    123 Bike Street
    New York, NY
    
    **Order Details:**
    - Sales Order ID: SO-2025-0043
    - Product: {st.session_state.order_data['product']}
    - Quantity: {st.session_state.order_data['quantity']}
    - Unit Price: ${st.session_state.order_data['unit_price']}
    - Total Product Cost: ${st.session_state.order_data['total_value']:,}
    
    **Additional Charges:**
    - Freight Cost: ${additional_costs:,}
    
    **Payment Details:**
    - Total Invoice Amount: ${total_invoice:,}
    - Payment Terms: Net 30
    - Due Date: {format_date(st.session_state.order_data['current_date'] + timedelta(days=30))}
    
    **Status:** Sent to Customer
    """, filename="customer_invoice")
    
    display_document("Accounts Receivable Update", f"""
    **A/R Journal Entry**
    Date: {format_date(st.session_state.order_data['current_date'])}
    
    **Debit:**
    - Accounts Receivable: ${total_invoice:,}
    
    **Credit:**
    - Sales Revenue: ${st.session_state.order_data['total_value']:,}
    - Freight Revenue: ${additional_costs:,}
    """, "notice", filename="ar_journal_entry")

elif current_step == 10:
    st.markdown("### Your Role: Accounts Receivable")
    st.markdown("#### Scenario")
    st.markdown("""📥 Input: Awaiting customer payment processing.""")
    
    total_invoice = st.session_state.order_data['total_value'] + st.session_state.order_data['costs']['shipping']
    
    display_document("Payment Processing", f"""
    **Payment Details**
    Invoice #: INV-2025-0103
    
    **Amount Due:**
    - Total Invoice Amount: ${total_invoice:,}
    - Due Date: {format_date(st.session_state.order_data['current_date'] + timedelta(days=30))}
    
    **Payment Method:**
    - Wire Transfer
    - Payment Terms: Net 30
    
    **Bank Information:**
    - Bank: Commerce Bank
    - Account: XXXXXXXX
    - Reference: INV-2025-0103
    
    **Status:** Awaiting Payment
    """, filename="payment_processing")
    
    st.success("🎉 Revenue Cycle Complete! All documents generated and processed.")

# Proceed button (except for last step)
if current_step < len(STEPS):
    st.button("Proceed to Next Step", on_click=proceed_to_next_step)
else:
    st.button("Start Over", on_click=lambda: setattr(st.session_state, 'current_step', 1)) 