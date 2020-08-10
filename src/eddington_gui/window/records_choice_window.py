from typing import List, Callable
import toga
from eddington import FitData
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LINE_HEIGHT, SMALL_PADDING, RECORD_WINDOW_SIZE


class RecordsChoiceWindow(toga.Window):

    __save_action: Callable
    __checkboxes: List[toga.Switch]

    def __init__(self, fit_data: FitData):
        super(RecordsChoiceWindow, self).__init__(size=RECORD_WINDOW_SIZE)
        main_box = toga.Box(style=Pack(direction=COLUMN))
        data_box = toga.Box()
        self.__checkboxes = [
            toga.Switch(
                label="",
                is_on=fit_data.is_selected(i),
                style=Pack(height=LINE_HEIGHT,),
            )
            for i in range(1, fit_data.length + 1)
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
                + self.__checkboxes,  # noqa: W503
            )
        )
        for header, column in fit_data.data.items():
            data_box.add(
                toga.Box(
                    style=Pack(
                        flex=1,
                        direction=COLUMN,
                        padding_left=SMALL_PADDING,
                        padding_right=SMALL_PADDING,
                    ),
                    children=[toga.Label(text=header, style=Pack(height=LINE_HEIGHT))]
                    + [  # noqa: W503
                        toga.Label(text=element, style=Pack(height=LINE_HEIGHT))
                        for element in column
                    ],
                )
            )
        main_box.add(data_box)
        main_box.add(
            LineBox(
                children=[
                    toga.Button(label="Save", on_press=self.save_action(fit_data))
                ],
            )
        )
        scroller = toga.ScrollContainer(content=main_box)
        self.content = scroller

    def save_action(self, fit_data: FitData):
        def save(widget):
            for i in range(fit_data.length):
                if self.__checkboxes[i].is_on:
                    fit_data.select_record(i + 1)
                else:
                    fit_data.unselect_record(i + 1)
            self.close()

        return save
