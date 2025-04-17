import razorpay
import json

class PaymentManager:
    def __init__(self):
        # Test mode credentials
        self.client = razorpay.Client(
            auth=("rzp_test_key", "rzp_test_secret")
        )
    
    def create_order(self, amount, currency="INR"):
        """Create a Razorpay order"""
        try:
            # For demo purposes, always return success
            return {
                'id': 'order_demo123',
                'amount': amount,
                'currency': currency,
                'status': 'created'
            }
        except Exception as e:
            return None
    
    def verify_payment(self, payment_id, order_id, signature):
        """Verify Razorpay payment signature"""
        try:
            # For demo purposes, always return success
            return True
        except Exception as e:
            return False
    
    def process_payment(self, amount):
        """Process payment and return demo success response"""
        return {
            'status': 'success',
            'payment_id': 'pay_demo123',
            'order_id': 'order_demo123',
            'signature': 'sig_demo123'
        }