from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db import transaction
from .models import (
    CustomUser, PlatformSettings, Level, BankDetails, Deposit, 
    Withdrawal, Task, Roulette, RouletteSettings, UserLevel, PlatformBankDetails
)

# --- CUSTOM USER ADMIN (Com contador de convites e investidores) ---

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Adicionado 'total_invited' e 'investor_referrals' no display
    list_display = ('phone_number', 'available_balance', 'total_invited', 'investor_referrals', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('phone_number', 'invite_code')
    list_filter = ('is_staff', 'is_active', 'level_active')
    readonly_fields = ('total_invited', 'investor_referrals')

    def total_invited(self, obj):
        """Conta quantas pessoas o usuário convidou no total."""
        return CustomUser.objects.filter(invited_by=obj).count()
    total_invited.short_description = 'Total Convidados'

    def investor_referrals(self, obj):
        """Conta quantos convidados já ativaram um nível (investiram)."""
        # Filtra usuários convidados por ele que possuem um UserLevel ativo
        return CustomUser.objects.filter(invited_by=obj, userlevel__is_active=True).distinct().count()
    investor_referrals.short_description = 'Convidados Investidores'

# --- DEPOSIT ADMIN (Com automação de saldo) ---

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'is_approved', 'created_at', 'proof_link') 
    search_fields = ('user__phone_number',)
    list_filter = ('is_approved',)
    readonly_fields = ('current_proof_display',)

    def save_model(self, request, obj, form, change):
        """
        Sobrescreve o salvamento para somar o saldo automaticamente 
        quando o depósito for marcado como aprovado.
        """
        if change: # Se estiver editando um depósito existente
            old_obj = Deposit.objects.get(pk=obj.pk)
            # Se mudou de NÃO aprovado para APROVADO agora
            if not old_obj.is_approved and obj.is_approved:
                with transaction.atomic():
                    user = obj.user
                    user.available_balance += obj.amount
                    user.save()
        
        super().save_model(request, obj, form, change)

    def proof_link(self, obj):
        if obj.proof_of_payment:
            return mark_safe(f'<a href="{obj.proof_of_payment.url}" target="_blank">Ver Comprovativo</a>')
        return "Nenhum"
    proof_link.short_description = 'Comprovativo'

    def current_proof_display(self, obj):
        if obj.proof_of_payment:
            return mark_safe(f'''
                <a href="{obj.proof_of_payment.url}" target="_blank">Ver Imagem</a><br/>
                <img src="{obj.proof_of_payment.url}" style="max-width:300px; height:auto; margin-top: 10px;" />
            ''')
        return "Nenhum"
    current_proof_display.short_description = 'Comprovativo Atual'

# --- WITHDRAWAL ADMIN (Dados bancários automáticos) ---

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    # Exibe os dados bancários diretamente na lista principal
    list_display = ('user', 'amount', 'status', 'get_user_full_name', 'user_iban', 'bank_info', 'created_at')
    search_fields = ('user__phone_number', 'user__full_name')
    list_filter = ('status',)
    
    def get_user_full_name(self, obj):
        return obj.user.full_name or "Não preenchido"
    get_user_full_name.short_description = 'Nome do Cliente'

    def user_iban(self, obj):
        try:
            return obj.user.bankdetails.IBAN
        except BankDetails.DoesNotExist:
            return "Sem IBAN"
    user_iban.short_description = 'IBAN'

    def bank_info(self, obj):
        try:
            details = obj.user.bankdetails
            return f"{details.bank_name} - {details.account_holder_name}"
        except BankDetails.DoesNotExist:
            return "Sem dados bancários"
    bank_info.short_description = 'Banco / Titular'

# --- OUTROS REGISTROS (Mantidos conforme original) ---

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'whatsapp_link', 'app_download_link') 

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'deposit_value', 'daily_gain', 'cycle_days')

@admin.register(BankDetails)
class BankDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'IBAN', 'account_holder_name')

@admin.register(PlatformBankDetails)
class PlatformBankDetailsAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_holder_name', 'IBAN')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'earnings', 'completed_at')

@admin.register(Roulette)
class RouletteAdmin(admin.ModelAdmin):
    list_display = ('user', 'prize', 'is_approved', 'spin_date')

@admin.register(RouletteSettings)
class RouletteSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'prizes')

@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'purchase_date', 'is_active')
    