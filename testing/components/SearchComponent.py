import rio
from difflib import SequenceMatcher
import json
import os

class SearchComponent(rio.Component):
    query: str = ""
    result: dict | None = None
    error: str | None = None
    suggestions: list = []

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def is_free(self, app):
        try:
            with open(os.path.join(os.path.dirname(__file__), '../../data/licenses.json'), 'r') as data:
                all_licenses = json.load(data)["licenses"]
                for al in all_licenses:
                    for l in app.get("licenses", []):
                        if l in [al.get("licenseId", ""), al.get("name", "")] and al.get("isFsfLibre", False):
                            return True
        except Exception as e:
            print("License Error!", e)
        return False

    def search_app(self, name):
        closest = {}
        match = 0
        apps_path = os.path.join(os.path.dirname(__file__), '../../apps')

        all_apps = []
        for i in os.listdir(apps_path):
            if i.endswith(".json"):
                try:
                    with open(os.path.join(apps_path, i)) as json_file:
                        idata = json.load(json_file)
                except Exception as e:
                    print("Error!", i, e)
                    idata = {}

                all_apps.append(idata)

        # Round 1: By the name
        for i in all_apps:
            for n in i.get("names", []):
                m = self.similar(n.lower(), name.lower())
                if m > match and m > 0.6:
                    closest = i
                    match = m

        if closest:
            return closest, match

        match = 0
        closest = {}

        # Round 2: By Generic name
        for i in all_apps:
            for n in i.get("generic_name", []):
                m = self.similar(n.lower(), name.lower())
                if m > match and self.is_free(i):
                    closest = i
                    match = m

        return closest if match > 0.6 else None, None

    def suggest(self, json_data):
        found = []
        apps_path = os.path.join(os.path.dirname(__file__), '../../apps')

        all_apps = []
        for i in os.listdir(apps_path):
            if i.endswith(".json"):
                try:
                    with open(os.path.join(apps_path, i)) as json_file:
                        idata = json.load(json_file)
                except Exception as e:
                    print("Error!", i, e)
                    idata = {}

                all_apps.append(idata)

        for i in all_apps:
            if i["names"][0] == json_data["names"][0]:
                continue  # Skip the main app from suggestions

            score = 0
            for c in ["generic_name", "networks_read", "networks_write", "formats_read", "formats_write"]:
                for b in json_data.get(c, []):
                    if b in i.get(c, []):
                        score += 10 if c == "generic_name" else 1
                        try:
                            i[c][i[c].index(b)] = "*" + b
                        except Exception as e:
                            print(e)

            if "issues" in i and score:
                score = max(0.1, score - len(i["issues"]))

            if score >= 10:  # Only include suggestions with score 10 or higher
                found.append([score, i])

        try:
            found.sort(key=lambda x: x[0], reverse=True)
        except Exception as e:
            print("Found problem:", e)
            found = []

        return found

    async def on_search(self):
        self.error = None
        self.result, match = self.search_app(self.query)
        if not self.result:
            self.error = "No matching app found."
        else:
            self.suggestions = self.suggest(self.result)

    def build(self):
        logo_url = "https://notabug.org/jyamihud/FreeCompetitors/raw/master/favicon.png"

        header = rio.Row(
            rio.Image(image=rio.URL(logo_url), width=5, height=5, fill_mode='fit', margin_right=1),
            rio.Text("FreeCompetitors 2.0", style="heading1"),
            align_x=0.5,
            spacing=1,
            margin_bottom=2
        )

        children = [
            header,
            rio.TextInput(
                text=self.bind().query,
                on_change=self.handle_input_change,
                width="grow"
            ),
            rio.Button("Search", on_press=self.on_search),
        ]

        if self.error:
            children.append(rio.Text(self.error, style="text", wrap=True))
        if self.result:
            result_text = f"Found app: {self.result['names'][0]}"
            children.append(rio.Text(result_text, style="text", wrap=True))
            if self.suggestions:
                children.append(rio.Text("Recommended Open-Source Alternatives:", style="heading2", wrap=True))
                suggestion_boxes = [self.render_suggestion(suggestion, score) for score, suggestion in self.suggestions]
                children.append(rio.Column(*suggestion_boxes, spacing=2))

        return rio.Column(
            *children,
            spacing=2,
            margin=2,
            width="grow",
            align_y=0.5
        )

    def handle_input_change(self, event):
        self.query = event.text

    def render_suggestion(self, suggestion, score):
        children = [
            rio.Text(f"{suggestion['names'][0]} (Score: {score})", style="heading3", wrap=True),
            rio.Text(f"Comment: {suggestion.get('comment', 'No description available.')}", style="text", wrap=True),
            rio.Text(f"Features: {', '.join(suggestion.get('generic_name', []))}", style="text", wrap=True),
            rio.Text(f"Licenses: {', '.join(suggestion.get('licenses', []))}", style="text", wrap=True),
            rio.Text(f"Platforms: {', '.join(suggestion.get('platforms', []))}", style="text", wrap=True),
            rio.Text(f"Formats Read: {', '.join(suggestion.get('formats_read', []))}", style="text", wrap=True),
            rio.Text(f"Formats Write: {', '.join(suggestion.get('formats_write', []))}", style="text", wrap=True),
            rio.Text(f"Interfaces: {', '.join(suggestion.get('interface', []))}", style="text", wrap=True),
            rio.Text(f"Programming Languages: {', '.join(suggestion.get('languages', []))}", style="text", wrap=True),
        ]
        links = suggestion.get('links', {})
        link_buttons = [self.render_link_button(link_name.upper(), link_url) for link_name, link_url in links.items() if link_name != 'icon']
        if link_buttons:
            children.append(rio.Row(*link_buttons, align_x=0.5, spacing=1))

        logo = suggestion.get('links', {}).get('icon', None)
        if logo:
            children.insert(0, rio.Image(image=rio.URL(logo), width=5, height=5, fill_mode='fit', margin_bottom=1))

        return rio.Card(
            content=rio.Column(*children, spacing=1, margin=1, width='grow'),
            margin=2,
            corner_radius=8,
            elevate_on_hover=True,
            color="neutral",
            width=30,
            height='natural'
        )

    def render_link_button(self, text, url):
        return rio.Link(
            content=rio.Button(
                content=text,
                style="major",
                color="primary",
                width="grow",
                margin_right=1  # Add margin_right for spacing between buttons
            ),
            target_url=url,
            open_in_new_tab=True
        )

if __name__ == "__main__":
    app = rio.App()
    app.run(page=SearchComponent())