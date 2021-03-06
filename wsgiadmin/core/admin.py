from django.contrib import admin
from wsgiadmin.core.models import Server, Capability, CommandLog


class CommandLogAdmin(admin.ModelAdmin):
    list_display = ("date", "server", "command", "result_stdout", "result_stderr", "status_code", "processed", )
    list_display_links = ("date", )
    ordering = ['-date']


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "ip", "ssh", "capabilities_str", "libvirt_url", )
    list_display_links = ("name", )
    ordering = ['name']


admin.site.register(CommandLog, CommandLogAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Capability)
