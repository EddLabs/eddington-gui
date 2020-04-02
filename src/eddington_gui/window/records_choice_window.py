from typing import List, Callable
import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LINE_HEIGHT, SMALL_PADDING


class RecordsChoiceWindow(toga.Window):

    __save_action: Callable
    __checkboxes: List[toga.Switch]

    def __init__(self, data_dict, initial_chosen_records, save_action):
        super(RecordsChoiceWindow, self).__init__()
        self.__save_action = save_action
        main_box = toga.Box(style=Pack(direction=COLUMN))
        data_box = toga.Box()
        self.__checkboxes = [
            toga.Switch(label="", is_on=chosen, style=Pack(height=LINE_HEIGHT,),)
            for chosen in initial_chosen_records
        ]
        data_box.add(
            toga.Box(
                style=Pack(
                    flex=1,
                    direction=COLUMN,
                    padding_left=SMALL_PADDING,
                    padding_right=SMALL_PADDING,
                ),
                children=[toga.Label(text="Chosen", style=Pack(height=LINE_HEIGHT))]
                + self.__checkboxes,
            )
        )
        for header, column in data_dict.items():
            data_box.add(
                toga.Box(
                    style=Pack(
                        flex=1,
                        direction=COLUMN,
                        padding_left=SMALL_PADDING,
                        padding_right=SMALL_PADDING,
                    ),
                    children=[toga.Label(text=header, style=Pack(height=LINE_HEIGHT))]
                    + [
                        toga.Label(text=element, style=Pack(height=LINE_HEIGHT))
                        for element in column
                    ],
                )
            )
        main_box.add(data_box)
        main_box.add(LineBox(children=[toga.Button(label="Save", on_press=self.save)],))
        self.content = main_box

    def save(self, widget):
        self.__save_action([checkbox.is_on for checkbox in self.__checkboxes])
        self.close()
