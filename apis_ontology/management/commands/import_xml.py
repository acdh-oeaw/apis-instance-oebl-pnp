import xml.etree.ElementTree as ET
import pathlib
from django.core.management.base import BaseCommand

ns = {'b': 'http://www.biographien.ac.at'}


def get_info(root, file):
    number = root.attrib.get("Nummer")
    name = root.find("./b:Lexikonartikel/b:Schlagwort/b:Hauptbezeichnung", ns).text
    if not number:
        print(f"No `Nummer` in {file}")
        return


class Command(BaseCommand):
    help = "Import data from legacy xml files"

    def add_arguments(self, parser):
        # point to XML_RESOLVE_IN_PROGRESS folder
        parser.add_argument("--folder", type=pathlib.Path)
        parser.add_argument("--file", type=pathlib.Path)

    def handle(self, *args, **options):
        if options["folder"]:
            subfolders = ["Print_Only_Resolved", "Print_UND_Online_Resolved"]
            for subfolder in subfolders:
                folder = options["folder"] / subfolder
                for file in folder.glob('**/*.xml'):
                    get_info(ET.parse(file).getroot(), file)
        if file := options["file"]:
            get_info(ET.parse(file).getroot(), file)
