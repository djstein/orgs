from django.contrib import admin

from .models import Member, Organization, Team, TeamMember


class MemberAdmin(admin.ModelAdmin):
    list_display = ["organization", "user", "role"]


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["slug", "created_by", "publicly_visible"]


class TeamAdmin(admin.ModelAdmin):
    list_display = [
        "slug",
        "organization",
        "created_by",
        "visible_to_organization",
    ]


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["team", "member", "team_role"]


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
