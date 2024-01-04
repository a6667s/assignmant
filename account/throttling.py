from rest_framework.throttling import AnonRateThrottle

class ThreeRequestsPerMinuteThrottle(AnonRateThrottle):
    rate = '3/m'