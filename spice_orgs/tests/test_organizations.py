from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Organization

UserModel = get_user_model()


class OrganizationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_1 = UserModel.objects.create(username="user_1")
        cls.user_1.set_password("password")
        cls.user_1.save()

        cls.user_2 = UserModel.objects.create(username="user_2")
        cls.user_2.set_password("password")
        cls.user_2.save()

    def _create_organization_via_api(self, name="First Org", publicly_visible=True):
        self.client.login(username=self.user_1.get_username(), password="password")
        response = self.client.post(
            path="/api/organizations/",
            data={"name": name, "publicly_visible": publicly_visible},
            content_type="application/json",
        )
        return response

    def _create_organization_via_orm(self, name="First Org", publicly_visible=True):
        return Organization.objects.create(
            name=name, publicly_visible=publicly_visible, created_by=self.user_1
        )

    def _get_organization_by_slug(self, organization_slug):
        return Organization.objects.get(slug=organization_slug)


class ListOrganizationTest(OrganizationTestCase):
    def test_list_public_organizations_no_auth(self):
        organization = self._create_organization_via_orm()
        response = self.client.get(
            path="/api/organizations/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "items": [
                    {
                        "name": organization.name,
                        "slug": organization.slug,
                        "publicly_visible": organization.publicly_visible,
                    }
                ],
                "count": 1,
            },
        )

    def test_list_private_organizations_no_auth(self):
        organization = self._create_organization_via_orm()
        organization.publicly_visible = False
        organization.save()
        response = self.client.get(
            path="/api/organizations/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                "items": [],
                "count": 0,
            },
        )

    def test_list_public_inactive_organizations_no_auth(self):
        organization = self._create_organization_via_orm()
        organization.is_active = False
        organization.save()
        response = self.client.get(
            path="/api/organizations/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                "items": [],
                "count": 0,
            },
        )

    def test_list_organizations_auth(self):
        self.client.login(username=self.user_1.get_username(), password="password")
        organization_1 = self._create_organization_via_orm()
        organization_2 = self._create_organization_via_orm(name="Second Org")
        organization_2.publicly_visible = False
        organization_2.save()

        response = self.client.get(
            path="/api/organizations/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "items": [
                    {
                        "name": organization_1.name,
                        "slug": organization_1.slug,
                        "publicly_visible": organization_1.publicly_visible,
                    },
                    {
                        "name": organization_2.name,
                        "slug": organization_2.slug,
                        "publicly_visible": organization_2.publicly_visible,
                    },
                ],
                "count": 2,
            },
        )
        # verify other users who are not in the organization can only see the public organization
        self.client.logout()
        self.client.login(username=self.user_2.get_username(), password="password")
        response = self.client.get(
            path="/api/organizations/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "items": [
                    {
                        "name": organization_1.name,
                        "slug": organization_1.slug,
                        "publicly_visible": organization_1.publicly_visible,
                    }
                ],
                "count": 1,
            },
        )


# class CreateOrganizationTest(OrganizationTestCase):
# def test_create_organization(self) -> None:
#     response = self.create_organization_via_api()
#     self.assertEqual(response.status_code, 200)
#     organization = Organization.objects.get(id=response.json()["id"])
#     self.assertDictEqual(
#         response.json(),
#         {
#             "id": str(organization.id),
#             "name": "First Org",
#             "slug": "first-org",
#         },
#     )
#     self.client.logout()
#     organization.delete()

# def test_create_organization_anonymous_user(self) -> None:
#     response = self.client.get(
#         path="/api/organizations/",
#     )
#     self.assertEqual(response.status_code, 200)
#     self.assertDictEqual(
#         response.json(),
#         {
#             "items": [
#                 {
#                     "id": str(organization.id),
#                     "name": "First Org",
#                     "slug": "first-org",
#                 }
#             ],
#             "count": 1,
#         },
#     )

#     # verify other users who are not in the organization can see the public organization
#     self.client.login(username=self.user_2.get_username(), password="password")
#     self.assertEqual(response.status_code, 200)
#     self.assertDictEqual(
#         response.json(),
#         {
#             "items": [
#                 {
#                     "id": str(organization.id),
#                     "name": "First Org",
#                     "slug": "first-org",
#                 }
#             ],
#             "count": 1,
#         },
#     )
#     self.client.logout()

#     # create a organization private organization. verify users that are not members cannot see it but can see other public organizations
#     self.client.login(username=self.user_1.get_username(), password="password")
#     response = self.client.post(
#         path="/api/organizations/",
#         data={"name": "Private Org", "publicly_visible": False},
#         content_type="application/json",
#     )
#     self.assertEqual(response.status_code, 200)
#     private_organization = Organization.objects.get(name="Private Org")
#     response = self.client.get(
#         path="/api/organizations/",
#     )
#     self.assertDictEqual(
#         response.json(),
#         {
#             "items": [
#                 {
#                     "id": str(organization.id),
#                     "name": "First Org",
#                     "slug": "first-org",
#                 },
#                 {
#                     "id": str(private_organization.id),
#                     "name": "Private Org",
#                     "slug": "private-org",
#                 },
#             ],
#             "count": 2,
#         },
#     )
#     self.client.logout()

#     response = self.client.get(
#         path="/api/organizations/",
#     )
#     self.assertDictEqual(
#         response.json(),
#         {
#             "items": [
#                 {
#                     "id": str(organization.id),
#                     "name": "First Org",
#                     "slug": "first-org",
#                 },
#             ],
#             "count": 1,
#         },
#     )
#     self.client.logout()

#     # delete the organization
#     organization.delete()
