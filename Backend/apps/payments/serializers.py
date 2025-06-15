from rest_framework import serializers
from .models import Payment, PaymentMethod, PaymentRefund


class PaymentSerializer(serializers.ModelSerializer):
    """
    Payment serializer
    """
    is_successful = serializers.BooleanField(read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)
    remaining_refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'amount', 'currency', 'status',
            'transaction_id', 'notes', 'processed_at', 'refund_amount',
            'refund_reason', 'is_successful', 'can_be_refunded',
            'remaining_refund_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order', 'transaction_id', 'processed_at', 'refund_amount',
            'created_at', 'updated_at'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Payment method serializer
    """
    masked_number = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'card_type', 'last_four_digits', 'expiry_month', 'expiry_year',
            'cardholder_name', 'is_default', 'is_verified', 'masked_number',
            'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CreatePaymentMethodSerializer(serializers.ModelSerializer):
    """
    Create payment method serializer
    """
    card_number = serializers.CharField(write_only=True, max_length=19)
    cvv = serializers.CharField(write_only=True, max_length=4)

    class Meta:
        model = PaymentMethod
        fields = [
            'card_number', 'cvv', 'card_type', 'expiry_month', 'expiry_year',
            'cardholder_name', 'is_default'
        ]

    def validate_card_number(self, value):
        # Remove spaces and validate length
        card_number = value.replace(' ', '')
        if len(card_number) < 13 or len(card_number) > 19:
            raise serializers.ValidationError("Invalid card number length")
        
        # Basic Luhn algorithm validation
        def luhn_check(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10 == 0
        
        if not luhn_check(card_number):
            raise serializers.ValidationError("Invalid card number")
        
        return card_number

    def validate_expiry_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Invalid expiry month")
        return value

    def validate_expiry_year(self, value):
        from datetime import date
        current_year = date.today().year
        if value < current_year or value > current_year + 20:
            raise serializers.ValidationError("Invalid expiry year")
        return value

    def create(self, validated_data):
        # Extract sensitive data
        card_number = validated_data.pop('card_number')
        cvv = validated_data.pop('cvv')
        
        # In production, tokenize the card with payment gateway
        # For now, just store last 4 digits
        validated_data['last_four_digits'] = card_number[-4:]
        validated_data['user'] = self.context['request'].user
        
        # TODO: Integrate with payment gateway to tokenize card
        # validated_data['gateway_token'] = tokenize_card(card_number, cvv, ...)
        
        return super().create(validated_data)


class ProcessPaymentSerializer(serializers.Serializer):
    """
    Process payment serializer
    """
    order_id = serializers.UUIDField()
    payment_method_id = serializers.UUIDField(required=False)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    
    # For new card payments
    card_number = serializers.CharField(required=False, max_length=19)
    cvv = serializers.CharField(required=False, max_length=4)
    expiry_month = serializers.IntegerField(required=False)
    expiry_year = serializers.IntegerField(required=False)
    cardholder_name = serializers.CharField(required=False, max_length=100)
    save_card = serializers.BooleanField(default=False)

    def validate(self, attrs):
        payment_method = attrs.get('payment_method')
        payment_method_id = attrs.get('payment_method_id')
        
        if payment_method in ['credit_card', 'debit_card']:
            if not payment_method_id:
                # Validate new card details
                required_fields = ['card_number', 'cvv', 'expiry_month', 'expiry_year', 'cardholder_name']
                for field in required_fields:
                    if not attrs.get(field):
                        raise serializers.ValidationError(f"{field} is required for card payments")
        
        return attrs


class PaymentRefundSerializer(serializers.ModelSerializer):
    """
    Payment refund serializer
    """
    is_successful = serializers.BooleanField(read_only=True)

    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'payment', 'amount', 'reason', 'status',
            'refund_transaction_id', 'processed_at', 'processed_by',
            'is_successful', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'payment', 'refund_transaction_id', 'processed_at',
            'processed_by', 'created_at', 'updated_at'
        ]


class CreateRefundSerializer(serializers.Serializer):
    """
    Create refund serializer
    """
    payment_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_payment_id(self, value):
        try:
            payment = Payment.objects.get(id=value, is_active=True)
            if not payment.can_be_refunded:
                raise serializers.ValidationError("Payment cannot be refunded")
            return payment
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found")

    def validate(self, attrs):
        payment = attrs['payment_id']
        amount = attrs['amount']
        
        if amount > payment.remaining_refund_amount:
            raise serializers.ValidationError("Refund amount exceeds remaining amount")
        
        return attrs