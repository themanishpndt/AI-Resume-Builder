from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _

@login_required
@require_POST
def delete_account(request):
    """
    View to delete the currently logged-in user's account.
    """
    user = request.user
    user.delete()
    logout(request)
    messages.success(request, _("Your account has been successfully deleted."))
    return redirect('home')

class DeleteAccountView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Class-based view for account deletion with confirmation.
    """
    template_name = 'account/delete_account_confirm.html'
    success_url = reverse_lazy('home')
    success_message = _("Your account has been successfully deleted.")
    
    def get_object(self, queryset=None):
        return self.request.user
        
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        logout(request)
        return response
