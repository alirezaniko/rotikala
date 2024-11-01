from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

token_obtain_pair_schema = extend_schema(
    responses={
        200: inline_serializer(
            name="TokenSuccessResponse",
            fields={
                'is_success': serializers.BooleanField(),
                'data': inline_serializer(
                    name="TokenData",
                    fields={
                        'access': serializers.CharField(),
                        'refresh': serializers.CharField(),
                    }
                ),
                'errors': serializers.JSONField(allow_null=True),
                'userPermission': serializers.CharField(allow_null=True),
            }
        ),
        400: inline_serializer(
            name="TokenErrorResponse",
            fields={
                'is_success': serializers.BooleanField(default=False),
                'data': serializers.BooleanField(default=False),
                'errors': serializers.ListField(
                    child=serializers.CharField()
                ),
            }
        )
    }
)
token_refresh_schema = extend_schema(
    responses={
        200: inline_serializer(
            name="TokenRefreshSuccessResponse",
            fields={
                'is_success': serializers.BooleanField(),
                'data': inline_serializer(
                    name="access",
                    fields={
                        'access': serializers.CharField()
                    }
                ),
                'errors': serializers.JSONField(allow_null=True),
            }
        ),
        400: inline_serializer(
            name="TokenRefreshErrorResponse",
            fields={
                'is_success': serializers.BooleanField(default=False),
                'data': serializers.JSONField(allow_null=True),
                'errors': serializers.ListField(
                    child=serializers.CharField()
                ),
            }
        )
    }
)

register_schema = extend_schema(
    responses={
        201: inline_serializer(
            name="Register",
            fields={
                'is_success': serializers.BooleanField(),
                'data': serializers.JSONField(),
                'errors': serializers.JSONField(allow_null=True),
            }
        ),
        # 400: inline_serializer(
        #     name="RegisterErrors",
        #     fields={
        #         'is_success': serializers.BooleanField(default=False),
        #         'data': serializers.JSONField(allow_null=True),
        #         'errors': serializers.ListField(
        #             child=serializers.CharField()
        #         ),
        #     }
        # )
    }
)
