# Generated by Django 4.2a1 on 2023-02-13 13:39

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique ID for this particular organization across whole system",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the organization",
                        max_length=255,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Slug of the organization",
                        max_length=255,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the organization was created",
                        verbose_name="Created At",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When the organization was last updated",
                        verbose_name="Updated At",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "publicly_visible",
                    models.BooleanField(
                        default=True,
                        help_text="Is this organization publicly visible",
                        verbose_name="Publicly Visible",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="User who created this organization",
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
            ],
            options={
                "verbose_name": "Organization",
                "verbose_name_plural": "Organizations",
            },
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique ID for this particular team across whole system",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the team",
                        max_length=255,
                        verbose_name="Name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Slug of the team",
                        max_length=255,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the team was created",
                        verbose_name="Created At",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When the team was last updated",
                        verbose_name="Updated At",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "visible_to_organization",
                    models.BooleanField(
                        default=False,
                        help_text="Is this team visible to the others in the organization",
                        verbose_name="Visible to Organization",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="User who created this team",
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="Which organization this team is associated with",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spice_orgs.organization",
                        verbose_name="Organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team",
                "verbose_name_plural": "Teams",
                "unique_together": {("name", "slug", "organization")},
            },
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique ID for this particular user + organization/team mapping across whole system",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the user was added to the organization",
                        verbose_name="Created At",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When the user's organization details was last updated",
                        verbose_name="Updated At",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("OWNER", "Owner"), ("MEMBER", "Member")],
                        default="MEMBER",
                        help_text="Role of the user in this organization",
                        max_length=255,
                        verbose_name="Role",
                    ),
                ),
                (
                    "publicly_visible",
                    models.BooleanField(
                        default=False,
                        help_text="Is this user's membership in this organization/team publicly visible",
                        verbose_name="Publicly Visible",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="Which organization this user is a member of",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spice_orgs.organization",
                        verbose_name="Organization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User in this organization",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Member",
                "verbose_name_plural": "Members",
                "unique_together": {("user", "organization")},
            },
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique ID for this particular user + organization/team mapping across whole system",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the user was added to the organization",
                        verbose_name="Created At",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When the user's organization details was last updated",
                        verbose_name="Updated At",
                    ),
                ),
                (
                    "team_role",
                    models.CharField(
                        choices=[("OWNER", "Owner"), ("MEMBER", "Member")],
                        default="MEMBER",
                        help_text="Role of the user in this team",
                        max_length=255,
                        verbose_name="Role",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        help_text="Member in organization",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spice_orgs.member",
                        verbose_name="Member",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="Which organization this user is a member of",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spice_orgs.organization",
                        verbose_name="Organization",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        help_text="Team member is associated with",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spice_orgs.team",
                        verbose_name="Team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team Member",
                "verbose_name_plural": "Team Members",
                "unique_together": {("organization", "team", "member")},
            },
        ),
    ]
