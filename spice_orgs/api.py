import logging
from typing import List

from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseForbidden
from ninja import Router
from ninja.pagination import paginate

from .models import Member, Organization, Team, TeamMember
from .schema import (
    AddMemberSchema,
    AddTeamMemberSchema,
    CreateUpdateOrganizationSchema,
    CreateUpdateTeamSchema,
    MemberSchema,
    OrganizationSchema,
    TeamMemberSchema,
    TeamSchema,
    UpdateMemberSchema,
    UpdateTeamMemberSchema,
)

UserModel = get_user_model()

logger = logging.getLogger(__name__)

router = Router()


@router.get("/", response=List[OrganizationSchema])
@paginate
def list_organizations(request):
    """
    List all Organizations a user can see.
    This includes all publicly visible, active ones and any the user is a member of.
    """
    organizations = Organization.objects.filter(is_active=True, publicly_visible=True)
    if not request.user.is_anonymous:
        # if the user is logged in, get the organizations they are a member of
        return organizations.union(
            Organization.objects.filter(is_active=True, member__user=request.user)
        )
    return organizations


@router.get("/{organization_slug}/", response=OrganizationSchema)
def get_organization_details_by_slug(request, organization_slug: str):
    """
    Get details for a specific Organization by slug.
    By default, returns details for active, publicly available ones.
    Else, returns the details of the organization if the user is a member.

    The happy path is that the organization exists and the user is a member of it, so search for that first.
    Then search for the organization and if it is active and publicly visible.
    """

    try:
        return Organization.objects.get(
            slug=organization_slug, is_active=True, member__user=request.user
        )
    except Organization.DoesNotExist:
        try:
            return Organization.objects.get(
                slug=organization_slug, is_active=True, publicly_visible=True
            )
        except Organization.DoesNotExist:
            raise Http404(f"Organization not found for slug: {organization_slug}")


@router.post("/", response=OrganizationSchema)
def create_organization(
    request,
    payload: CreateUpdateOrganizationSchema,
):
    """
    Create a new Organization. Any authorized user can do so.
    """
    organization = Organization.objects.create(
        **payload.dict(), created_by=request.user
    )
    return organization


@router.patch("/{organization_slug}/", response=OrganizationSchema)
def update_organization_details(
    request, organization_slug: str, payload: CreateUpdateOrganizationSchema
):
    """
    Update an Organization if user is an owner.
    """

    try:
        organization = Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
            member__role=Member.MemberRole.OWNER,
        )
        for key, value in payload.dict().items():
            setattr(organization, key, value)
        organization.save()
        return organization
    except Organization.DoesNotExist:
        return HttpResponseForbidden(
            "You can only update organizations you are the owner of"
        )


@router.delete("/{organization_slug}/", response=bool)
def delete_organization(request, organization_slug: str):
    """
    Delete an Organization if user is an owner.
    """

    try:
        Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
            member__role=Member.MemberRole.OWNER,
        ).delete()
        return True
    except Organization.DoesNotExist:
        return HttpResponseForbidden(
            "You can only delete organizations you are the owner of"
        )


@router.get("/{organization_slug}/members/", response=List[MemberSchema])
@paginate
def list_organization_members(request, organization_slug: str):
    """
    List members of an Organization.
    If the user is an owner or a superuser return all members.
    Else, return only publicly visible members.
    """
    try:
        request_user = request.user if request.user.is_authenticated else None
        # we found an organization the user is a member of
        organization = Organization.objects.get(
            slug=organization_slug, is_active=True, member__user=request_user
        )
        # if the user is a superuser or an owner of the organization return all members
        if (
            request_user.is_superuser
            or organization.member_set.filter(
                user=request_user, role=Member.MemberRole.OWNER
            ).exists()
        ):
            return organization.member_set.filter()
        else:
            # else return only publicly visible members
            return organization.member_set.filter(publicly_visible=True)
    except Organization.DoesNotExist:
        try:
            # if the organization is active and publicly visible, return only publicly visible members
            organization = Organization.objects.get(
                slug=organization_slug, is_active=True, publicly_visible=True
            )
            return organization.member_set.filter(publicly_visible=True)
        except Organization.DoesNotExist:
            raise Http404(f"Organization not found for slug: {organization_slug}")


