from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


class Member(models.Model):
    class MemberRole(models.TextChoices):
        OWNER = "OWNER", _("Owner")
        MEMBER = "MEMBER", _("Member")

    id = models.UUIDField(
        verbose_name=_("UUID"),
        help_text=_(
            "Unique ID for this particular user + organization/team mapping across"
            " whole system"
        ),
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        help_text=_("When the user was added to the organization"),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        help_text=_("When the user's organization details was last updated"),
        auto_now=True,
    )
    user = models.ForeignKey(
        verbose_name=_("User"),
        help_text=_("User in this organization"),
        to=UserModel,
        on_delete=models.CASCADE,
    )
    organization = models.ForeignKey(
        verbose_name=_("Organization"),
        help_text=_("Which organization this user is a member of"),
        to="spice_orgs.Organization",
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        verbose_name=_("Role"),
        help_text=_("Role of the user in this organization"),
        choices=MemberRole.choices,
        default=MemberRole.MEMBER,
        max_length=255,
    )
    publicly_visible = models.BooleanField(
        verbose_name=_("Publicly Visible"),
        help_text=_(
            "Is this user's membership in this organization/team publicly visible"
        ),
        default=False,
    )

    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Members"
        unique_together = ["user", "organization"]

    def __str__(self) -> str:
        return f"{self.organization.slug} | {self.user.username} | {self.role}"


class Organization(models.Model):
    id = models.UUIDField(
        verbose_name=_("UUID"),
        help_text=_("Unique ID for this particular organization across whole system"),
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Name of the organization"),
        max_length=255,
        unique=True,
        blank=False,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        help_text=_("Slug of the organization"),
        max_length=255,
        unique=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        help_text=_("When the organization was created"),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        help_text=_("When the organization was last updated"),
        auto_now=True,
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        verbose_name=_("Created By"),
        help_text=_("User who created this organization"),
        to=UserModel,
        on_delete=models.RESTRICT,
        blank=False,
    )
    publicly_visible = models.BooleanField(
        verbose_name=_("Publicly Visible"),
        help_text=_("Is this organization publicly visible"),
        default=True,
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return f"{self.slug}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if not self.member_set.count() == 0:
            self.add_user_to_organization(
                username=self.created_by.username, role=Member.MemberRole.OWNER
            )

    def is_user_in_organization(self, username) -> bool:
        return self.member_set.filter(user__username=username).exists()

    def add_user_to_organization(self, username, role=Member.MemberRole.MEMBER):
        if self.is_user_in_organization(username):
            raise Exception("User already exists in this organization")
        user = UserModel.objects.get(username=username)
        member = Member.objects.create(user=user, role=role, organization=self)
        return member

    def remove_user_from_organization(self, username) -> bool:
        if self.is_user_in_organization(username):
            raise Exception("User does not exist in this organization")
        if (
            self.member_set.get(member__user__username=username).role
            == Member.MemberRole.OWNER
            and self.member_set.filter(role=TeamMember.MemberRole.OWNER).count() == 1
        ):
            raise Exception("Cannot remove only owner from organization")
        member = Member.objects.get(user__username=username)
        member.delete()
        return True


class TeamMember(models.Model):
    class TeamMemberRole(models.TextChoices):
        OWNER = "OWNER", _("Owner")
        MEMBER = "MEMBER", _("Member")

    id = models.UUIDField(
        verbose_name=_("UUID"),
        help_text=_(
            "Unique ID for this particular user + organization/team mapping across"
            " whole system"
        ),
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        help_text=_("When the user was added to the organization"),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        help_text=_("When the user's organization details was last updated"),
        auto_now=True,
    )
    organization = models.ForeignKey(
        verbose_name=_("Organization"),
        help_text=_("Which organization this user is a member of"),
        to="spice_orgs.Organization",
        on_delete=models.CASCADE,
    )
    member = models.ForeignKey(
        verbose_name=_("Member"),
        help_text=_("Member in organization"),
        to="spice_orgs.Member",
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(
        verbose_name=_("Team"),
        help_text=_("Team member is associated with"),
        to="spice_orgs.Team",
        on_delete=models.CASCADE,
    )
    team_role = models.CharField(
        verbose_name=_("Role"),
        help_text=_("Role of the user in this team"),
        choices=TeamMemberRole.choices,
        default=TeamMemberRole.MEMBER,
        max_length=255,
    )

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        unique_together = ["organization", "team", "member"]

    def __str__(self) -> str:
        return (
            f"{self.organization.slug} | {self.team.slug} |"
            f" {self.member.user.username} | {self.role}"
        )


class Team(models.Model):
    id = models.UUIDField(
        verbose_name=_("UUID"),
        help_text=_("Unique ID for this particular team across whole system"),
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Name of the team"),
        max_length=255,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        help_text=_("Slug of the team"),
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        help_text=_("When the team was created"),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        help_text=_("When the team was last updated"),
        auto_now=True,
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        verbose_name=_("Created By"),
        help_text=_("User who created this team"),
        to=UserModel,
        on_delete=models.RESTRICT,
        blank=False,
    )
    organization = models.ForeignKey(
        verbose_name=_("Organization"),
        help_text=_("Which organization this team is associated with"),
        to="spice_orgs.Organization",
        on_delete=models.CASCADE,
    )
    visible_to_organization = models.BooleanField(
        verbose_name=_("Visible to Organization"),
        help_text=_("Is this team visible to the others in the organization"),
        default=False,
    )

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        unique_together = ["name", "slug", "organization"]

    def __str__(self) -> str:
        return f"{self.organization.slug} | {self.slug}"

    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if self.teammember_set.count() == 0:
            self.add_user_to_team(
                username=self.created_by.username, role=TeamMember.MemberRole.OWNER
            )

    def is_user_in_team(self, username) -> bool:
        return self.teammember_set.filter(member__user__username=username).exists()

    def add_user_to_team(
        self, username, role=TeamMember.TeamMemberRole.MEMBER
    ) -> TeamMember:
        if not self.organization.is_user_in_organization(username=username):
            raise Exception("User does not exist in this organization")
        if self.is_user_in_team(username=username):
            raise Exception("User already a team member")
        organization_member = self.organization.member_set.get(user__username=username)
        team_member = TeamMember.objects.create(
            member=organization_member,
            role=role,
            organization=self.organization,
            team=self,
        )
        return team_member

    def remove_user_from_team(self, username) -> bool:
        if not self.organization.is_user_in_organization(username=username):
            raise Exception("User does not exist in this organization")
        if not self.is_user_in_team(username=username):
            raise Exception("User does not exist in this team")
        if (
            self.teammember_set.get(member__user__username=username).role
            == TeamMember.MemberRole.OWNER
            and self.teammember_set.filter(role=TeamMember.MemberRole.OWNER).count()
            == 1
        ):
            raise Exception("Cannot remove only owner from team")
        self.teammember_set.get(member__user__username=username).delete()
        return True
