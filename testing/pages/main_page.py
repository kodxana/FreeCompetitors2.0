import rio
from testing.components.SearchComponent import SearchComponent

class MainPage(rio.Component):
    def build(self):
        return SearchComponent()

if __name__ == "__main__":
    app = rio.App()
    app.run(page=MainPage())