@router.post("/{organization_slug}/members/", response=MemberSchema)
def add_member_to_organization(
    request, organization_slug: str, payload: AddMemberSchema
):
    request_user = request.user
    organization = Organization.objects.get(slug=organization_slug, is_active=True)
    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
    ):
        raise Exception(
            "You can only add members to an organization you are the owner of"
        )
    return organization.add_user_to_organization(
        username=payload.username, role=payload.role
    )


@router.patch("/{organization_slug}/members/{member_username}", response=MemberSchema)
def update_member_in_organization(
    request, organization_slug: str, member_username: str, payload: UpdateMemberSchema
):
    request_user = request.user
    organization = Organization.objects.get(slug=organization_slug, is_active=True)
    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
    ):
        raise Exception(
            "You can only updates members in this organization if you are an owner"
        )
    member = organization.member_set.get(user__username=member_username)
    for key, value in payload.dict().items():
        setattr(member, key, value)
    member.save()
    return member


@router.delete("/{organization_slug}/members/{member_username}", response=bool)
def remove_member_from_organization(
    request, organization_slug: str, member_username: str
):
    request_user = request.user
    organization = Organization.objects.get(slug=organization_slug, is_active=True)
    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
    ):
        raise Exception(
            "You can only add members to an organization you are the owner of"
        )
    return organization.remove_user_from_organization(username=member_username)


@router.get("/{organization_slug}/teams/", response=List[TeamSchema])
@paginate
def list_teams(request, organization_slug: str):
    """
    List all Teams in an Organization a user can see.
    This includes all publicly visible, active ones and any the user is a member of.
    """
    request_user = request.user
    organization = Organization.objects.get(
        slug=organization_slug,
        is_active=True,
        member__user=request.user,
    )
    # if the user is a super user or owner of the organization, return all teams
    if request_user.is_superuser or organization.member_set.get(
        user=request_user, role=Member.MemberRole.OWNER
    ):
        return organization.team_set.filter(is_active=True)
    # else return all publicly visible teams and any the user is a member of
    return organization.team_set.filter(
        is_active=True, visible_to_organization=True
    ).union(organization.team_set.filter(is_active=True, members__user=request_user))


@router.get("/{organization_slug}/teams/{team_slug}", response=TeamSchema)
def team_details(request, organization_slug: str, team_slug: str):
    request_user = request.user
    organization = Organization.objects.get(
        slug=organization_slug,
        is_active=True,
        member__user=request.user,
    )
    if request_user.is_superuser or organization.member_set.get(
        user=request_user, role=Member.MemberRole.OWNER
    ):
        return organization.team_set.get(is_active=True, slug=team_slug)
    else:
        return organization.team_set.get(
            is_active=True,
            visible_to_organization=True,
            slug=team_slug,
        )


@router.post("/{organization_slug}/teams/", response=TeamSchema)
def create_team(request, organization_slug: str, payload: CreateUpdateTeamSchema):
    request_user = request.user
    organization = Organization.objects.get(
        slug=organization_slug,
        is_active=True,
        member__user=request.user,
        member__role=Member.MemberRole.OWNER,
    )
    team = Team.objects.create(
        organization=organization,
        created_by=request_user,
        **payload.dict(),
    )
    return team


@router.delete("/{organization_slug}/teams/{team_slug}", response=TeamSchema)
def delete_team(request, organization_slug: str, team_slug: str):
    request_user = request.user
    team = Team.objects.get(organization_slug=organization_slug, slug=team_slug)
    if not team.member_set.filter(
        user=request_user, role=TeamMember.TeamMemberRole.OWNER
    ).exists():
        raise Exception("You can only delete teams you are the owner of")
    team.delete()
    return team


