
DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'avatar': ['rest_framework.permissions.IsAuthenticated'],
    },
    'SERIALIZERS': {
        'user_create': 'users.serializers.UserSignupSerializer',
        'current_user': 'api.serializers.UserGetSerializer',
        'user': 'api.serializers.UserGetSerializer',
        'avatar': 'users.serializers.AvatarSerializer',
    },
}
