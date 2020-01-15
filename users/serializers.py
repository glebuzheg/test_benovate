from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, )

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'inn', 'balance']


class SendToUsersSerializer(serializers.ModelSerializer):
    inns = serializers.ListField(child=serializers.CharField(required=False), required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, )

    class Meta:
        model = User
        fields = ['id', 'inns', 'amount', ]

    def validate_inns(self, inns):
        users = User.objects.filter(inn__in=inns).exclude(id=self.instance.pk)
        if not users:
            raise serializers.ValidationError('Пользователи с данными инн не найдены')
        return users

    def validate_amount(self, amount):
        if self.instance.balance < amount:
            raise serializers.ValidationError('На балансе не достаточно средств')
        return amount

    @transaction.atomic
    def update(self, instance, validated_data):
        amount = validated_data.pop('amount')
        users = validated_data.pop('inns')
        count = len(users)
        instance.write_off(amount)
        users.add_to_balance(amount / count)
        return super().update(instance, validated_data)

    @property
    def data(self):
        return UserSerializer(instance=self.instance, context=self.context).data