@router.patch("/{organization_slug}/teams/{team_slug}", response=TeamSchema)
def update_team(
    request, organization_slug: str, team_slug: str, payload: CreateUpdateTeamSchema
):
    request_user = request.user
    try:
        organization = Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
        )
    except Organization.DoesNotExist:
        raise Http404("Organization does not exist")

    try:
        team = organization.team_set.get(is_active=True, slug=team_slug)
    except Team.DoesNotExist:
        raise Http404("Team does not exist for this organization")

    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
        or team.member_set.get(user=request_user, role=TeamMember.TeamMemberRole.OWNER)
    ):
        raise Exception("You can only update teams you are the owner of")

    for key, value in payload.dict().items():
        setattr(team, key, value)
    team.save()
    return team


@router.get(
    "/{organization_slug}/teams/{team_slug}/members/", response=List[TeamMemberSchema]
)
@paginate
def list_team_members(request, organization_slug: str, team_slug: str):
    request_user = request.user
    try:
        organization = Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
        )
    except Organization.DoesNotExist:
        raise Http404("Organization does not exist")

    try:
        team = organization.team_set.get(is_active=True, slug=team_slug)
    except Team.DoesNotExist:
        raise Http404("Team does not exist for this organization")

    if not (
        request_user.is_superuser
        or organization.teammember_set.get(
            user=request_user, role=Member.MemberRole.OWNER
        )
        or team.teammember_set.get(user=request_user)
        or team.visible_to_organization
    ):
        raise Exception("You can only list members of teams you have access too")
    print(team.teammember_set.all()[0].member)
    return team.teammember_set.all()


@router.post(
    "/{organization_slug}/teams/{team_slug}/members/", response=TeamMemberSchema
)
def add_member_to_team(
    request, organization_slug: str, team_slug: str, payload: AddTeamMemberSchema
):
    request_user = request.user
    try:
        organization = Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
        )
    except Organization.DoesNotExist:
        raise Http404("Organization does not exist")

    try:
        team = organization.team_set.get(is_active=True, slug=team_slug)
    except Team.DoesNotExist:
        raise Http404("Team does not exist for this organization")

    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
        or team.member_set.get(user=request_user, role=TeamMember.TeamMemberRole.OWNER)
    ):
        raise Exception("You can only add members to a team you are the owner of")

    return team.add_user_to_team(username=payload.username, role=payload.role)


@router.delete(
    "/{organization_slug}/teams/{team_slug}/members/{username}",
    response=bool,
)
def remove_member_from_team(
    request, organization_slug: str, team_slug: str, username: str
):
    request_user = request.user
    try:
        organization = Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
        )
    except Organization.DoesNotExist:
        raise Http404("Organization does not exist")

    try:
        team = organization.team_set.get(is_active=True, slug=team_slug)
    except Team.DoesNotExist:
        raise Http404("Team does not exist for this organization")

    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
        or team.member_set.get(user=request_user, role=TeamMember.TeamMemberRole.OWNER)
    ):
        raise Exception("You can only remove members from a team you are the owner of")
    return team.remove_user_from_team(username=username)


@router.patch(
    "/{organization_slug}/teams/{team_slug}/members/{username}",
    response=TeamMemberSchema,
)
def update_member_in_team(
    request,
    organization_slug: str,
    team_slug: str,
    username: str,
    payload: UpdateTeamMemberSchema,
):
    request_user = request.user
    try:
        organization = Organization.objects.get(
            slug=organization_slug,
            is_active=True,
            member__user=request.user,
        )
    except Organization.DoesNotExist:
        raise Http404("Organization does not exist")

    try:
        team = organization.team_set.get(is_active=True, slug=team_slug)
    except Team.DoesNotExist:
        raise Http404("Team does not exist for this organization")

    if not (
        request_user.is_superuser
        or organization.member_set.get(user=request_user, role=Member.MemberRole.OWNER)
        or team.teammember_set.get(
            user=request_user, role=TeamMember.TeamMemberRole.OWNER
        )
    ):
        raise Exception("You can only update members from a team you are the owner of")

    member = team.teammember_set.get(member__user__username=username)
    for key, value in payload.dict().items():
        setattr(member, key, value)
    member.save()
    return member
