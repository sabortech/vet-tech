import unittest

from vet_tech.components.sidebar import _EXISTING_ROUTES, _NAV_ITEMS, _menu_item
from vet_tech.features.navigation.state import NavigationState


def make_state():
    state = NavigationState(_reflex_internal_init=True)
    state.sidebar_preference = "true"
    state.drawer_open = False
    return state


class NavigationStateTests(unittest.TestCase):
    def test_desktop_sidebar_starts_expanded_and_toggles_preference(self):
        state = make_state()

        self.assertTrue(state.sidebar_expanded)

        NavigationState.toggle_sidebar.fn(state)
        self.assertFalse(state.sidebar_expanded)
        self.assertEqual(state.sidebar_preference, "false")

        NavigationState.toggle_sidebar.fn(state)
        self.assertTrue(state.sidebar_expanded)
        self.assertEqual(state.sidebar_preference, "true")

    def test_mobile_drawer_starts_closed_and_can_be_closed(self):
        state = make_state()

        self.assertFalse(state.drawer_open)

        NavigationState.toggle_drawer.fn(state)
        self.assertTrue(state.drawer_open)

        NavigationState.close_drawer.fn(state)
        self.assertFalse(state.drawer_open)

    def test_unimplemented_navigation_items_have_no_route(self):
        route_ids = set(_EXISTING_ROUTES)
        self.assertEqual(route_ids, {"meus_pets", "configuracoes"})
        self.assertEqual(_EXISTING_ROUTES["meus_pets"], "/")

        for item_id, label, icon_name in _NAV_ITEMS:
            with self.subTest(item_id=item_id):
                item = _menu_item(item_id, label, icon_name, "meus_pets")
                self.assertEqual(
                    type(item).__name__,
                    "Link" if item_id in route_ids else "Box",
                )


if __name__ == "__main__":
    unittest.main()
