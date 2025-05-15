class PaymentStatus:
    PENDING = 'Pending'
    SUCCESS = 'Success'
    FAILED = 'Failed'

    CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]